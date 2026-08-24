---
name: lexiang-vault-sync
description: >-
  把 Obsidian vault 单向同步到腾讯乐享作为外部可读镜像。当用户说"同步乐享"
  "导入乐享""更新乐享镜像""push to lexiang""乐享重导""刷新乐享页面"时触发。
  负责：md→乐享 md 转换（图片 ![[...]]→COS URL、wikilink [[...]]→/pages/{id}）、
  逐页 entry_import_content_to_entry 重导、陈旧孤儿块护栏（以 block_fetch_page 为准）、
  CJK 近形字码点校验、畸形链接 pre-flight、幂等重同步。vault 是源，乐享是派生，绝不回写。
agent_created: true
---

# 乐享镜像同步器（lexiang-vault-sync）

把凌日星世界观 vault（`/workspace/世界观`）单向同步到腾讯乐享，作为外部可读镜像。
**vault 是源，乐享是派生，镜像永不回写 vault。**

## 动机
本轮工作中把全量 vault 导入乐享，踩出大量平台特有坑（陈旧孤儿块、CJK 字符被误判篡改、
图片/链接转换规则）。现有 `obsidian-*` 全部是 vault **内部**工具，无任何 skill
覆盖"vault → 乐享"传输层。本 skill 填补这一真空。

## 输入 / 输出
- **输入**：vault 根目录、`lexiang_page_map.json`（路径→entry_id）、`lexiang_img_map.json`（文件名→COS URL）
- **输出**：乐享镜像页面（与 vault 内容一致）、更新后的映射 JSON、`sync_report.json`

## 工作流（命令式）
1. 读 `lexiang_page_map.json` 得路径→entry_id 映射；新页面用 `mcp__lexiang-ol__entry_create_entry` 建页。
2. 对每篇 md 跑 `scripts/vault_to_lexiang.py`：
   - `![[图片/x.jpg]]` → COS 基础 URL（查 `lexiang_img_map.json`；缺失则先 `mcp__lexiang-ol__file_*` 上传取 URL）
   - `[[文件夹/笔记|别名]]` → `/pages/{entry_id}`（查 page_map；缺失则标 pending）
   - **保留**表格内 `\|` 转义（乐享亦需）
3. 跑 `scripts/preflight.py` 做 pre-flight 校验：畸形 `[[` 含空格、未转义 `|`、CJK 近形字
   （`references/cjk_glyph_table.md` 码点比对）。不通过则中止该页并报告。
4. 调 `mcp__lexiang-ol__entry_import_content_to_entry`（force_write）整页重导。
5. **护栏（关键）**：重导后立即 `mcp__lexiang-ol__block_fetch_page` 取当前块树，用
   `scripts/verify_blocks.py` 与源 md 做文本/字符级（按码点）比对，确认无陈旧孤儿块残留、
   CJK 字符未被篡改。**绝不以单 `block_id` 的 `block_describe_block` 读数判定正确性。**
6. 更新映射 JSON，输出 `sync_report.json`（新增/更新/跳过/失败）。

## 文件结构
```
lexiang-vault-sync/
├── SKILL.md
├── scripts/
│   ├── vault_to_lexiang.py   # md→乐享 md 转换（可独立运行）
│   ├── preflight.py          # 畸形链接 + CJK 码点校验（可独立运行）
│   └── verify_blocks.py      # block_fetch_page 后比对（比对逻辑可运行，MCP 取数由 agent 执行）
├── references/
│   ├── cjk_glyph_table.md    # 近形字码点对照（是/昰 等）
│   └── lexiang_conversion.md # 图片/链接转换规则
└── assets/
    └── sync_report.template.json
```

## 护栏 / 已知坑（来自实战，务必遵守）
- **陈旧孤儿块**：整页重导后旧 `block_id` 仍可被 `block_describe_block` 读到陈旧内容 →
  必须用 `block_fetch_page` 当前块树判定真实状态。
- **CJK 字符完整性**：乐享平台不篡改字符；"不过昰"误报是手敲错字 + 孤儿块误读，非 bug →
  用 `references/cjk_glyph_table.md` 码点校验，不凭肉眼。
- **单向性**：乐享永不回写 vault；镜像永远是派生。
- **幂等**：重导用 force_write，可重复执行；page_map 缺失的页面先建后导。

## 去重说明
与现有 `obsidian-*` **无重叠**（那些是 vault 内部工具）。本 skill 专注
"vault → 外部平台"传输层，是唯一覆盖乐享同步的 skill。
