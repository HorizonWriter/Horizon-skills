---
name: obsidian-vault-doctor
description: 诊断并修复 Obsidian 笔记库的链接与表格问题——相对路径 wikilink([[../...]])、表格内管道符转义、死链、.md 后缀、图片嵌入、.canvas 画布里的链接、转义嵌入(\![[导致图片不渲染)、内容条目缺 frontmatter、CJK 近形字(是/昰)码点校验。编码了"表格内管道必须转义"这条极易写反的规则和转义管道的正确解析方式，避免重复试错。当用户说"表格打散""wikilink 失效""链接点不开""Obsidian 链接修复""检查死链""转义嵌入""图片不显示""体检并修复"时使用。
---

# Obsidian Vault Doctor

一键体检 + 修复 Obsidian 笔记库常见的"链接点不开 / 表格被打散"类问题。

## 何时使用
- 用户报告 Obsidian 里表格"被打散"、wikilink 显示为纯文本、链接点不开。
- 用户要求"检查死链 / 体检 / 规范化链接"。
- 批量把某个生成器产出的 `[[../相对路径/文件.md|别名]]` 改成 Obsidian 原生写法。

## 关键规则（踩过坑才得出的正确结论，照做别反向）
1. **Obsidian wikilink 基于 vault 根**：`[[文件夹/笔记|别名]]`，**原生不认 `../` 相对路径**。`[[../Sibling/Note]]` 必死。
2. **表格单元格内的 piped link，别名分隔符 `|` 必须转义为 `\|`**（Obsidian 官方确认）。
   - 表格解析器**先按未转义 `|` 拆列，再解析行内元素**，`[[ ]]` 保护不了内部管道。
   - 段落 / 列表里的 `|` **不要转义**，直接写 `|`。
3. **错误示范**（我第一轮就是这么写反的）：把全库 `\|` 改成 `|` → 表格被撑成多列、链接废掉。
4. **正确示范**：
   - 表格内：`| [[组织/摩晶工业\|摩晶工业]] |`
   - 段落内：`见 [[组织/摩晶工业|摩晶工业]]`

## 解析链接时的致命陷阱（工具自身也会踩）
- 提取目标时**切勿**用 `inner.split('|')`——转义后的 `\|` 会被一起切开，得到 `组织/摩晶工业\|摩晶工业` 这种含别名的假路径。
- 正确：`re.split(r'\\?\|', inner)[0]` —— 按"可选反斜杠 + 管道"切，第一节即目标。
- `![[图片.png]]` 是**图片嵌入**，不是笔记链接，解析时要按资源路径校验，别当 `.md` 去查。

## 标准作业流程（SOP）
1. **先定位 vault 根**：找含 `.obsidian/` 的目录（通常是用户给的库根）。
2. **备份**：`shutil.copytree(vault, backup_dir)` 再动手（绝不做无备份的批量改写）。
3. **审计**（用附带 `doctor.py`，`python doctor.py <vault>`）：
   - 死链（目标文件不存在）、`../` 残留、`.md` 后缀、表格内未转义 `|`、图片嵌入失效、歧义（重名 basename）、**`.canvas` 画布里的断裂链接**。
   - **必须扫 `.canvas` 文件**：画布的 JSON 里 `file` 节点和文字节点的 `text` 都含 wikilink，纯 `.md` 扫描会漏掉（本次就漏出一个幻影文件夹死链）。
4. **修复**（带 `--fix`，仅对"目标真实存在"的链接改写，绝不制造新死链）：
   - `[[../a/b.md|alias]]` → `[[a/b|alias]]`（去 `../`、去 `.md`）
   - 表格行内的 link inner 未转义 `|` → `\|`
   - 顺手统一去 `.md` 后缀（指向不变）
   - canvas 节点同样归一化
5. **复检**：再跑一次 `doctor.py`，确认全 0。

## 边界 / 不处理
- `[[#标题]]` 同笔记锚点、frontmatter `aliases` 作为目标——本库 0 个别名，风险低，脚本已做 basename+alias 兜底。
- 其他独立仓库（`世界观-web/`、`archives/`）属于不同 vault，不在本次范围内，需单独跑。
- 无版本控制时，回滚只靠备份目录；建议对库 `git init`。

## 附带脚本
`doctor.py` —— 审计 + 可选修复，纯标准库，无依赖。

## 本轮合并的新探测器（vault 治理轮次，合并自 obsidian-vault-doctor 增强 + 原 cjk-glyph-guard 微 skill）
在原有 7 维（dead / dotdot / mdsuffix / pipe_unesc / img_fail / ambiguous / canvas_broken）之上，新增 3 维：

1. **`escaped_embed`（转义嵌入）**：扫描 `\![[`（正则 `\\!\\[\\[`）。写成 `\![[图片/x.jpg]]` 会被 Obsidian 当字面文本、**图片不渲染**；正确写法是 `![[图片/x.jpg]]`。本轮 vault 曾因此 8 处（云朵×7、祢俎×1）图片不显示，已修复。
   - 修复（`--fix`）：仅对图片嵌入 `\![[图片/` → `![[图片/`（外科手术式，不动文档示例中的 `\![[...]]`）。
2. **`missing_fm`（内容条目缺 frontmatter）**：内容条目（排除 `_templates`/`_scenes`/`.trash`）不以 `---` 开头即标记。模板/场景/回收站属预期无 frontmatter。
   - 修复（`--fix --add-frontmatter`）：补 `--- / tags: / ---` 空骨架，**不自动填设定内容**（防脑补）。
3. **`cjk_glyph`（CJK 近形字）**：按 `references/cjk_glyph_table.md` 的码点集合扫描正文，命中即报警（如 `昰` U+6630 应为 `是` U+662F）。仅报告、不自动改（字形需人判）。

用法补充：
```
python doctor.py <vault>                # 仅审计（含 3 新维）
python doctor.py <vault> --fix          # 审计 + 修链接/管道/转义嵌入（自动备份）
python doctor.py <vault> --fix --add-frontmatter   # 上述 + 补 frontmatter 骨架
```
