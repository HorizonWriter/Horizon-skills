---
name: obsidian-backlink-completer
description: 通用 Obsidian 双向引用补全器。扫描 vault 条目的"关联板块"，检测 A→B 但 B 未反向引用 A，自动追加根相对回链（不注入 ../，正确处理表格内 \| 转义）。当用户说"补全反向链接""修复单向引用""check backlinks""关联板块完备率""双向引用"时使用。
---

# Obsidian Backlink Completer

自动补全 Obsidian vault 条目间缺失的双向关联引用。

## 工作原理

1. 扫描所有 `.md` 条目，从"关联板块 / related / backlinks"行提取 wikilink
2. 检测 A 引用了 B、但 B 没有反向引用 A 的单向引用
3. dry-run 预览 / `--apply` 自动追加回链 / `--stats` 仅统计完备率

写入的链接格式为 **vault 根相对** `[[目录/文件|别名]]`，符合 Obsidian 规范（不注入 `../`，表格内 `\|` 正确转义）。

## 用法

```bash
# 预览缺失回链（不写入）
python completer.py /path/to/vault

# 写入修复（自动 .bak 备份）
python completer.py /path/to/vault --apply

# 仅统计完备率
python completer.py /path/to/vault --stats
```

## 环境变量（可选）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LINK_SECTION` | `关联板块\|关联人物\|related\|backlinks` | 关联板块关键词（\| 分隔的正则 or） |
| `IGNORE_DIRS` | （空） | 额外忽略目录（逗号分隔） |
| `NON_ENTRY` | `.gitignore,README.md,LICENSE` | 不算条目的文件名（逗号分隔） |

## 注意

- 写入操作会生成 `.bak` 备份文件
- 正确处理表格内转义管道 `\|`（提取目标前先还原）
- 与 `obsidian-vault-doctor` 互补：doctor 修链接语法（死链/转义），本工具补缺失的回链

## 关联技能

- `obsidian-vault-doctor` — 链接语法修复（死链、表格转义、`../`）
- `obsidian-consistency-checker` — 内容一致性检查
- `obsidian-orphan-auditor` — 索引/总览完整性
