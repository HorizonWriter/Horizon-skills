---
name: obsidian-section-filler
description: 通用 Obsidian 内容填充器。自动扫描 vault 顶层目录作为板块，列出空文件/迷你文件/待补充文件，可选自动生成标准骨架内容。板块目录自动发现（不硬编码），模板可配置。当用户说"填充空文件""待补充清单""填充骨架""fill empty""哪些该补""板块状态"时使用。
---

# Obsidian Section Filler

扫描 vault 中的空文件/迷你文件/待补充文件，自动生成标准骨架内容。

## 工作原理

- 自动扫描 vault 顶层目录作为"板块"（不硬编码板块列表）
- 判定"待填充"：文件 < `MIN_SIZE` 字节 或 内容含"待补充"
- `--fill-empty`：给空文件生成通用骨架（H1 + 基本档案表格 + 概述 + 详细信息 + 关联板块）
- 非空文件不会被覆盖

## 用法

```bash
# 列出所有板块的空文件
python filler.py /path/to/vault --list-all

# 查看某板块填充状态
python filler.py /path/to/vault --status 角色

# 自动填充所有空文件（交互确认）
python filler.py /path/to/vault --fill-empty
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MIN_SIZE` | `50` | 判定为"空文件"的大小阈值（字节） |
| `TEMPLATE_FILE` | `.template.md` | 模板文件后缀（目录下有则读取） |

## 关联技能

- `obsidian-note-scaffolder` — 新建标准条目（filler 补全已有空文件）
- `obsidian-content-hotspot` — 内容空洞排名（filler 列出空文件，hotspot 按优先级排名）
- `obsidian-entry-register` — 注册新条目到索引
