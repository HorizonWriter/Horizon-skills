---
name: vault-patrol
description: >-
  worldbuilding vault 定期巡检 + 网盘分发 SOP。把"清临时文件 → 刷新 5 份元文档
  (AGENT/HANDOFF/CHECK/SKILLBUILD/SKILL) → 下载网盘原有世界观去重(本地结构不变) →
  打包 世界观(含故事列表)+skill 单 zip → 上传网盘根目录覆盖 → 生成转接 JSON"
  整套动作固化为一条可复跑命令。
  当用户说"巡检""打包分发""巡检skill""清临时文件打包""维护 vault 并投递网盘"
  "生成交接 JSON""vault-patrol""定期巡检"时触发。
  vault 根：`/workspace/世界观`（git 仓库）；skill 根：`/workspace/skills`（git 仓库）；
  网盘根 dir_id：`SkzlugcQcTgO`。
agent_created: true
---

# vault-patrol — worldbuilding vault 巡检 / 分发 skill

> 一句话：vault 的"版本发布 + 交接快照"流水线。每次巡检 = 一次「vault 版本更新」。
> 本 skill 沉淀自 2026-08-18 多轮手工巡检，固化所有踩过的坑。

---

## 0. 触发与边界

| 你说 | 本 skill 做什么 |
|------|----------------|
| "巡检" / "vault-patrol" / "定期巡检" | 跑完整流水线（§1 → §6）|
| "打包分发" / "清临时文件打包" | 跳过元文档刷新，直奔去重+打包+上传 |
| "生成交接 JSON" | 仅做 §6 转接快照（前置需本地状态已最新）|
| "刷新元文档" | 仅做 §2（AGENT/HANDOFF/CHECK/SKILLBUILD/SKILL）|

**前置**：两个 git 仓库工作区干净或变更已 intent 明确；网盘 MCP（`tdrive.*`）可用。
**不可逆操作**：网盘删除/覆盖、本地 `rm`、git commit —— 均按 §7.2 确认或复核。

---

## 1. 清临时文件（staging 层，必须最先做）

```bash
rm -rf /tmp/pkg* /tmp/staging /tmp/restore /tmp/upload*.py /tmp/*.json
# 本地历史归档（非交付物）可清：/workspace/世界观-*.tar / 旧版 *_pkg/ —— 清前先 dir_list 核对网盘已有备份
```
- 临时文件指：`/tmp` 下的解包 staging、Python 上传脚本、下载缓存。
- **不要**删 `/workspace/世界观` 内的内容（除非用户明确要清历史 tar）。
- **不要**用 `rm -rf *-perspective` 这类通配符（见 §7.3 坑）。

---

## 2. 刷新 5 份元文档（内容层，给零上下文新会话看）

> 数字一律现场实测，禁止引用上一轮 summary 记忆值。

### 2.1 AGENT.md（架构 + 项目关联分析）
- 套用 `AGENTS.md` 10 节软件模板（保留 §5 编码规范、§7 AI 代理行为规则）。
- 新增 **§11 档案库架构扫描与项目关联分析**：
  1. **扫描**：md 总数（全量 vs 内容层口径）、图片/音频数、_scenes 篇数、板块数、两个 git HEAD。
  2. **项目三层定义**：长期（vault=SSOT）/ 中期（工具化与衍生内容工程）/ 短期（本批扩充）。
  3. **联系**：当前会话 ↔ 各项目，识别存档信息/观点如何推进项目。
  4. **可复用洞察**：跨 IP 改编 SOP、云端数字生命落点、印象曲载入 SOP、网盘分发 SOP、来源登记 SOP、五条底线过滤器、K22 登记法则、巡检即版本更新、主代理 Bash 委外、网盘 .tar 凭证 bug。

### 2.2 HANDOFF.md（零上下文交接）
- §0 定位 → §1 我们在做什么（含五条底线）→ §2 完成了什么（表+证据 commit）→ §3 卡在哪 → §4 下一步 → §5 踩过的坑 → §6 入口速查。
- 坑清单必须含：cd 前缀被吞、附件本地副本在 /root/uploads、网盘根 ID 非字面 root、上传签名失效、删除限流静默失败、overwrite 不真覆盖、跨 IP 改编 SOP、别信 summary 数字、一致性 H1 误报、元文档示例嵌入、新概念须登记、音频 doctor 误报 dead、**主代理 Bash 故障委外**。

### 2.3 CHECK.md（obsidian 合规体检 + 盲点）
- 跑 `obsidian-vault-doctor/doctor.py` 出链接层（dead/dotdot/mdsuffix/pipe_unesc/missing_fm/escaped_embed）。
- 跑 `obsidian-consistency-checker` 出一致性（注意 H1 正则误报）。
- 列不合理之处 + 不符合 Obsidian 规范处 + **盲点**（你没注意但值得注意）：授权字段缺失、印象曲 frontmatter 缺口、体检"全绿"欺骗性、孤儿图假阴性。
- 标注每轮真实修复（如总览 `|` 转义、LR-world 清理、perspective 合并）。

### 2.4 SKILLBUILD.md（去重优化的 skill 提案）
- §0 现有生态扫描（去重前提）→ §1-§4 待建 skill 提案（worldview-canon-guard / vault-asset-importer / skill-ecosystem-auditor / vault-to-notion-syncer）→ §5 合并方案 → §6 已建成范例 → §7 落地建议 → §8 vault-patrol（本轮）。

### 2.5 SKILL.md（统一入口）
- §0 生态总览（5 族）→ §1 触发词路由 → §2 创意族 → §3 合并状态 → §4 失效警示 → §5 入口。
- 每次 skill 增删/合并后必须同步本文件。

---

## 3. 下载网盘原有世界观去重（保持本地结构不变）

> 目的：把网盘历史独有内容并入新包，本地 `/workspace/世界观` 结构一律不改。

```bash
# 1. dir_list 根目录，定位"合并去重包-YYYYMMDD.zip"（可正常下载的旧版，约 220 md / 42 图）
# 2. tdrive.file_download 取 URL → 立即 curl 落盘（.zip 凭证有效，.tar/.gz 返回 InvalidAccessKeyId）
# 3. 解包到 /tmp/old_worldview
# 4. 内容级去重：旧版独有文件 = 本地不存在的文件（零内容冲突则并入）
#    _scenes 由本地 13 篇 → 并入网盘独有 77 篇 = 90 篇（仅进包，不写回本地）
```

- **仅 `.zip` 可靠下载**（网盘对 `.gz`/`.tar` 下载凭证有系统性 `InvalidAccessKeyId` bug）。
- 旧 `世界观.tar`（`SvQKAhjGnlSg`）凭证已损坏，改用根目录 `.zip` 交付物作旧版来源。
- 去重结论必须记录：旧版独有文件数、是否零冲突、_scenes 最终篇数。

---

## 4. 打包 世界观（含故事列表）+ skill 单 zip

```bash
rm -rf /tmp/pkg && mkdir -p /tmp/pkg/skills
cd /tmp/pkg
unzip -q <本地交付物zip> "世界观/*"        # 复用上轮去重结果（含 90 篇 _scenes）
# 用新版 /workspace/世界观 覆盖（含本次新增内容）：
cp -r /workspace/世界观/. 世界观/  && rm -rf 世界观/.git 世界观/.trash
# 并入 skill（排除 .git）：
for d in $(find /workspace/skills -maxdepth 1 -mindepth 1 -type d ! -name '.git'); do
  cp -r "$d" skills/; done
cp -r ~/.codebuddy/skills/impression-song-crafter skills/
find /tmp/pkg -name __pycache__ -type d -exec rm -rf {} + ; find /tmp/pkg -name '*.pyc' -delete
zip -rq /workspace/<vault-name>-含故事列表+skills-<日期>.zip 世界观 skills
```
- 顶层必须为 `世界观/` + `skills/`；排除 `.git`/`.trash`/`__pycache__`/`.DS_Store`。
- 命名规范：`<vault-name>-含故事列表+skills-YYYYMMDD.zip`；示例：`<vault-name>`=玄机城世界观
  时为 `玄机城世界观-含故事列表+skills-20260824.zip`。

---

## 5. 上传网盘根目录覆盖（不可逆，先 dir_list 复核）

```
1. dir_list 根目录，确认旧交付物 file_id 当前存在
2. tdrive.file_delete(旧 file_id)        # 拿 trace_id，稍后复核
3. tdrive.file_upload(dir_id=SkzlugcQcTgO, file_name, file_size, conflict_strategy="rename")
   → 返回 upload_url + 超长签名头 + confirm_key + task_id
4. Python 脚本文件精确传参 curl PUT upload_url（不要内联超长 token 到 shell）
   → 发送全部字节，确认 HTTP 200
5. tdrive.file_upload_complete(confirm_key/task_id/dir_id/file_name/file_size)
   → 返回新 file_id
6. dir_list 根目录复核：旧 file_id 不在、新文件就位、size 一致
```
- **网盘根 ID = `SkzlugcQcTgO`**（不是字面量 `root`）。
- 上传后务必 `dir_list` 复核（删除可能静默失败）。
- 两个 git 仓库各自 `git add -A && git commit`（commit 需用户确认）。

---

## 6. 生成转接 JSON 快照

写 `/workspace/agent_handoff_<YYYYMMDD>.json`：
```json
{
  "handoff_metadata": { "generated_at","agent","vault_head","purpose" },
  "vault_state": { "path_local","is_git_repo","git_head","git_status","content_files","story_list","top_level_dirs","meta_docs" },
  "five_unbreakable_settings": [...5 条...],
  "netdrive": { "root_dir_id","deliverable_root":{name,file_id,size_bytes,contains,note} },
  "meta_docs_refreshed_this_session": {...},
  "skills": {...},
  "key_conclusions": { "ip_risk","dedup_merge_result","k22_canonical" },
  "open_items": [...],
  "netdrive_sop_notes": [...]
}
```
- 用 `python3 -c "import json; json.load(open(...))"` 校验合法。
- 同步 `netdrive.deliverable_root.file_id` / `size_bytes` 为新上传值。

---

## 7. 已知坑（巡检必读）⚠️

### 7.1 网盘 `.gz`/`.tar` 凭证系统性损坏
下载旧 `世界观.tar` 返回 `InvalidAccessKeyId`；**仅 `.zip` 可正常下载与上载**。投递一律 `.zip`。

### 7.2 上传签名失效（超长 token）
内联 `curl` 传超长安全令牌会被 shell 干扰报 `SignatureDoesNotMatch`/`InvalidAccessKeyId`。
**做法**：把凭证写进 Python 脚本文件（如 `/tmp/upload.py`），用变量传参 `bash upload.py` 精确 PUT；`file_upload` 取凭证后**紧接** PUT，隔多轮次会过期。

### 7.3 `rm` 通配符误删 🔴
`rm -rf *-perspective` 会把刚建的 `role-perspective` 也删掉。合并后用
`find . -maxdepth 1 -type d -name '*-perspective' ! -name 'role-perspective' -exec rm -rf {} +` 精确排除。

### 7.4 主代理 Bash 故障 → 委外
主代理 `Bash` 偶发 `command undefined`（环境层故障）。所有 shell 重活
（扫描/打包/上传/Python PUT）委派 `general-purpose` 子代理（其 Bash 独立可用）；
主代理负责 Read/Write/Edit 文档 + netdrive MCP 复核。

### 7.5 删除静默失败
`file_delete` 批量限流，有时返回 `trace_id` 却未真删。**删后必 `dir_list` 复核**。

### 7.6 别信 summary 里的数字
所有 md/图/音频计数现场跑脚本重出（曾 148→180、3→4 音频）。

---

## 8. 退出标准
- [ ] 临时文件已清
- [ ] 5 份元文档刷新且 HEAD 同步
- [ ] 网盘去重完成（本地结构不变，_scenes 90 篇）
- [ ] zip 生成（顶层 世界观/ + skills/，无 .git）
- [ ] 网盘根目录新文件就位 + dir_list 复核通过
- [ ] 转接 JSON 校验通过 + file_id 同步
- [ ] 两个 git 仓库已提交
