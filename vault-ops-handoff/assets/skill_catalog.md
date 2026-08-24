# 现有 skill 速查（SKILLBUILD 去重用）

> 生成于 vault 运维轮次。新增 skill 前先比对，避免重复。

| skill | 能力 | 约束 |
|-------|------|------|
| `obsidian-consistency-checker` | 通用只读一致性扫描（9 维，含 `\|` 表格转义、死链、孤儿、单向引用、概念冲突） | 只读不写 |
| `obsidian-vault-doctor` | **一体机**：只读 7 维 + 新增 3 维（转义嵌入/缺 frontmatter/CJK）+ 安全自动修复 | 已增强，勿重建 |
| `obsidian-orphan-auditor` | 孤儿页审计 | 勿重复 |
| `obsidian-content-hotspot` | 引用数 × 空置率 内容缺口 | 勿重复 |
| `obsidian-section-filler` / `obsidian-backlink-completer` / `obsidian-rename` / `obsidian-note-scaffolder` / `obsidian-entry-register` / `obsidian-notes-to-entry` | 各类原子维护动作 | 编排时调用 |
| `obsidian-timeline-checker` | 年份/年龄/占位符时间线矛盾 | 勿重复 |

## 外部镜像 / 运维元文档（本次构建）
| skill | 能力 | 状态 |
|-------|------|------|
| `lexiang-vault-sync` | vault → 腾讯乐享单向镜像同步（传输层真空） | **新建** |
| `vault-ops-handoff` | 生成 HANDOFF/CHECK/SKILLBUILD 运维元文档 | **新建（原为空占位）** |
| `obsidian-vault-doctor`（增强） | 合并原 cjk-glyph-guard 微 skill + 3 新探测器 | **增强已有** |

## 去重结论
- 只读体检已饱和 → 新 skill 一律**调用**而非重写。
- 真空仅在：①外部镜像传输层（lexiang-vault-sync）②运维元文档生成（vault-ops-handoff）。
- 微 skill（如 cjk-glyph-guard）应作为 `references/` 资产合并进 doctor，不独立成 skill。
