# Horizon Skills

从 worldbuilding（世界观构建）项目实践中沉淀出的**通用 skill 合集**：一组 Obsidian vault 内容工具链 + 角色/创作类 skill。每个子目录是一个独立 skill，以 `SKILL.md` 为入口，可直接安装到支持 Agent Skills 的环境中，或按文档手动调用其中的脚本。

所有工具均为通用实现——不绑定任何特定世界观项目；板块类型、索引页、纪年正则等均可通过环境变量或模板注册表配置。

## 技能列表

### Obsidian Vault 工具链

围绕「标准条目格式」（H1 标题 + 基本档案表格 + 关联板块段落）与「vault 根相对 wikilink」两个核心约定构建，互相配合覆盖内容生产全流程：

| Skill | 读/写 | 用途 |
|-------|-------|------|
| [obsidian-note-scaffolder](obsidian-note-scaffolder/) | 写 | 新建规范条目：自动 H1 + 档案表格 + 关联板块，链接全部根相对、表格内管道正确转义 |
| [obsidian-template-scaffolder](obsidian-template-scaffolder/) | 写 | 基于 14 种板块创作提示词模板生成条目（角色/组织/种族/科技/地理/事件/历史/物品/文化/生物/疾病/军事/系统/世界概要），嵌入 AI 创作指南 |
| [obsidian-backlink-completer](obsidian-backlink-completer/) | 写 | 检测 A→B 单向引用，自动补全 B→A 回链 |
| [obsidian-rename](obsidian-rename/) | 写 | 重命名文件并全库更新 wikilink 引用，保持原链接形式 |
| [obsidian-entry-register](obsidian-entry-register/) | 写 | 新条目自动注册到板块总览页、相关文件关联板块、全局索引 |
| [obsidian-notes-to-entry](obsidian-notes-to-entry/) | 写 | 非标准笔记 → 标准条目格式转换，保留原始正文 |
| [obsidian-section-filler](obsidian-section-filler/) | 写 | 扫描空/迷你/待补充文件，可选生成标准骨架 |
| [obsidian-content-hotspot](obsidian-content-hotspot/) | 只读 | 「被引用最多但内容最空」排名，输出优先写作队列 |
| [obsidian-consistency-checker](obsidian-consistency-checker/) | 只读 | 一致性扫描：死链、孤页、重复段落、概念值冲突等 |
| [obsidian-orphan-auditor](obsidian-orphan-auditor/) | 只读 | 索引/总览完整性审计：缺条目、孤立链接、重复索引/文件 |
| [obsidian-timeline-checker](obsidian-timeline-checker/) | 只读 | 时间线矛盾检测：时间引用、年龄线索跨文件交叉对比 |
| [obsidian-vault-doctor](obsidian-vault-doctor/) | 诊断+修复 | 链接点不开/表格被打散类问题体检修复：相对路径、管道转义、死链、转义嵌入、CJK 近形字码点校验 |

### 共享库

- **[shared-vault-lib](shared-vault-lib/)** — 上述工具共用的 Python 库（`libvault.py`）：vault 根定位（`VAULT_PATH` 环境变量 / 向上探测 `.obsidian` / cwd 回退）、wikilink 解析（含表格内 `\|` 转义）、文件读写。

### 创作与运维

| Skill | 用途 |
|-------|------|
| [role-perspective](role-perspective/) | 角色视角扮演框架：persona 文件放入 `references/{slug}.md` 即可以第一人称扮演任意角色分析问题。内置 24 个示例 persona（来自作者的凌日星世界观项目，仅作格式示例，可整体替换） |
| [impression-song-crafter](impression-song-crafter/) | 角色卡 → SUNO 就绪的印象曲素材：音乐风格 prompt + 去除 AI 腔的押韵歌词 |
| [vault-patrol](vault-patrol/) | vault 定期巡检 + 打包分发 SOP：清临时文件 → 刷新元文档 → 去重 → 单 zip 分发，固化为一条可复跑命令 |
| [vault-ops-handoff](vault-ops-handoff/) | 生成运维交接 / 仓库体检 / 构建类元文档（HANDOFF.md / CHECK.md / SKILLBUILD.md），结论必须附实测证据 |

## 快速上手

```bash
# 例：列出脚手架支持的 14 种板块类型
python obsidian-template-scaffolder/scripts/scaffold.py --list-types

# 例：为你的 vault 创建一个角色条目
python obsidian-template-scaffolder/scripts/scaffold.py /path/to/vault 角色 --name 林夕 --fields "org=玄机城"

# 例：检测时间线矛盾（自定义纪年）
ERA_PATTERN="新历[前]?约?(\d+)年" python obsidian-timeline-checker/checker.py /path/to/vault

# 运行测试
cd shared-vault-lib && python -m pytest ../tests -q
```

常用环境变量：

| 变量 | Skill | 说明 |
|------|-------|------|
| `VAULT_PATH` | shared-vault-lib 系列 | 显式指定 vault 根目录 |
| `ERA_PATTERN` | timeline-checker | 追加自定义纪年正则 |
| `INDEX_MAP` / `INDEX_FILE` / `LINK_SECTION` | entry-register | 板块→总览页映射、全局索引、关联板块段标题 |
| `ENTRY_FIELDS` | notes-to-entry | 标准条目的档案字段集 |

## License

见 [LICENSE](LICENSE)。
