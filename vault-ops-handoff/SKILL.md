---
name: vault-ops-handoff
description: >-
  为凌日星 vault 仓库生成运维交接 / 检查 / 构建类元文档
  （HANDOFF.md / CHECK.md / SKILLBUILD.md）。当用户说"写交接文档"
  "生成仓库体检""构建 skill 描述""沉淀运维文档""给我一份 handoff"时触发。
  基于当前 git 状态、实测体检脚本输出与现有 skill 生态，产出面向零上下文新会话的可接手文档。
  所有结论必须附实测证据，禁止凭记忆。
agent_created: true
---

# vault 运维文档生成器（vault-ops-handoff）

把"交接 / 体检 / 构建"三类运维元文档的生成固化为一键产出，避免每轮手搓且口径漂移。
与 `obsidian-vault-doctor`（体检执行）配合：doctor 出数据，本 skill 出文档。

## 输入 / 输出
- **输入**：vault 根目录、git 仓库、`/workspace/skills/` 列表
- **输出**：`HANDOFF.md`（在做什么/完成/卡住/下一步/坑）、`CHECK.md`（实测体检+盲点）、`SKILLBUILD.md`（去重后的 skill 方案）

## 工作流（命令式）
1. `cd <vault> && git log --oneline -10` + `git status` → 提取"完成了什么 / 卡在哪"。
2. 跑 `scripts/snapshot_audit.py <vault>` → 产出实测 JSON（转义嵌入 / 缺 frontmatter / 死链 / 近形字）。
3. `ls /workspace/skills/` → 生成现有 skill 生态表（用于 SKILLBUILD 去重，见 `assets/skill_catalog.md`）。
4. 按 `references/*.md` 三模板渲染三文档，**所有结论附实测证据**，禁止凭记忆。
5. 写出三文档到 vault 根目录（与 `AGENT.md` 同级），提示是否 `git add`。

## 关键纪律（来自踩坑）
- **绝不脑补设定**：vault 无依据时明示"未提供"，绝不编造；5 条不可推翻底线冲突时保设定弃新内容。
- **实测优先**：数字来自 `snapshot_audit.py` 而非记忆；若与上一轮 summary 冲突，以本次实测为准。
- **去重**：SKILLBUILD 提案前必须扫 `/workspace/skills/` 现有 skill，避免重复（本轮即发现
  `obsidian-vault-doctor` 与 `vault-ops-handoff` 已存在，应合并增强而非新建）。

## 文件结构
```
vault-ops-handoff/
├── SKILL.md
├── scripts/
│   └── snapshot_audit.py        # 实测体检聚合（可独立运行）
├── references/
│   ├── handoff_template.md      # HANDOFF 模板
│   ├── check_template.md        # CHECK 模板
│   └── skillbuild_template.md   # SKILLBUILD 模板
└── assets/
    └── skill_catalog.md         # 现有 skill 速查（去重用）
```
