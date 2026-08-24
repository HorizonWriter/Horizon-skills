---
name: impression-song-crafter
description: |-
  This skill should be used when the user wants to turn a character card (角色卡)
  — from the 凌日星 worldview vault or any character profile — into SUNO-ready
  song material: a music style prompt plus rhyming lyrics stripped of AI-slop.
  Trigger when the user asks for an 印象曲 / 角色曲 / theme song from a character
  entry, or wants lyrics that rhyme and read human rather than generic-AI. It
  extracts concrete details from the card, maps them to musical choices, and
  enforces Chinese anti-AI-slop rules (converted from woosal1337's STE method).
agent_created: true
---

# Impression Song Crafter（印象曲制作）

把角色卡变成可直接粘贴进 **SUNO** 的音乐素材：一段风格提示词 + 一首押韵、去 AI 味的歌词。

核心理念：**AI 味的解药是具体**。歌词必须锚定角色卡里的真实细节（冰蓝双马尾、离心力、计分板、柯伊伯带、自转一百圈），而不是「孤独的灵魂」「岁月的痕迹」这类可套任意角色的空话。

## When to use

- 用户给了角色卡路径 / 角色名 / 粘贴的角色卡文本，要「印象曲 / 角色歌 / 主题曲」。
- 用户要押韵歌词，且明确要求「别像 AI 写的」「去 AI 味」。
- 产物最终进 SUNO（风格框 + 歌词框两个输入框）。

## Inputs

接受三种输入之一：

1. **vault 路径**：如 `角色/星流纨.md` 或 `世界观/角色/星流纨.md`。从 vault 根目录定位。
2. **角色名**：在 vault 的 `角色/` 目录下按名查找条目。
3. **粘贴文本**：用户直接贴出角色卡内容。

## Workflow

### Step 1 · 读角色卡，抽具体素材

读取条目，结构化提取以下字段（只取**具体**信息，跳过泛泛描述）：

- **基本档案**：全名、种族、阵营、状态、核心标签（ESFP / 极速自旋 / 社交小太阳 等）。
- **视觉形象**：颜色、体型、标志性物件（冰蓝双马尾、无跟冰刀鞋、腰间光环、计分板）。
- **背景叙事**：关键事件、矛盾点（如「降频即解体」「曾搅碎主网数据流」）。
- **外貌与性格**：行为模式、信条（「慢下来会失去平衡，快起来才能保持优雅」）。
- **核心羁绊**：与其他角色的关系动词（绕星玄转一百圈、把星阋月整改令当背景音乐）。
- **独白金句**：可直接化用作歌词意象的原句。

> 把提取到的具体名词/动词列成「意象池」，写歌词时只从池里取，禁止从池外编造空词。

### Step 2 · 提炼音乐人格

把卡面特质映射到音乐选择，**每一项选择都要能回溯到卡里某条具体依据**：

| 角色特质 | 音乐映射 |
|---|---|
| 高速 / ESFP / 社交小太阳 | fast tempo (120–140 BPM)、energetic、bright |
| 悲伤 / 孤独 / 现存但游离 | minor key、melancholic、slow |
| 庄严 / 古老 / 组织 | orchestral、epic、choir |
| 数字生命 / 云端原生 | synthwave、glitch、electronic、arps |
| 战斗 / 治安官 / 对手 | industrial、driving bass、distorted |
| 考古 / 冷观 / 记录 | ambient、minimal、piano |

输出：genre、BPM、mood、key instruments、vocal style 各一项，并标注依据（来自哪条卡面信息）。

### Step 3 · 生成 SUNO 风格提示词

按 `references/suno-format-guide.md` 拼一行风格提示词：

```
[流派] [子流派], [速度] BPM, [情绪], [乐器], [人声], Chinese lyrics
```

末尾务必带 `Chinese lyrics`，否则 SUNO 按英文发音处理中文。

### Step 4 · 生成押韵歌词

按 `references/suno-format-guide.md` 的模板铺段落：`[Intro] [Verse] [Pre-Chorus] [Chorus] [Verse 2] [Chorus] [Bridge] [Outro]`。

写词时严格执行 `references/anti-ai-slop-zh.md`：

- 一行一画面，每行 ≤ 15 字，主语明确、主动语态。
- 只用简单时态，禁模态堆叠（可能会/似乎是/仿佛在）。
- 禁空泛形容词（无尽/永恒/璀璨/美妙）、抽象名词（岁月/灵魂/远方）、廉价比喻（仿佛/如同）。
- 禁「的」堆叠（一行 >3 个）、排比三连（「在…在…在…」）、万能过渡（然而/于是）、说教结尾。
- **押韵但必须载意**：邻句同韵，副歌韵脚固定；韵脚词要有信息量，不能为押韵硬凑「的/了/吧」。
- 全部意象取自 Step 1 的「意象池」，不用池外通用词。

**反例（AI 味）**：「无尽的岁月里／她仿佛在孤独中绽放出灵魂」
**正例（去味）**：「冰蓝双马尾甩成直线／第一百圈她还不停」

### Step 5 · 自检（必须执行）

用配套 linter 给歌词打分：

```
python3 scripts/anti_slop_zh.py lyrics.md          # 目标 < 2.5 / 100 字
python3 scripts/anti_slop_zh.py lyrics.md --json   # 机读
```

- 若分数 ≥ 2.5：按输出里的「命中行」和 `anti-ai-slop-zh.md` 的自检清单改对应行，**最多两轮**后复测。
- 复测通过（< 2.5）才进入交付；不要跳过 lint 直接声称「已去味」。

### Step 6 · 交付

给出两个**明确分开**的块，用户直接复制粘贴：

1. **Style 框内容**：Step 3 的风格提示词一行。
2. **Lyrics 框内容**：带段落标签的完整歌词。

并附一行 lint 最终分数。不要混填两个框，不要把演唱指示写进歌词。

## Resources

- `references/anti-ai-slop-zh.md` — 中文歌词去 AI 味规则（由 woosal1337 的 STE 方法转化，含自检清单与 STE 溯源表）。**写词与改词时必读。**
- `references/suno-format-guide.md` — SUNO 风格提示词与歌词格式、可直接粘贴模板、常见翻车点。
- `scripts/anti_slop_zh.py` — 中文歌词去 AI 味启发式检查器，输出每 100 字违规分；支持 `--json`、`--fail-over N`。

## Notes

- 本 skill 只负责「形式去味」：它保证歌词具体、主动、不堆空词，但无法替角色补足设定深度——若卡面本身单薄，先回 vault 补条目。
- 五条不可推翻设定是底线；若角色曲触及（如意识提取、社会性灭绝），歌词须与设定兼容，不新造冲突。
- 押韵与去味可能冲突时，**优先保具体意象**，再调韵；空韵比 AI 味更糟。
