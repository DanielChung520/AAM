/**
 * @purpose: 版本比较组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Select,
  Option,
  Sheet,
  Code,
  Chip,
  Divider,
  Accordion,
  AccordionGroup,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { Version, VersionCompareResult } from '@/types/version';

export interface VersionCompareProps {
  versions: Version[];
  onCompare: (v1: string, v2: string) => Promise<VersionCompareResult>;
  loading?: boolean;
}

export const VersionCompare: React.FC<VersionCompareProps> = ({
  versions,
  onCompare,
  loading = false,
}) => {
  const { mode } = useColorScheme();
  const [version1, setVersion1] = useState<string>('');
  const [version2, setVersion2] = useState<string>('');
  const [compareResult, setCompareResult] = useState<VersionCompareResult | null>(null);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (version1 && version2 && version1 !== version2) {
      handleCompare();
    } else {
      setCompareResult(null);
    }
  }, [version1, version2]);

  const handleCompare = async () => {
    if (!version1 || !version2 || version1 === version2) {
      return;
    }

    try {
      setComparing(true);
      setError(null);
      const result = await onCompare(version1, version2);
      setCompareResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '比较版本失败');
      setCompareResult(null);
    } finally {
      setComparing(false);
    }
  };

  const getDiffColor = (type: 'added' | 'removed' | 'modified') => {
    switch (type) {
      case 'added':
        return mode === 'dark' ? 'success.700' : 'success.100';
      case 'removed':
        return mode === 'dark' ? 'danger.700' : 'danger.100';
      case 'modified':
        return mode === 'dark' ? 'warning.700' : 'warning.100';
    }
  };

  const getDiffTextColor = (type: 'added' | 'removed' | 'modified') => {
    switch (type) {
      case 'added':
        return mode === 'dark' ? 'success.300' : 'success.700';
      case 'removed':
        return mode === 'dark' ? 'danger.300' : 'danger.700';
      case 'modified':
        return mode === 'dark' ? 'warning.300' : 'warning.700';
    }
  };

  return (
    <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
      {/* 版本选择器 */}
      <Card>
        <CardContent>
          <Typography level="title-lg" sx={{ mb: 2 }}>
            版本比较
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
            <Select
              placeholder="选择版本 1"
              value={version1}
              onChange={(_, value) => setVersion1(value as string)}
              sx={{ minWidth: 200 }}
              disabled={loading || comparing}
            >
              {versions.map((v) => (
                <Option key={v.version} value={v.version}>
                  {v.version}
                </Option>
              ))}
            </Select>

            <Typography level="body-md" sx={{ color: 'text.secondary' }}>
              vs
            </Typography>

            <Select
              placeholder="选择版本 2"
              value={version2}
              onChange={(_, value) => setVersion2(value as string)}
              sx={{ minWidth: 200 }}
              disabled={loading || comparing}
            >
              {versions.map((v) => (
                <Option key={v.version} value={v.version}>
                  {v.version}
                </Option>
              ))}
            </Select>
          </Box>
        </CardContent>
      </Card>

      {/* 比较结果 */}
      {comparing && (
        <Card>
          <CardContent>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              正在比较...
            </Typography>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card>
          <CardContent>
            <Typography level="body-sm" sx={{ color: 'danger.500' }}>
              {error}
            </Typography>
          </CardContent>
        </Card>
      )}

      {compareResult && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* 差异摘要 */}
          <Card>
            <CardContent>
              <Typography level="title-md" sx={{ mb: 2 }}>
                差异摘要
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip color="success" variant="soft">
                  新增: {compareResult.summary.added}
                </Chip>
                <Chip color="danger" variant="soft">
                  删除: {compareResult.summary.removed}
                </Chip>
                <Chip color="warning" variant="soft">
                  修改: {compareResult.summary.modified}
                </Chip>
              </Box>
            </CardContent>
          </Card>

          {/* 详细差异 */}
          <Card>
            <CardContent>
              <Typography level="title-md" sx={{ mb: 2 }}>
                详细差异
              </Typography>
              <AccordionGroup>
                {Object.entries(compareResult.differences).map(([category, diff]) => (
                  <Accordion key={category}>
                    <AccordionSummary>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                        <Typography level="title-sm">{category}</Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          {diff.added.length > 0 && (
                            <Chip size="sm" color="success" variant="soft">
                              +{diff.added.length}
                            </Chip>
                          )}
                          {diff.removed.length > 0 && (
                            <Chip size="sm" color="danger" variant="soft">
                              -{diff.removed.length}
                            </Chip>
                          )}
                          {diff.modified.length > 0 && (
                            <Chip size="sm" color="warning" variant="soft">
                              ~{diff.modified.length}
                            </Chip>
                          )}
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {diff.added.length > 0 && (
                          <Box>
                            <Typography level="body-sm" sx={{ mb: 1, fontWeight: 'bold', color: getDiffTextColor('added') }}>
                              新增项 ({diff.added.length})
                            </Typography>
                            <List>
                              {diff.added.map((item, index) => (
                                <ListItem key={index}>
                                  <Sheet
                                    sx={{
                                      p: 1,
                                      bgcolor: getDiffColor('added'),
                                      borderRadius: 'sm',
                                      width: '100%',
                                    }}
                                  >
                                    <Code sx={{ color: getDiffTextColor('added') }}>+ {item}</Code>
                                  </Sheet>
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                        )}

                        {diff.removed.length > 0 && (
                          <Box>
                            <Typography level="body-sm" sx={{ mb: 1, fontWeight: 'bold', color: getDiffTextColor('removed') }}>
                              删除项 ({diff.removed.length})
                            </Typography>
                            <List>
                              {diff.removed.map((item, index) => (
                                <ListItem key={index}>
                                  <Sheet
                                    sx={{
                                      p: 1,
                                      bgcolor: getDiffColor('removed'),
                                      borderRadius: 'sm',
                                      width: '100%',
                                    }}
                                  >
                                    <Code sx={{ color: getDiffTextColor('removed') }}>- {item}</Code>
                                  </Sheet>
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                        )}

                        {diff.modified.length > 0 && (
                          <Box>
                            <Typography level="body-sm" sx={{ mb: 1, fontWeight: 'bold', color: getDiffTextColor('modified') }}>
                              修改项 ({diff.modified.length})
                            </Typography>
                            <List>
                              {diff.modified.map((item, index) => (
                                <ListItem key={index}>
                                  <Sheet
                                    sx={{
                                      p: 1,
                                      bgcolor: getDiffColor('modified'),
                                      borderRadius: 'sm',
                                      width: '100%',
                                    }}
                                  >
                                    <Code sx={{ color: getDiffTextColor('modified') }}>~ {item}</Code>
                                  </Sheet>
                                </ListItem>
                              ))}
                            </List>
                          </Box>
                        )}

                        {diff.added.length === 0 && diff.removed.length === 0 && diff.modified.length === 0 && (
                          <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                            无差异
                          </Typography>
                        )}
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </AccordionGroup>
            </CardContent>
          </Card>
        </Box>
      )}

      {!version1 || !version2 ? (
        <Card>
          <CardContent>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              请选择两个版本进行比较
            </Typography>
          </CardContent>
        </Card>
      ) : null}
    </Box>
  );
};

export default VersionCompare;

