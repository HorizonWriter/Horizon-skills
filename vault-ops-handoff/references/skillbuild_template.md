# SKILLBUILD — vault 运维 skill 构建方案

> 从对话历史提炼 skill 描述；原则：**去重**（不重复现有）、**优化**（更好则改进）。
> 构建标准：`SKILL.md` 含 `name`/`description`/`agent_created: true` frontmatter；
> 分层 `scripts/`（可执行）`references/`（按需加载）`assets/`（输出资源）；命令式写法。

## 0. 现有 skill 生态扫描（去重前提）
{{扫 /workspace/skills/，列表 + 约束}}

## 1. {{skill_name}}（新 / 优化）
```yaml
---
name: {{name}}
description: >-
  {{触发短语 + 职责}}
agent_created: true
---
```
### 背景 / 动机
### 输入 / 输出
### 工作流（命令式）
### 文件结构
### 护栏 / 已知坑
### 去重说明（与现有 skill 的关系）

## N. 落地建议
{{优先建哪个、复用哪些现有脚本}}
