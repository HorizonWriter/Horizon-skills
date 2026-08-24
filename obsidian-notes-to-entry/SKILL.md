---
name: obsidian-notes-to-entry
description: 通用 Obsidian 笔记标准化转换器。检测笔记是否已是标准格式（H1+基本档案表格+关联板块），若否则提取字段信息生成标准骨架、保留原始正文。ENTRY_FIELDS/LINK_SECTION 可通过环境变量配置。当用户说"标准化笔记""笔记转条目""normalize note""格式不规范""转换格式"时使用。
---

# Obsidian Notes to Entry

将非标准格式的笔记转换为标准条目格式。

## 工作原理

1. 检测是否已标准化（有 H1 + 基本档案表格 + 关联板块行）
2. 若未标准化：提取字段信息（种族/阵营/职位等，可配置）、提取已有 wikilink
3. 生成标准骨架（H1 + 基本档案表格 + 原始正文 + 关联板块），保留所有原始内容
4. `--apply` 写入（自动 `.bak` 备份）

## 用法

```bash
# 预览转换（不写入）
python normalize.py /path/to/vault 角色/云朵

# 执行转换（自动 .bak 备份）
python normalize.py /path/to/vault 角色/云朵 --apply
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ENTRY_FIELDS` | `种族,阵营,职位,状态,核心标签` | 基本档案字段（逗号分隔） |
| `LINK_SECTION` | `关联板块\|关联人物\|related\|backlinks` | 关联板块关键词 |

## 注意

- 已标准化的文件不会被修改（检测到 H1+表格+关联板块即跳过）
- 写入前自动生成 `.bak` 备份
- 正确处理表格内转义管道 `\|`

## 关联技能

- `obsidian-note-scaffolder` — 新建标准条目（从零创建）
- `obsidian-section-filler` — 补全空文件（已有文件缺内容）
- `obsidian-consistency-checker` — 检查内容一致性
