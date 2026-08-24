#!/usr/bin/env python3
"""snapshot_audit.py — vault 运维文档生成器的实测数据来源。

聚合关键体检维度，输出 JSON，供 vault-ops-handoff 渲染 HANDOFF/CHECK/SKILLBUILD。
与 obsidian-vault-doctor 的 doctor.py 互补：doctor 出完整修复报告，本脚本出精简快照。

维度：
  - escaped_embed: \![[ 转义嵌入（图片不渲染）
  - missing_fm:    内容条目（非 _templates/_scenes/.trash）缺 frontmatter
  - dead:          死链（正确处理表格内 \| 转义）
  - cjk_glyph:     CJK 近形字（来自 references 下的码点表，可选）

用法：
  python3 snapshot_audit.py /workspace/世界观
"""
import os, re, json, argparse


def load_glyph_blacklist(table_path):
    bad = set()
    if not os.path.exists(table_path):
        return bad
    txt = open(table_path, encoding="utf-8").read()
    for m in re.finditer(r'`([^`]+)`\s*U\+([0-9A-Fa-f]{4,})', txt):
        if len(m.group(1)) == 1:
            bad.add(m.group(1))
    return bad


def audit(vault, glyph_blacklist=None):
    glyph_blacklist = glyph_blacklist or set()
    res = {"total_md": 0, "escaped_embed": [], "missing_fm": [], "dead": [], "cjk_glyph": []}
    for dp, ds, fs in os.walk(vault):
        for f in fs:
            if not f.endswith(".md"):
                continue
            fp = os.path.join(dp, f)
            rel = os.path.relpath(fp, vault)
            res["total_md"] += 1
            if rel.startswith("_templates") or rel.startswith("_scenes") or rel.startswith(".trash"):
                continue
            raw = open(fp, encoding="utf-8").read()
            # 转义嵌入
            for m in re.finditer(r'\\!\[\[', raw):
                res["escaped_embed"].append(rel)
                break
            # 缺 frontmatter（内容条目）
            if not raw.startswith("---"):
                res["missing_fm"].append(rel)
            # CJK 近形字
            for ch in raw:
                if ch in glyph_blacklist:
                    res["cjk_glyph"].append((rel, "U+%04X" % ord(ch)))
                    break
            # 死链（正确处理 \| 转义；跳过图片嵌入 ![[...]]，资源校验由 doctor 负责）
            txt_nc = re.sub(r'```.*?```', '', raw, flags=re.S)
            txt_nc = re.sub(r'`[^`]*`', '', txt_nc)
            for m in re.finditer(r'(!?)\[\[([^\]]+)\]\]', txt_nc):
                if m.group(1) == '!':
                    continue  # 图片嵌入，不计死链
                inner = m.group(2)
                tgt = re.split(r'\\?\|', inner)[0].split('#')[0].strip()
                if not tgt:
                    continue
                cand = os.path.join(vault, tgt + '.md')
                if not os.path.exists(cand):
                    res["dead"].append((rel, tgt))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vault")
    ap.add_argument("--glyph-table", default="")
    args = ap.parse_args()
    glyph = load_glyph_blacklist(args.glyph_table) if args.glyph_table else set()
    r = audit(args.vault, glyph)
    # 去重列表
    for k in ("escaped_embed", "missing_fm", "cjk_glyph"):
        r[k] = sorted(set(r[k]))
    r["dead"] = sorted(set(r["dead"]))
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
