---
name: obsidian-entry-register
description: 通用 Obsidian 条目注册器。新建条目后自动更新对应板块总览页、同板块提到该名称的文件关联板块、全局索引页。INDEX_MAP/INDEX_FILE/LINK_SECTION 均可通过环境变量配置。当用户说"注册新文件""auto register""更新总览""加入索引""新条目注册"时使用。
---

# Obsidian Entry Register

新建条目后自动注册到索引/总览页，保持 vault 索引同步。

## 工作原理

1. **板块总览**：如果文件在某个板块目录下且该板块配置了总览页，追加 wikilink 引用
2. **同板块关联板块**：同目录下提到该条目名称的文件，在其关联板块行追加回链
3. **全局索引**：追加到全局索引文件（如 `世界索引.md`）

## 用法

```bash
# 注册单个文件
python register.py /path/to/vault 角色/云朵.md

# 扫描所有未注册文件
python register.py /path/to/vault --all
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `INDEX_MAP` | `{}` | 板块→总览路径 JSON，如 `{"组织":"组织/组织总览.md","角色":"角色/角色总览.md"}` |
| `INDEX_FILE` | `世界索引.md` | 全局索引文件（不存在则跳过） |
| `LINK_SECTION` | `关联板块\|关联人物\|related\|backlinks` | 关联板块关键词 |

## 注意

- 写入操作直接修改总览/索引文件（建议先用 git 管理或备份）
- `--all` 会扫描全 vault，跳过 `<50B` 的迷你文件

## 关联技能

- `obsidian-orphan-auditor` — 检测索引缺失（注册的互补操作）
- `obsidian-note-scaffolder` — 新建标准条目（注册的前置操作）
