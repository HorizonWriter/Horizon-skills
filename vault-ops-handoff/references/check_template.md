# CHECK — worldbuilding vault 仓库体检报告

> 基于**实测脚本**（`obsidian-vault-doctor/doctor.py` + `vault-ops-handoff/snapshot_audit.py`），非记忆。
> 被测对象：`{{VAULT}}`，共 **{{TOTAL_MD}}** 个 `.md`。
> 体检时间：{{DATE}}（git HEAD `{{HEAD}}`）。

## 0. 实测结果速览
| 维度 | 实测值 | 判定 |
|------|--------|------|
| 真死链 | {{dead}} | {{verdict}} |
| 转义嵌入 `\![[` | {{escaped}} | {{verdict}} |
| 缺 frontmatter（内容条目）| {{missing_fm}} | {{verdict}} |
| CJK 近形字 | {{cjk}} | {{verdict}} |

## 1. 不合理之处（应修复的真实问题）
{{逐条：文件 / 行 / 影响 / 修复}}

## 2. 不符合 Obsidian 标准 / 维护规范之处
{{列表}}

## 3. 盲点（你没注意但值得注意）
{{列表}}

## 4. 与上一轮 summary 的差异（以本次实测为准）
{{纠正表}}

## 5. 优先级与建议动作
| 优先级 | 动作 | 负责方 |
|--------|------|--------|
| {{P}} | {{action}} | {{owner}} |

## 附录：可复现脚本
- `python3 /workspace/skills/obsidian-vault-doctor/doctor.py {{VAULT}}`
- `python3 /workspace/skills/vault-ops-handoff/scripts/snapshot_audit.py {{VAULT}}`
