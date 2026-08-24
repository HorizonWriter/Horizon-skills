---
name: obsidian-timeline-checker
description: 通用 Obsidian 时间线矛盾检测器。扫描 vault 中的时间引用、年龄线索、占位年份，跨文件交叉对比输出疑似矛盾。默认匹配通用"\d{1,4}年"，可通过 ERA_PATTERN 环境变量追加自定义纪年（如"凌日纪年\d+年""公元\d+年"）。当用户说"检查时间线""timeline conflict""时间矛盾""年份冲突""年龄矛盾"时使用。
---

# Obsidian Timeline Checker

扫描 vault 中的时间引用并检测跨文件矛盾。

## 工作原理

1. 提取所有时间引用（年份、年龄、首次出现、出生描述、占位符）
2. 统计时间引用分布（哪些年份被哪些文件引用）
3. 检测同一年份关键词出现在同一文件（可能描述不同事件 → 疑似矛盾）
4. 输出占位年份分布（`■■■` / `???` / `TBD` / `待定`）

## 用法

```bash
# 默认通用模式（匹配 "2024年"、"85年" 等）
python checker.py /path/to/vault

# 追加自定义纪年模式
ERA_PATTERN="凌日纪年[前]?约?(\d+)年" python checker.py /path/to/vault

# 多纪年体系
ERA_PATTERN="公元(\d+)年|建安(\d+)年" python checker.py /path/to/vault
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ERA_PATTERN` | （空） | 自定义纪年正则（设了则同时匹配通用年份 + 自定义） |
| `PLACEHOLDER` | `■■■\|\?\?\?\|TBD\|待定` | 占位符模式（\| 分隔） |
| `IGNORE_DIRS` | （空） | 额外忽略目录（逗号分隔） |

## 注意

- "疑似矛盾"是指同一年份关键词出现在同一文件，需人工核实（不一定是真矛盾）
- 年龄线索会显示上下文前缀（前 40 字符）便于判断

## 关联技能

- `obsidian-consistency-checker` — 内容一致性（重复段落、概念冲突等）
- `obsidian-vault-doctor` — 链接语法修复
