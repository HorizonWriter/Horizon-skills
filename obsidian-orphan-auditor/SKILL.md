---
name: obsidian-orphan-auditor
description: 审计任意 Obsidian vault 的索引/总览页完整性——缺条目、孤立链接、重复索引、重复文件、无索引目录。当用户说"检查索引""索引完整性""总览同步""孤儿链接""重复文件""verify index""审计索引"时触发。只读不写，通用适用，正确处理表格内转义管道。
---

# Obsidian 索引/总览完整性审计器（通用版）

基于 `worldbuilding-index-auditor` 的核心逻辑改造为**通用 Obsidian** 工具：去掉世界观硬编码，正确处理 `[[...\|别名]]` 中的转义竖线，支持 `../`、根相对、basename 三种链接形式解析。

## 它解决什么

Obsidian vault 用「总览/索引/清单」页聚合某目录下的条目。当有人新增笔记却没更新索引、或删了文件却留着链接，索引就会**缺条目**或挂**孤立链接**——这类问题 `obsidian-vault-doctor` 的死链检测抓不到（链接本身没断，只是索引和实际不同步）。

## 检测维度

1. **缺条目**：目录内有文件，但对应索引页没列它
2. **孤立链接**：索引页里列了链接，但目标文件已不存在
3. **重复索引**：同目录有多个总览/索引文件
4. **缺索引**：目录有文件但没有索引页
5. **重复文件**：同目录内文件名高度重叠、共享链接 > 40% 的文件对

## 用法

```bash
# 索引完整性审计
python scripts/auditor.py <vault_root>
# 重复文件检测
python scripts/auditor.py <vault_root> --dedup
```

索引页识别关键词（中英文，可在脚本顶部 `INDEX_KEYWORDS` 调整）：`总览 索引 清单 index overview 目录`。

## 与 obsidian-vault-doctor 的区别

- `vault-doctor`：链接**是否断**（死链 / `../` / 表格转义 / canvas）
- 本 skill：索引**是否与实际目录同步**（缺条目 / 孤立链接 / 重复）

两者互补，不重叠。

## 安全

纯只读，不修改任何文件。
