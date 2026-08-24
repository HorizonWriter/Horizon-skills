---
name: obsidian-content-hotspot
description: 通用 Obsidian 内容空洞排名器。扫描 vault 所有 .md，按「被引用数 × 内容空置率」排名，找出"被引用最多但内容最空"的笔记，输出优先写作队列。当用户说"该先写哪个""内容空洞""哪些笔记该补""content hotspot""写作优先级""空洞排名"时使用。
---

# Obsidian Content Hotspot

找出 vault 中"被引用最多但内容最空"的笔记，生成优先写作队列。

## 工作原理

- **内容密度** = 正文行数 / 总行数（排除标题、引用、分隔线、表格行）
- **空置率** = 1 - 密度
- **得分** = 被引用数 × 空置率
- 得分越高 = 越多文件引用它、但它本身内容越空 → 最该先写

## 用法

```bash
# 默认前 20
python hotspot.py /path/to/vault

# 前 50
python hotspot.py /path/to/vault --top 50

# 只看被引用 ≥5 次的
python hotspot.py /path/to/vault --threshold 5
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `IGNORE_DIRS` | （空） | 额外忽略目录（逗号分隔） |

## 关联技能

- `obsidian-consistency-checker` — 查内容逻辑一致性（空文件、重复段落等）
- `obsidian-backlink-completer` — 补全双向引用
