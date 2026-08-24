# -*- coding: utf-8 -*-
r"""
Obsidian Content Hotspot —— 内容空洞排名
扫描 vault 所有 .md 文件，按「被引用数 × 内容空置率」排名，输出"最该先写的笔记"。

用法:
  python hotspot.py <vault_root>              # 默认前 20
  python hotspot.py <vault_root> --top 50     # 前 50
  python hotspot.py <vault_root> --threshold 5  # 只显示被引用≥5的

环境变量:
  IGNORE_DIRS  额外忽略目录（逗号分隔）
"""
import os, sys, re
from pathlib import Path

def get_vault():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    vault = args[0] if args else os.environ.get("VAULT_PATH", "")
    if not vault:
        print("用法: python hotspot.py <vault_root> [--top N] [--threshold N]")
        sys.exit(1)
    p = Path(vault)
    if not p.is_dir():
        print(f"[FAIL] vault 目录不存在: {vault}")
        sys.exit(1)
    return p

VAULT = get_vault()

EXTRA_IGNORE = set(d.strip() for d in os.environ.get("IGNORE_DIRS", "").split(",") if d.strip())
IGNORE_DIRS = {".obsidian", ".trash", "node_modules", "__pycache__",
               "_templates", "_scenes", ".git"} | EXTRA_IGNORE

WIKILINK_RE = re.compile(r'\[\[([^\]|#\\]+?)(?:#[^\]|]*)?(?:\\?\|[^\]]*)?\]\]')


def vault_files():
    result = []
    for f in VAULT.rglob("*.md"):
        if any(p.name in IGNORE_DIRS for p in f.parents):
            continue
        result.append(f)
    return result


def read_text(f):
    try:
        return Path(f).read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def content_density(text):
    """正文行数 / 总行数。排除标题/引用/分隔线/表格行。"""
    lines = text.strip().split("\n")
    if not lines:
        return 0.0
    body = [l for l in lines if l.strip()
            and not l.strip().startswith("#")
            and not l.strip().startswith(">")
            and not l.strip().startswith("---")
            and not l.strip().startswith("|")]
    return len(body) / max(len(lines), 1)


def count_inbound_refs(name_stem, all_texts):
    """name_stem 在多少其他文件中被引用（wikilink 或纯文本提及）。"""
    count = 0
    for text in all_texts:
        if name_stem in text:
            count += 1
    return count


def scan(top_n=20, min_refs=0):
    files = vault_files()
    if not files:
        print("  (vault 为空或无 .md 文件)")
        return

    texts = [read_text(f) for f in files]
    names = [str(f.relative_to(VAULT)).replace("\\", "/") for f in files]

    scores = []
    for f, name, text in zip(files, names, texts):
        stem = name.replace(".md", "").split("/")[-1]
        refs = count_inbound_refs(stem, texts)
        density = content_density(text)
        vacuity = 1 - min(density, 1.0)
        score = refs * vacuity
        scores.append((score, refs, vacuity, name))

    scores.sort(key=lambda x: -x[0])

    # 过滤
    if min_refs > 0:
        scores = [s for s in scores if s[1] >= min_refs]
    scores = scores[:top_n]

    print("═══════════════════════════════════════════════════════════")
    print("  内容空洞排名（引用数 × 空置率 降序）")
    print("═══════════════════════════════════════════════════════════\n")

    critical = 0
    top = scores[0][0] if scores else 1
    for i, (score, refs, vac, name) in enumerate(scores, 1):
        bar_len = int(score * 10 / max(top, 1))
        bar = "█" * min(bar_len, 10) + "▒" * max(10 - bar_len, 0)
        level = "★" if vac > 0.8 else "☆"
        print(f"  {i:>2}. {name:<40s} 引用:{refs:>3}  空置:{vac:>3.0%}  {level} {bar}")
        if vac > 0.8 and refs > 0:
            critical += 1

    print(f"\n─── 摘要 ───")
    print(f"  扫描文件: {len(files)}  |  严重空洞(空置>80%且被引用): {critical}")
    print(f"  建议优先写前 {min(5, len(scores))} 个\n")


if __name__ == "__main__":
    top = 20
    min_refs = 0
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--top" and i + 1 < len(args):
            top = int(args[i + 1])
        elif a == "--threshold" and i + 1 < len(args):
            min_refs = int(args[i + 1])
    scan(top_n=top, min_refs=min_refs)
