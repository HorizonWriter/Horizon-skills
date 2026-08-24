#!/usr/bin/env python3
# anti_slop_zh.py — 中文歌词「去 AI 味」启发式检查器
#
# 对应 woosal1337 的 ste-lint.py，但针对中文歌词场景。
# 机械可检的 AI-slop 信号: 空泛形容词、抽象名词堆砌、廉价比喻、
# 万能过渡、模态堆叠、名词化/复合动词、「的」堆叠、排比「在」堆叠、说教结尾。
#
# 分数 = 每 100 中文字符的违规数，越低越干净。
#   目标 < 2.5 可直接进 SUNO；2.5–5.0 偏味；> 5.0 明显 slop。
#
# 用法:
#   python3 anti_slop_zh.py lyrics.md
#   python3 anti_slop_zh.py lyrics.md --json
#   python3 anti_slop_zh.py lyrics.md --fail-over 2.5   # CI / 钩子: 超标 exit 1
# 也可从 stdin 读:  cat lyrics.md | python3 anti_slop_zh.py -

import sys
import re
import json

# ---- 触发词表（按类别）----
TRIGGERS = {
    "空泛形容词": ["无尽", "永恒", "璀璨", "绚烂", "美妙", "震撼", "无与伦比",
                  "绝美", "极致", "完美", "动人的", "唯美"],
    "抽象名词堆砌": ["岁月", "时光", "光阴", "流年", "灵魂", "心灵", "梦境",
                  "远方", "彼岸", "宇宙"],
    "廉价比喻": ["仿佛", "如同", "好像", "宛若", "好似", "犹如", "宛然"],
    "万能过渡": ["然而", "于是", "或许", "终究", "话说回来", "不得不说",
              "总而言之", "可见", "话说"],
    "模态堆叠": ["可能会", "应该是", "似乎是", "仿佛在", "好像要", "将会",
              "或许会", "似乎要", "仿佛要"],
    "名词化/复合动词": ["进行了", "做出", "绽放出", "涌现出", "流淌着",
                    "闪烁着", "升腾起", "萦绕着", "展现出了", "勾勒出", "诉说着"],
}

# 结构性启发（按行判断，命中整行记 1 次）
DE_STACK_THRESHOLD = 3      # 一行「的」超此数
ZAI_STACK_THRESHOLD = 3     # 一行「在」超此数（排比堆砌）
PREACHY = re.compile(r"(所以我们|这就是|只要.{0,6}就|让我们|不得不说)")

TAG_RE = re.compile(r"^\s*\[[^\]]+\]\s*$")   # [Verse] 等段落标签
CN_RE = re.compile(r"[\u4e00-\u9fff]")


def count_cn(text: str) -> int:
    return len(CN_RE.findall(text))


def lint(text: str):
    lines = text.splitlines()
    hits = []           # (line_no, category, matched)
    cat_counts = {}
    cn_total = 0

    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or TAG_RE.match(line):
            continue
        cn_total += count_cn(line)

        # 词表类
        for cat, words in TRIGGERS.items():
            for w in words:
                if w in line:
                    hits.append((i, cat, w))
                    cat_counts[cat] = cat_counts.get(cat, 0) + 1

        # 「的」堆叠
        de = line.count("的")
        if de > DE_STACK_THRESHOLD:
            hits.append((i, "的堆叠", f"{de}×的"))
            cat_counts["的堆叠"] = cat_counts.get("的堆叠", 0) + 1

        # 「在」排比堆砌
        zai = line.count("在")
        if zai >= ZAI_STACK_THRESHOLD:
            hits.append((i, "排比/在堆叠", f"{zai}×在"))
            cat_counts["排比/在堆叠"] = cat_counts.get("排比/在堆叠", 0) + 1

        # 说教结尾
        if PREACHY.search(line):
            hits.append((i, "说教结尾", PREACHY.search(line).group(1)))
            cat_counts["说教结尾"] = cat_counts.get("说教结尾", 0) + 1

    total = sum(cat_counts.values())
    score = round(total / cn_total * 100, 2) if cn_total else 0.0
    return {
        "cn_chars": cn_total,
        "violations": total,
        "score_per_100": score,
        "category_counts": cat_counts,
        "hits": hits,
    }


def main():
    args = sys.argv[1:]
    fail_over = None
    as_json = False
    path = None

    for a in args:
        if a == "--json":
            as_json = True
        elif a.startswith("--fail-over"):
            fail_over = float(a.split("=", 1)[1]) if "=" in a else None
        elif a == "-":
            path = "-"
        elif not a.startswith("-"):
            path = a

    if path == "-":
        text = sys.stdin.read()
    elif path:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    else:
        print("用法: anti_slop_zh.py <lyrics.md|-> [--json] [--fail-over N]")
        sys.exit(2)

    r = lint(text)

    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(0 if not fail_over or r["score_per_100"] <= fail_over else 1)

    print(f"anti_slop_zh · 中文字符: {r['cn_chars']} · 违规: {r['violations']} · "
          f"分数: {r['score_per_100']} / 100 字 (目标 < 2.5)")
    if r["category_counts"]:
        print("-- 按类别 --")
        for cat, n in sorted(r["category_counts"].items(), key=lambda x: -x[1]):
            print(f"  {cat}: {n}")
        print("-- 命中行 --")
        for ln, cat, m in r["hits"]:
            print(f"  L{ln} [{cat}] {m}")
    else:
        print("未发现 AI 味信号。")

    if fail_over is not None and r["score_per_100"] > fail_over:
        sys.exit(1)


if __name__ == "__main__":
    main()
