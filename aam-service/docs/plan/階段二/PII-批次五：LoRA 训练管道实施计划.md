# 批次五：LoRA 训练管道实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 已完成  
**基准文档**: `AAM Phase II.md`  
**前置条件**: Phase I 已完成（需要 ChromaDB 中有数据）、批次一（降级策略框架）已完成、批次二（抽象模型服务层）已完成  
**最后更新**: 2025-11-12

---

## 批次概述

### 目标

实现 LoRA 训练管道，基于 DeepSeek-R1 8B 训练 EB-mM (Enterprise Bot mini-Model) LoRA 适配器。通过定期从 ChromaDB 和 PostgreSQL 导出高质量对话数据，格式化为 Instruction JSONL 格式，使用 PEFT 进行 LoRA 微调，实现模型版本管理和动态更新。

### 核心任务

1. **数据导出器** - 从 ChromaDB 和 PostgreSQL 导出训练数据，清洗和格式化
2. **LoRA 训练脚本** - 使用 Hugging Face Transformers 和 PEFT 进行 LoRA 微调
3. **模型版本管理** - 实现模型版本化、存储和加载接口
4. **训练配置管理** - 扩展配置系统支持训练参数
5. **训练任务调度** - 实现定期训练任务（可选，使用 CronJob 或 Celery）
6. **单元测试和集成测试** - 创建完整的测试套件

### 设计理念

**离线训练管道**：
- 训练管道独立于主服务运行，不阻塞生产环境
- 定期（如每周）从数据库导出高质量数据
- 使用 LoRA 技术实现参数高效微调（仅训练适配器，不修改基础模型）
- 支持模型版本管理，可以回滚到之前的版本
- 训练完成后，通过配置更新使用新的 LoRA 适配器

---

## 任务清单

### Task 5.1: 创建训练目录结构

**文件**: `src/training/` (新建目录)

**任务**:
- [ ] 创建 `src/training/` 目录
- [ ] 创建 `src/training/__init__.py` 文件
- [ ] 创建 `src/training/data_exporter.py` 文件
- [ ] 创建 `src/training/train_lora.py` 文件
- [ ] 创建 `src/training/model_repository.py` 文件
- [ ] 创建 `src/training/utils.py` 文件（可选，用于工具函数）
- [ ] 添加标准头部注释到所有文件

**验收标准**:
- [ ] 目录结构正确
- [ ] 所有文件包含标准头部注释
- [ ] 符合 AiDevelopmentGuide.md 规范

---

### Task 5.2: 实现数据导出器

**文件**: `src/training/data_exporter.py` (新建)

**任务**:
- [ ] 创建 `DataExporter` 类
- [ ] 实现连接 ChromaDB 的方法
  - [ ] 使用 `ChromaKnowledgeStore` 或直接连接 ChromaDB
  - [ ] 查询过去 N 天的对话数据（通过 timestamp 过滤）
  - [ ] 过滤高质量数据（基于质量评估分数，如果有）
- [ ] 实现连接 PostgreSQL 的方法（可选，如果需要用户画像数据）
  - [ ] 查询用户画像数据（如果需要）
- [ ] 实现数据清洗和过滤逻辑
  - [ ] 过滤空文本或无效数据
  - [ ] 保留包含实体或三元组的数据（高质量数据）
  - [ ] 可选：基于质量评估分数过滤
- [ ] 实现格式化为 Instruction JSONL 格式
  - [ ] 针对 NER 任务的格式：`{"instruction": "...", "input": "...", "output": "..."}`
  - [ ] 针对 KE 任务的格式
  - [ ] 针对 KT 任务的格式
  - [ ] 针对个性分析的格式（可选）
- [ ] 实现保存为 JSONL 文件的方法
- [ ] 实现数据统计和日志记录
- [ ] 添加错误处理和重试机制

**数据格式示例**:
```json
{
  "instruction": "请从以下文本中提取命名实体（人名、地名、组织名、产品名等）。",
  "input": "我想了解订单 #12345 的状态，请联系销售部门的张三。",
  "output": "{\"entities\": [\"订单 #12345\", \"销售部门\", \"张三\"], \"entity_types\": {\"订单 #12345\": \"Product\", \"销售部门\": \"Organization\", \"张三\": \"Person\"}}"
}
```

**验收标准**:
- [ ] 数据导出正确，能够从 ChromaDB 查询数据
- [ ] 数据质量过滤逻辑正确
- [ ] JSONL 格式符合训练要求
- [ ] 支持配置导出天数、质量阈值等参数
- [ ] 错误处理完善
- [ ] 日志记录详细
- [ ] 包含单元测试（覆盖率 > 80%）

**参考代码**:
- `src/infrastructure/database/chroma_knowledge_store.py` - ChromaDB 连接参考
- `src/models/domain/database.py` - `KnowledgeAsset` 模型参考

---

### Task 5.3: 实现 LoRA 训练脚本

**文件**: `src/training/train_lora.py` (新建)

**任务**:
- [ ] 创建 `LoRATrainer` 类
- [ ] 实现加载基础模型的方法
  - [ ] 使用 Hugging Face Transformers 加载 DeepSeek-R1 8B
  - [ ] 支持从本地或 Hugging Face Hub 加载
  - [ ] 实现模型量化（可选，使用 bitsandbytes）
- [ ] 实现配置 PEFT LoRA 参数
  - [ ] `r` (rank): 默认 8，支持配置
  - [ ] `lora_alpha`: 默认 16（r * 2），支持配置
  - [ ] `target_modules`: 默认 `["q_proj", "v_proj"]`，支持配置
  - [ ] `lora_dropout`: 默认 0.1，支持配置
  - [ ] `bias`: 默认 "none"，支持配置
- [ ] 实现加载训练数据的方法
  - [ ] 读取 JSONL 文件
  - [ ] 解析 Instruction 格式
  - [ ] 实现数据预处理和 tokenization
- [ ] 实现训练循环
  - [ ] 使用 Hugging Face Trainer API
  - [ ] 配置训练参数（learning_rate, batch_size, num_epochs 等）
  - [ ] 实现训练进度记录和日志
  - [ ] 实现检查点保存（checkpoint）
- [ ] 实现模型验证和评估
  - [ ] 在验证集上评估模型性能
  - [ ] 计算 NER、KE、KT 提取的准确率
  - [ ] 记录评估指标（loss, accuracy 等）
- [ ] 实现保存 LoRA 适配器的方法
  - [ ] 保存适配器权重（`adapter_model.bin`）
  - [ ] 保存适配器配置（`adapter_config.json`）
  - [ ] 保存训练元数据（训练日期、参数、性能指标等）
- [ ] 实现训练报告生成
- [ ] 添加错误处理和日志记录

**训练参数配置**:
```python
training_args = {
    "output_dir": "./models/eb-mm-lora-v1",
    "num_train_epochs": 3,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "learning_rate": 2e-4,
    "warmup_steps": 100,
    "logging_steps": 10,
    "save_steps": 500,
    "evaluation_strategy": "steps",
    "eval_steps": 500,
    "save_total_limit": 3,
    "load_best_model_at_end": True,
    "metric_for_best_model": "eval_loss",
}
```

**验收标准**:
- [ ] 训练脚本可运行
- [ ] 能够加载 DeepSeek-R1 8B 模型
- [ ] LoRA 配置正确
- [ ] 训练循环正常执行
- [ ] 模型验证和评估功能正常
- [ ] LoRA 适配器正确保存
- [ ] 训练报告生成正确
- [ ] 错误处理完善
- [ ] 日志记录详细
- [ ] 包含单元测试（覆盖率 > 70%，训练脚本测试较复杂）

**参考文档**:
- Hugging Face PEFT 文档: https://huggingface.co/docs/peft/
- Hugging Face Transformers 文档: https://huggingface.co/docs/transformers/

---

### Task 5.4: 实现模型版本管理

**文件**: `src/training/model_repository.py` (新建)

**任务**:
- [ ] 创建 `ModelRepository` 类
- [ ] 实现模型版本化逻辑
  - [ ] 版本命名规则：`eb-mm-lora-v{version}`（如 `eb-mm-lora-v1`, `eb-mm-lora-v2`）
  - [ ] 版本元数据存储（版本号、创建日期、训练参数、性能指标等）
- [ ] 实现模型存储接口
  - [ ] 本地存储：保存到 `models/` 目录
  - [ ] 可选：S3 存储（如果配置了 AWS）
  - [ ] 存储适配器文件和元数据
- [ ] 实现模型加载接口
  - [ ] 根据版本号加载适配器
  - [ ] 验证适配器文件完整性
  - [ ] 返回适配器路径和元数据
- [ ] 实现版本列表查询
  - [ ] 列出所有可用版本
  - [ ] 获取最新版本
  - [ ] 获取版本详细信息
- [ ] 实现版本删除（可选，谨慎使用）
- [ ] 实现版本回滚功能
- [ ] 添加错误处理和日志记录

**版本元数据格式**:
```json
{
  "version": "v1",
  "created_at": "2025-11-12T10:00:00Z",
  "base_model": "deepseek-r1:8b",
  "training_params": {
    "r": 8,
    "lora_alpha": 16,
    "target_modules": ["q_proj", "v_proj"],
    "num_epochs": 3,
    "learning_rate": 2e-4
  },
  "performance_metrics": {
    "ner_accuracy": 0.85,
    "kt_accuracy": 0.78,
    "eval_loss": 0.12
  },
  "data_stats": {
    "num_samples": 1000,
    "data_date_range": "2025-01-01 to 2025-11-12"
  }
}
```

**验收标准**:
- [ ] 版本管理正确
- [ ] 模型存储和加载正常
- [ ] 版本列表查询功能正常
- [ ] 版本元数据完整
- [ ] 错误处理完善
- [ ] 日志记录详细
- [ ] 包含单元测试（覆盖率 > 80%）

---

### Task 5.5: 扩展配置管理

**文件**: `src/config/settings.py`

**任务**:
- [ ] 创建 `TrainingSettings` 类
- [ ] 添加训练相关配置项
  - [ ] `training_enabled: bool` - 是否启用训练
  - [ ] `training_data_export_days: int` - 导出过去 N 天的数据
  - [ ] `training_quality_threshold: float` - 数据质量阈值
  - [ ] `training_output_dir: str` - 训练输出目录
  - [ ] `base_model_name: str` - 基础模型名称（如 "deepseek-r1:8b"）
  - [ ] `lora_rank: int` - LoRA rank 参数
  - [ ] `lora_alpha: int` - LoRA alpha 参数
  - [ ] `lora_target_modules: str` - LoRA target modules（逗号分隔）
  - [ ] `training_batch_size: int` - 训练批次大小
  - [ ] `training_learning_rate: float` - 学习率
  - [ ] `training_num_epochs: int` - 训练轮数
  - [ ] `model_storage_type: str` - 模型存储类型（"local" 或 "s3"）
  - [ ] `s3_bucket_name: str` - S3 存储桶名称（可选）
- [ ] 更新 `Settings` 类，包含 `TrainingSettings`
- [ ] 确保所有配置项都有默认值
- [ ] 支持环境变量覆盖
- [ ] 添加配置验证逻辑

**验收标准**:
- [ ] 所有配置项都有默认值
- [ ] 配置项有清晰的描述
- [ ] 支持环境变量覆盖
- [ ] 配置验证正确

---

### Task 5.6: 实现训练 CLI 命令（可选）

**文件**: `src/training/cli.py` (新建，可选)

**任务**:
- [ ] 创建 CLI 命令接口
- [ ] 实现 `export-data` 命令
  - [ ] 导出训练数据
  - [ ] 支持参数：`--days`, `--output`, `--quality-threshold`
- [ ] 实现 `train` 命令
  - [ ] 执行训练
  - [ ] 支持参数：`--data-file`, `--output-dir`, `--epochs`, `--batch-size`
- [ ] 实现 `list-models` 命令
  - [ ] 列出所有模型版本
- [ ] 实现 `use-model` 命令
  - [ ] 切换使用的模型版本
- [ ] 使用 `click` 或 `argparse` 实现 CLI

**验收标准**:
- [ ] CLI 命令可运行
- [ ] 参数解析正确
- [ ] 错误处理完善
- [ ] 帮助信息完整

**注意**: 此任务为可选，如果不需要 CLI 可以跳过。

---

### Task 5.7: 集成训练任务到主服务（可选）

**文件**: `src/main.py`, `src/training/training_scheduler.py` (新建，可选)

**任务**:
- [ ] 创建 `TrainingScheduler` 类（可选）
- [ ] 实现定期训练任务
  - [ ] 使用 Celery 或 APScheduler 实现定时任务
  - [ ] 配置训练频率（如每周一次）
- [ ] 在 `main.py` 中集成训练调度器（可选）
- [ ] 实现训练任务监控和通知

**验收标准**:
- [ ] 定时任务正常工作
- [ ] 训练任务可以独立运行
- [ ] 不影响主服务性能

**注意**: 此任务为可选，训练管道可以独立运行，不需要集成到主服务。

---

### Task 5.8: 单元测试和集成测试

**文件**: 
- `tests/unit/test_data_exporter.py` (新建)
- `tests/unit/test_train_lora.py` (新建)
- `tests/unit/test_model_repository.py` (新建)
- `tests/integration/test_training_pipeline.py` (新建)

**任务**:
- [ ] 测试数据导出器
  - [ ] 测试 ChromaDB 连接和数据查询
  - [ ] 测试数据清洗和过滤
  - [ ] 测试 JSONL 格式转换
  - [ ] 测试错误处理
- [ ] 测试 LoRA 训练脚本
  - [ ] 测试模型加载
  - [ ] 测试 LoRA 配置
  - [ ] 测试训练循环（使用小数据集）
  - [ ] 测试适配器保存
- [ ] 测试模型版本管理
  - [ ] 测试版本创建和存储
  - [ ] 测试版本加载
  - [ ] 测试版本列表查询
  - [ ] 测试版本元数据
- [ ] 集成测试
  - [ ] 测试完整训练流程（数据导出 → 训练 → 版本管理）
  - [ ] 测试训练后的模型集成（可选，需要真实模型服务）

**验收标准**:
- [ ] 单元测试覆盖率 > 80%（训练脚本 > 70%）
- [ ] 集成测试通过
- [ ] 包含真实数据测试用例
- [ ] 所有边界情况都有测试
- [ ] 错误处理测试完善

---

## 验收标准总结

- [ ] 数据导出器正常工作，能够从 ChromaDB 导出高质量数据
- [ ] LoRA 训练脚本可运行，能够训练适配器
- [ ] 模型版本管理正常，支持版本化存储和加载
- [ ] 配置管理支持训练参数
- [ ] 训练管道完整实现
- [ ] LoRA 适配器训练完成
- [ ] 模型性能达到目标（NER > 80%, KT > 75%）（需要实际训练验证）
- [ ] 单元测试覆盖率 > 80%（训练脚本 > 70%）
- [ ] 集成测试通过
- [ ] 代码符合 AiDevelopmentGuide.md 规范
- [ ] 所有文件包含标准头部注释
- [ ] 通过 linter 检查

---

## 创建/修改的文件

### 新建文件

1. `src/training/__init__.py` - 训练模块初始化
2. `src/training/data_exporter.py` - 数据导出器实现
3. `src/training/train_lora.py` - LoRA 训练脚本
4. `src/training/model_repository.py` - 模型版本管理
5. `src/training/utils.py` - 工具函数（可选）
6. `src/training/cli.py` - CLI 命令接口（可选）
7. `src/training/training_scheduler.py` - 训练调度器（可选）
8. `tests/unit/test_data_exporter.py` - 数据导出器单元测试
9. `tests/unit/test_train_lora.py` - LoRA 训练单元测试
10. `tests/unit/test_model_repository.py` - 模型版本管理单元测试
11. `tests/integration/test_training_pipeline.py` - 训练管道集成测试

### 修改文件

1. `src/config/settings.py` - 添加 `TrainingSettings` 配置类
2. `requirements.txt` - 添加训练相关依赖（transformers, peft, datasets 等）

---

## 依赖关系

- **前置**: 
  - Phase I 已完成（需要 ChromaDB 中有数据）
  - 批次一（降级策略框架）已完成
  - 批次二（抽象模型服务层）已完成
- **可并行**: 可与批次三、四并行进行（不阻塞其他批次）
- **后续**: 批次四可以在模型训练完成后使用训练好的 LoRA 适配器

---

## 依赖包

需要添加以下 Python 包到 `requirements.txt`:

```txt
# LoRA 训练相关
transformers>=4.35.0
peft>=0.7.0
datasets>=2.14.0
accelerate>=0.24.0
bitsandbytes>=0.41.0  # 可选，用于模型量化
torch>=2.0.0  # 如果还没有
```

---

## 参考文档

- `docs/AAM Agent SD v2.md` - 系统设计规格
- `docs/plan/AAM Phase II.md` - Phase II 总体计划
- `docs/plan/PII-批次四：EB-mM 模型集成实施计划.md` - 批次四实施计划
- `docs/AAM (AI-Augmented Memory) SA v1.md` - LoRA 训练说明
- `docs/AiDevelopmentGuide.md` - 开发规范
- Hugging Face PEFT 文档: https://huggingface.co/docs/peft/
- Hugging Face Transformers 文档: https://huggingface.co/docs/transformers/

---

## 计划备份

**备份要求**:
- **时機**: 执行计划前
- **路径**: `/aam-service/docs/plan/`
- **文件名**: `PII-批次五：LoRA 训练管道实施计划.md`
- **内容**: 完整的计划内容（本文件）

**备份状态**: ✅ 已备份（本文件即为备份）

---

## 测试报告要求

测试完成后，需要在 `tests/reports/` 目录下创建测试报告：

**文件**: `tests/reports/批次五：LoRA 训练管道-測試報告.md`

**报告内容结构**:
- 测试概述
- 测试项目
- 测试结果（通过项目、失败项目、待改进项目）
- 结论与建议

**参考格式**: 参考 `tests/reports/PII-批次四：EB-mM 模型集成-測試報告.md`

---

**最后更新**: 2025-11-12

