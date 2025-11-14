"""
@purpose: LoRA 训练脚本，使用 Hugging Face Transformers 和 PEFT 进行 LoRA 微调
@author: DanielChung
@createdAt: 2025-11-12
@lastModified: 2025-11-12
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import structlog
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset, Dataset

logger = structlog.get_logger(__name__)


class LoRATrainer:
    """LoRA 训练器，用于训练 EB-mM LoRA 适配器"""

    def __init__(
        self,
        base_model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        output_dir: str = "./models/eb-mm-lora-v1",
        lora_rank: int = 8,
        lora_alpha: int = 16,
        lora_target_modules: Optional[List[str]] = None,
        lora_dropout: float = 0.1,
    ):
        """
        初始化 LoRA 训练器

        Args:
            base_model_name: 基础模型名称
            output_dir: 输出目录
            lora_rank: LoRA rank 参数
            lora_alpha: LoRA alpha 参数
            lora_target_modules: LoRA target modules 列表
            lora_dropout: LoRA dropout 参数
        """
        self.base_model_name = base_model_name
        self.output_dir = Path(output_dir)
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.lora_target_modules = lora_target_modules or ["q_proj", "v_proj"]
        self.lora_dropout = lora_dropout

        self.model = None
        self.tokenizer = None
        self.peft_model = None

        logger.info(
            "初始化 LoRA 训练器",
            base_model_name=base_model_name,
            output_dir=str(output_dir),
            lora_rank=lora_rank,
            lora_alpha=lora_alpha,
        )

    def load_base_model(self, use_quantization: bool = False):
        """
        加载基础模型

        Args:
            use_quantization: 是否使用量化（bitsandbytes）
        """
        logger.info("加载基础模型", model_name=self.base_model_name)

        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if use_quantization:
            from transformers import BitsAndBytesConfig

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype="float16",
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                quantization_config=quantization_config,
                device_map="auto",
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                device_map="auto",
            )

        logger.info("基础模型加载完成")

    def configure_lora(self):
        """配置 LoRA 参数"""
        logger.info("配置 LoRA 参数", target_modules=self.lora_target_modules)

        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=self.lora_rank,
            lora_alpha=self.lora_alpha,
            target_modules=self.lora_target_modules,
            lora_dropout=self.lora_dropout,
            bias="none",
        )

        self.peft_model = get_peft_model(self.model, lora_config)
        self.peft_model.print_trainable_parameters()

        logger.info("LoRA 配置完成")

    def load_training_data(self, data_file: str) -> Dataset:
        """
        加载训练数据

        Args:
            data_file: JSONL 数据文件路径

        Returns:
            训练数据集
        """
        logger.info("加载训练数据", data_file=data_file)

        dataset = load_dataset("json", data_files=data_file, split="train")

        def preprocess_function(examples):
            """预处理函数"""
            inputs = []
            targets = []

            for instruction, input_text, output_text in zip(
                examples["instruction"], examples["input"], examples["output"]
            ):
                prompt = f"{instruction}\n\n输入：{input_text}\n\n输出："
                inputs.append(prompt)
                targets.append(output_text)

            # Tokenize
            model_inputs = self.tokenizer(
                inputs,
                max_length=512,
                truncation=True,
                padding="max_length",
            )

            labels = self.tokenizer(
                targets,
                max_length=256,
                truncation=True,
                padding="max_length",
            )

            model_inputs["labels"] = labels["input_ids"]
            return model_inputs

        processed_dataset = dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=dataset.column_names,
        )

        logger.info("训练数据加载完成", num_samples=len(processed_dataset))

        return processed_dataset

    def train(
        self,
        train_dataset: "Dataset",
        eval_dataset: Optional["Dataset"] = None,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
    ) -> Dict:
        """
        执行训练

        Args:
            train_dataset: 训练数据集
            eval_dataset: 验证数据集（可选）
            num_epochs: 训练轮数
            batch_size: 批次大小
            learning_rate: 学习率
            warmup_steps: 预热步数

        Returns:
            训练结果字典
        """
        logger.info("开始训练", num_epochs=num_epochs, batch_size=batch_size)

        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            logging_steps=10,
            save_steps=500,
            evaluation_strategy="steps" if eval_dataset else "no",
            eval_steps=500 if eval_dataset else None,
            save_total_limit=3,
            load_best_model_at_end=True if eval_dataset else False,
            metric_for_best_model="eval_loss" if eval_dataset else None,
            fp16=True,
            report_to="none",
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False
        )

        trainer = Trainer(
            model=self.peft_model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )

        train_result = trainer.train()

        logger.info("训练完成", train_loss=train_result.training_loss)

        return {
            "train_loss": train_result.training_loss,
            "train_runtime": train_result.metrics.get("train_runtime", 0),
        }

    def save_adapter(self, version: str, metadata: Optional[Dict] = None):
        """
        保存 LoRA 适配器

        Args:
            version: 版本号
            metadata: 训练元数据
        """
        adapter_dir = self.output_dir / f"eb-mm-lora-{version}"
        adapter_dir.mkdir(parents=True, exist_ok=True)

        logger.info("保存 LoRA 适配器", adapter_dir=str(adapter_dir))

        # 保存适配器
        self.peft_model.save_pretrained(str(adapter_dir))

        # 保存元数据
        if metadata:
            metadata_file = adapter_dir / "training_metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info("LoRA 适配器保存完成", adapter_dir=str(adapter_dir))

