# SUNO 格式指南（印象曲输出规范）

本 skill 的产物最终粘贴进 **SUNO** 音乐生成软件。SUNO 有两个输入框：

1. **Style（风格提示词）**：一段自由文本，描述曲风、速度、情绪、乐器、人声、语言。
2. **Lyrics（歌词）**：带段落标签的歌词文本。

两部分分别填写，不要混在一起。

## 一、风格提示词（Style Prompt）写法

建议结构（顺序不强制，用逗号分隔）：

```
[流派] [子流派], [速度] BPM, [情绪], [乐器], [人声], [语言: 中文]
```

示例（适配星流纨这类高速角色）：

```
synthwave, energetic, 128 BPM, driving bass, bright synth arps, glitch percussion, female vocals, Chinese lyrics
```

要点：

- **流派要具体**：synthwave / J-pop / orchestral / lo-fi / industrial metal / city pop / 古风 / 国风电子。不要写「好听的」「燃的」。
- **情绪词**：epic / melancholic / uplifting / dark / playful / bittersweet。
- **乐器**：bass / synth / piano / strings / distorted guitar / choir；中文乐器可用「笛 / 古筝 / 二胡 / 编钟」。
- **人声**：male vocals / female vocals / breathy / powerful / whispered / harmonies / choir。
- **结构提示（可选）**：intro-build-drop、verse-chorus、no intro。
- **语言标注**：务必加 `Chinese lyrics`，否则 SUNO 可能按英文发音处理中文。
- 从角色卡提炼：高速→fast tempo / energetic；悲伤→minor key / melancholic；庄严→orchestral / epic。

## 二、歌词格式（Lyrics）

用方括号段落标签，每行标签独占一行：

```
[Intro] [Verse] [Pre-Chorus] [Chorus] [Bridge] [Breakdown] [Outro] [Instrumental]
```

规则：

- 每段标签独占一行，标签后换行开始歌词。
- 歌词每行一句，SUNO 按行自动断句；长句拆两行更可控。
- `[Instrumental]` 表示间奏（纯音乐，无词）。
- 重复段落：直接再写一次 `[Chorus]` + 歌词；或写 `(Repeat Chorus)`。
- **不要把演唱指示写进歌词**（如「大声唱」「渐弱」）——这些进 Style 框。

## 三、中文歌词押韵注意

- 相邻句尾字同韵。流行多押平声韵；副歌（Chorus）韵脚固定不换。
- 一行不要太长，避免发音模型断句错误。
- 避免生僻字影响发音。
- **韵脚必须载意**：为押韵硬凑「的 / 了 / 吧 / 啊」是高级 AI 味，见 `anti-ai-slop-zh.md` 第四节。

## 四、可直接粘贴模板

```
【Style 框】
synthwave, 128 BPM, energetic, driving bass, bright synth, female vocals, Chinese lyrics

【Lyrics 框】
[Intro]
(具体音色/环境白描，可无词)

[Verse]
(角色专属画面，一行一景)
(承接上一行，推进)

[Pre-Chorus]
(情绪抬升，为副歌蓄力)

[Chorus]
(押韵副歌，角色核心意象+信条，韵脚固定)
(重复强化)

[Verse 2]
(另一面/另一场景，仍用具体细节)

[Chorus]
(同副歌)

[Bridge]
(转折/独白式，可破韵制造张力)

[Outro]
(画面收尾，别说教)
```

## 五、常见翻车点

- Style 框写太笼统（「好听的中文歌」）→ SUNO 随机性爆炸。
- 歌词里夹演唱指示 → 被当歌词唱出来，出戏。
- 段落标签写错（用了圆括号或小写）→ SUNO 不识别。
- 中文没标 `Chinese lyrics` → 发音模型按英文念。
- 副歌韵脚飘 → 记忆点弱。
