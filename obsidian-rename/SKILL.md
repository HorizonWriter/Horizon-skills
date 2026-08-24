---
name: obsidian-rename
description: 通用 Obsidian 文件重命名工具，重命名后自动更新全库所有 wikilink 引用。支持匹配根相对路径、裸名(basename)、../相对路径三种链接形式，写入的新链接保持原形式（绝不新注入 ../），正确处理表格内 \| 转义。当用户说"重命名笔记""rename file""改文件名并更新链接""批量更新引用"时使用。
---

# Obsidian Rename

重命名 vault 文件并自动更新全库所有 wikilink 引用。

## 工作原理

1. 备份原文件（`.rename.bak`）
2. 重命名文件
3. 扫描全库 `.md`，将所有指向旧文件的 wikilink 更新为新路径

支持匹配三种链接形式：
- **根相对** `[[角色/云朵|云朵]]` → 精确匹配路径
- **裸名** `[[云朵]]` → 按 basename 匹配
- **`../` 相对** `[[../角色/云朵]]` → 兼容已有（但不新注入）

写入的新链接**保持原形式**：根相对→根相对，裸名→裸名。表格内 `\|` 转义保持不变。

## 用法

```bash
# 预览（不写入）
python rename.py /path/to/vault 角色/云朵.md 角色/云朵小天使.md --dry-run

# 执行（自动 .rename.bak 备份）
python rename.py /path/to/vault 角色/云朵.md 角色/云朵小天使.md
```

路径为 **vault 根相对**，可带可不带 `.md` 后缀。

## 注意

- 执行前建议先用 `--dry-run` 预览影响范围
- 自动生成 `.rename.bak` 备份（仅原文件）
- 建议先用 `obsidian-vault-doctor` 消灭 `../` 链接，再重命名（减少匹配歧义）

## 关联技能

- `obsidian-vault-doctor` — 修链接语法（消灭 `../`、修转义）
- `obsidian-note-scaffolder` — 新建条目（重命名的互补操作）
