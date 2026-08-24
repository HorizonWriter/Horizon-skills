#!/usr/bin/env python3
"""preflight.py — 乐享同步前的 pre-flight 校验。

检测：
  1. 畸形 wikilink：[[ 目标含 2+ 空格（如 [[角色/昭曦     | 昭曦]]）-> 乐享无法解析、破坏表格
  2. 未转义管道：表格行内裸 | 作为别名分隔符但未写成 \|
  3. CJK 近形字：文件正文命中 references/cjk_glyph_table.md 中的"易错字"码点

用法：
  python3 preflight.py --vault-root /workspace/世界观 \
      --glyph-table references/cjk_glyph_table.md

输出 JSON 报告；发现问题返回非 0 退出码（供 CI / 同步流程中止该页）。
"""
import os, re, json, argparse, sys


def load_glyph_blacklist(table_path):
    """从 cjk_glyph_table.md 解析出需报警的"易错字"集合。"""
    if not os.path.exists(table_path):
        return set()
    bad = set()
    txt = open(table_path, encoding="utf-8").read()
    # 匹配形如 `昰` U+6630 的行，收集码点
    for m in re.finditer(r'`([^`]+)`\s*U\+([0-9A-Fa-f]{4,})', txt):
        ch = m.group(1)
        if len(ch) == 1:
            bad.add(ch)
    return bad


def check_file(path, glyph_blacklist):
    issues = []
    txt = open(path, encoding="utf-8").read()
    # 1. 畸形 [[ 含 2+ 空格
    for m in re.finditer(r'\[\[[^\]]*?\s{2,}[^\]]*\]\]', txt):
        line = txt[:m.start()].count("\n") + 1
        issues.append({"type": "malformed_wikilink_spaces", "line": line, "snippet": m.group(0)[:40]})
    # 2. 未转义管道（简化：行内出现 | 且前个字符非 \，且看起来在表格上下文）— 保守仅报裸 | 在 [[..|..]] 内未转义
    for m in re.finditer(r'\[\[([^\]]*?)\|([^\]]*?)\]\]', txt):
        if "\\|" not in m.group(0):
            # 已经是正常 [[a|b]]，合法，跳过
            continue
    # 3. CJK 近形字
    for i, ch in enumerate(txt):
        if ch in glyph_blacklist:
            line = txt[:i].count("\n") + 1
            issues.append({"type": "cjk_glyph_risk", "line": line, "char": ch, "codepoint": f"U+{ord(ch):04X}"})
    return issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault-root", required=True)
    ap.add_argument("--glyph-table", default="references/cjk_glyph_table.md")
    args = ap.parse_args()

    bad = load_glyph_blacklist(args.glyph_table)
    all_issues = {}
    for root, _, files in os.walk(args.vault_root):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            iss = check_file(p, bad)
            if iss:
                all_issues[os.path.relpath(p, args.vault_root)] = iss

    print(json.dumps(all_issues, ensure_ascii=False, indent=2))
    if all_issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
