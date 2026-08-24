---
name: ste-writing
description: Rewrite prose (docs, READMEs, PR descriptions, error messages, release notes, comments — never code) into ASD-STE100 Simplified Technical English to remove "AI slop". Use when asked to make writing not sound like AI, make docs clear or plain, enforce a controlled writing style, or write technical documentation that reads human. Two modes — strict (procedures/safety) and STE-flavored (general prose).
agent_created: true
---

# ste-writing

Write prose in ASD-STE100 Simplified Technical English. This applies to documentation, READMEs, pull-request text, error messages, release notes, and comments. It does not apply to code, identifiers, or command syntax. It is not for marketing copy, essays, or anything that needs a voice — STE strips voice on purpose.

> 中文撰写规范见下方「中文规范（中文 vault 落地）」一节，按本英文规范的同款骨架组织，直接并入本文件，不另立文档。原版英文规则为权威；中文节是其等效映射 + vault 特定补充。

## Rules

WORDS
- Use one name for one thing. Do not call the same item by two different names.
- Use the short common word: start (not begin/commence/initiate), use (not utilize/leverage), help (not facilitate), make sure (not ensure), before (not prior to), after (not subsequent to), about (not regarding/concerning), get (not obtain/acquire), show (not demonstrate), also (not additionally/furthermore/moreover).
- Give each word one meaning. "fall" means to move down, not to decrease.
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, world-class, next-generation, revolutionary.
- American spelling.

VERBS
- Active voice. "the parser reads the file", not "the file is read by the parser".
- Use a verb for an action. "analyze the log", not "perform an analysis of the log".
- No stacked auxiliaries. Not "it is important to note that this may help to improve". Write "this improves X".
- No "-ing" main verb where a simple tense works.

SENTENCES
- One instruction per sentence. Max 20 words (instruction), max 25 (descriptive).
- No contractions. Use articles: a, an, the, this, these.

PUNCTUATION
- No semicolons. Write two sentences. (Note: the em dash is not banned by STE, only the semicolon is — add "no em dash" yourself if you want it gone.)

STRUCTURE
- One topic per paragraph, max six sentences. For steps, use a numbered vertical list, one action per item, imperative form. Put a condition before its command.

Write only the requested text. No preamble, no summary, no closing remarks.

## Modes

- **strict** — procedures, runbooks, safety text, error messages: apply every rule and both length caps.
- **STE-flavored** — general prose (READMEs, PR descriptions, docs): apply the sentence, paragraph, active-voice, and no-phrasal-verb discipline; relax the ~900-word dictionary lockdown so the text keeps enough range to read naturally.

## Self-lint (run before returning text)

1. Any sentence over 20 words? Split it.
2. Any semicolon? Replace with a period.
3. Any contraction? Expand it.
4. Any passive voice with a known actor? Make it active.
5. Any "-ing" main verb, nominalization ("perform an analysis"), or phrasal verb ("spin up")? Replace with a plain verb.
6. Same thing named two ways? Pick one name.

The mechanical rules above are lintable and are what removes slop. Full STE also needs human judgment (the right technical noun, whether a sentence "makes good sense") — a checker cannot certify that, and slop is not about that. This skill fixes the FORM of slop. It cannot make a hollow paragraph true.

Free official standard (do not paste it in full; it is copyrighted): https://asd-ste100.org

## 工具：ste-lint.py（启发式 anti-slop 检查器）

确定性 linter，覆盖 STE 中机器可检的子集。打分 = 每 100 词违规数（越低越干净）。

```bash
python3 ste-lint.py your-draft.md        # 检查单个文件
python3 ste-lint.py *.md                  # 批量（支持 glob）
cat draft.md | python3 ste-lint.py        # 从 stdin
```

用法信号：先 lint 草稿 → 应用本 skill 改写 → 再 lint 一次，**两次分差（delta）**就是改写生效的证据。

---

# 中文规范（中文 vault 落地）

> 适用：凌日星世界观 vault 的中文条目撰写与润色。STE 治「AI 废话」的**形式**——空洞用词、长句、被动、堆叠副词；它不能让无设定依据的段落变真实（绝不脑补设定，见 vault 铁律）。
> 本节按英文规范同款骨架组织。英文规则中无中文对应的项（美式拼写、英文缩写）标注「中文无对应」；中文特有问题（长破折号、营销词堆砌）在此补齐。

## 规则

用词
- **一物一名**：同一概念全库只用一词。例：摩晶工业勿混用「摩尔晶工业」「晶工」。名字打架是 vault 一致性头号坑。
- **用短常用词**：用「使用」非「利用/借助/运用」；用「帮助」非「助力/赋能」；用「开始」非「着手/启动」；用「关于」非「就……而言/针对……方面」。
- **一词一义**：例：「下降」只表数值变小，勿兼表恶化/衰减/退化，需要时换词。
- **禁营销形容词（重点）**：无缝、强大、革命性、一站式、赋能、颠覆、业界领先、极致、丝滑、开箱即用、下一代、世界级。设定条目里零信息量，且是 AI 生成强信号。
- **美式拼写**：中文无对应，忽略。

动词
- **主动语态**：「系统读取文件」非「文件被系统读取」。设定说明、操作步骤用主动。
- **用动词表动作**：「分析日志」非「对日志进行分析」；「检查连接」非「执行连接的检查」。
- **禁堆叠助动词**：勿写「值得注意的是，这可能会有助于改善……」，写「这改善了 X」。
- **勿拖沓进行体**：中文对应「正在……」式冗长，能直说就直说。

句子
- **一句一指令**。操作类每句一个动作。
- **限长**：指令句 ≤ 35 字，描述句 ≤ 45 字（对应英文 20/25 词）。长句是 vault 最隐蔽的废话温床。
- **禁缩略**：中文无英文 contractions，忽略；但**禁「等/等等」含糊收尾**——能列全则列全，不能则写明范围。

标点
- **禁长破折号（——）**：中文 AI 废话头号标记（对应英文 em dash）。原版 STE 只禁分号，vault 显式追加「禁 ——」，多拆两句或改冒号/逗号。
- **慎用分号（；）**：能拆两句就拆。
- 其余中文标点（书名号、顿号等）按规范。

结构
- **一段一主题，≤ 6 句**。
- 操作步骤用**竖排编号列表**，每项规定一个动作，祈使句；**条件在前、命令在后**：先「若 X 成立」，再「执行 Y」。

只写被要求的文本。不写开场白、不写总结、不写收尾客套。

## 模式

- **strict（严格）**——操作步骤、安全须知、报错说明、适用范围声明、铁律条目：每条规则 + 限长全开。
- **STE-flavored（风味）**——角色卡、组织档案、地点条目、设定说明等一般散文：开句子/段落/主动/禁短语动词；放宽用词锁定，保留自然语感。
- 对话、剧情正文、需要「声音/风格」的文学创作**不适用 STE**——STE 会刻意抹掉文风。

## 中文自检（提交前逐条过）

1. 同一概念全库是否只用一个名字？
2. 是否出现长破折号「——」？拆成两句或改冒号。
3. 是否出现营销形容词（无缝/赋能/革命性/一站式…）？删。
4. 有无 > 35 字（指令）/ > 45 字（描述）长句？拆。
5. 有无被动堆叠（「被……所……」、拖沓「正在……」）？转主动。
6. 段落是否一段一主题、≤ 6 句？
7. 步骤是否编号竖排、每项规定一个动作、条件在前？

## 🔴 已知局限（务必知道，否则误判）

- **`ste-lint.py` 只检英文**：正则仅匹配拉丁字母（`[A-Za-z0-9]`），对中文**完全不报错**（纯中文 `words=0, total=0` 是「没检」不是「干净」）。中文质量靠本节人工自查；如需机检，须另写中文 linter。
- **破折号计数**：linter 的 em-dash 项只认英文 `—`/`–`，不认中文全角「——」；中文破折号需人工数。
- **linter 是启发式、非认证 STE 检查器**：判定规则（正确技术名词、句子是否「讲得通」）需人；linter 只覆盖机器可检子集。
- **`run-openai.py` 依赖包外 `sys_*.md`/`prompts.json`**，单独安装后跑不通，仅作来源可追溯保留。

## 与 vault 铁律的关系

STE 管「怎么说」，5 条不可推翻设定（人类社会性灭绝 / 意识提取不可逆 / 数字生命不患晶化疾病 / 摩晶科技体系 / 云朵小镇与物理层完全隔离）管「什么能说」。STE 绝不可为通顺弱化或改写铁律表述；冲突时保设定弃新内容。亚人族群风俗等「需要声音」的内容走 flavored 甚至不走 STE；技术设定、档案表说明走 strict。
