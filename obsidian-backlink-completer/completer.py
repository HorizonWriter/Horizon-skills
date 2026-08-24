# -*- coding: utf-8 -*-
r"""
Obsidian Backlink Completer —— 自动补全双向引用
扫描 vault 条目的"关联板块"，检测 A→B 但 B 没有反向引用 A，自动追加回链。

用法:
  python completer.py <vault_root>              # dry-run 预览
  python completer.py <vault_root> --apply      # 写入修复（自动 .bak 备份）
  python completer.py <vault_root> --stats      # 仅统计完备率

环境变量:
  LINK_SECTION   关联板块关键词（| 分隔的 正则 or，默认"关联板块|关联人物|related|backlinks"）
  IGNORE_DIRS    额外忽略目录（逗号分隔）
  NON_ENTRY      不算条目的文件名（逗号分隔）

写入的链接格式为 vault 根相对 [[目录/文件|别名]]，不注入 ../（Obsidian 不识别）。
正确处理表格内转义管道 \|。
"""
import os, sys, re, shutil
from pathlib import Path

# 注意：本文件中的 vault_files/read_file/write_file/color 与 shared-vault-lib/libvault.py 重复。
# 两者行为一致（含 \\| 转义处理）。新代码请统一复用 libvault；此处保留以免破坏现有调用。

def get_vault():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    vault = args[0] if args else os.environ.get("VAULT_PATH", "")
    if not vault:
        print("用法: python completer.py <vault_root> [--apply|--stats]")
        sys.exit(1)
    p = Path(vault)
    if not p.is_dir():
        print(f"[FAIL] vault 目录不存在: {vault}")
        sys.exit(1)
    return p

VAULT = get_vault()

LINK_SECTION = os.environ.get("LINK_SECTION", "关联板块|关联人物|related|backlinks")
EXTRA_IGNORE = set(d.strip() for d in os.environ.get("IGNORE_DIRS", "").split(",") if d.strip())
IGNORE_DIRS = {".obsidian", ".trash", "node_modules", "__pycache__",
               "_templates", "_scenes", ".git"} | EXTRA_IGNORE

NON_ENTRY = {".gitignore", "README.md", "LICENSE"}
_extra_non = os.environ.get("NON_ENTRY", "")
if _extra_non:
    NON_ENTRY |= set(f.strip() for f in _extra_non.split(",") if f.strip())

RELATED_RE = re.compile(r"\*\*(?:" + LINK_SECTION + r")\*\*[：:]?\s*(.*)")
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

_R = "\033[91m"; _Y = "\033[93m"; _G = "\033[92m"; _C = "\033[96m"; _B = "\033[1m"; _E = "\033[0m"
def color(text, name):
    m = {"red": _R, "yellow": _Y, "green": _G, "cyan": _C, "bold": _B}
    return f"{m.get(name, '')}{text}{_E}"


def vault_files():
    result = []
    for f in VAULT.rglob("*.md"):
        if any(p.name in IGNORE_DIRS for p in f.parents):
            continue
        result.append(f)
    return result


def read_file(f):
    try:
        return Path(f).read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def write_file(f, text, backup=False):
    p = Path(f)
    if backup and p.exists():
        shutil.copy2(p, p.parent / (p.name + ".bak"))
    p.write_text(text, encoding="utf-8-sig")
    return True


def is_entry(f):
    if f.name in NON_ENTRY or f.suffix != ".md":
        return False
    if any(d in f.parts for d in IGNORE_DIRS):
        return False
    return True


def get_related_links(text):
    """从关联板块行提取所有 wikilink 目标（根相对路径）。正确处理 \\| 转义。"""
    m = RELATED_RE.search(text)
    if not m:
        return set()
    targets = set()
    for wm in WIKILINK_RE.finditer(m.group(1)):
        raw = wm.group(1).strip()
        cleaned = raw.replace("\\|", "|")          # 还原转义管道
        target = cleaned.split("|")[0].strip().replace(".md", "")
        if target:
            targets.add(target)
    return targets


def file_stem_to_rel(f):
    return str(f.relative_to(VAULT).with_suffix("")).replace("\\", "/")


def fix_backlinks(dry_run=True):
    entry_rels = {}
    for f in vault_files():
        if not is_entry(f):
            continue
        text = read_file(f)
        if not text:
            continue
        rel = file_stem_to_rel(f)
        links = get_related_links(text)
        entry_rels[rel] = {"path": f, "text": text, "links": links}

    missing = []
    for rel_a, da in entry_rels.items():
        a_name = rel_a.split("/")[-1]
        for target_raw in da["links"]:
            if target_raw not in entry_rels:
                continue
            db = entry_rels[target_raw]
            b_name = target_raw.split("/")[-1]
            b_has_a = any(a_name in l or rel_a == l or rel_a in l for l in db["links"])
            if b_has_a:
                continue
            missing.append((rel_a, a_name, target_raw, b_name, db["path"], db["text"]))

    if not missing:
        print(color("  完备率 100%，无缺失回链", "green"))
        return

    print(f"  发现 {len(missing)} 处缺失回链:\n")
    for ra, an, rb, bn, _, _ in missing:
        print(f"    {color(an, 'yellow')} → {color(bn, 'cyan')}")

    if dry_run:
        print(f"\n  使用 {color('--apply', 'bold')} 写入修复")
        return

    fixed = 0
    for ra, an, rb, bn, b_path, b_text in missing:
        link = f"[[{ra}|{an}]]"            # 根相对，绝不注入 ../
        if link in b_text:
            continue
        lines = b_text.split("\n")
        for i, l in enumerate(lines):
            if any(kw in l for kw in LINK_SECTION.split("|")):
                lines[i] = l.rstrip() + f" · {link}"
                if write_file(b_path, "\n".join(lines), backup=True):
                    fixed += 1
                    print(f"    {color('+', 'green')} {bn} ← {an}")
                break
    print(f"\n  修复 {fixed}/{len(missing)} 处")


def stats():
    entry_rels = {}
    for f in vault_files():
        if not is_entry(f):
            continue
        text = read_file(f)
        if not text:
            continue
        rel = file_stem_to_rel(f)
        entry_rels[rel] = get_related_links(text)

    total_pairs = complete_pairs = 0
    for rel_a, links_a in entry_rels.items():
        a_name = rel_a.split("/")[-1]
        for target_raw in links_a:
            if target_raw not in entry_rels:
                continue
            total_pairs += 1
            if any(a_name in l or rel_a == l or rel_a in l for l in entry_rels[target_raw]):
                complete_pairs += 1

    rate = (complete_pairs / total_pairs * 100) if total_pairs else 100
    print(f"\n  关联板块完备率: {complete_pairs}/{total_pairs} ({rate:.1f}%)")
    print(f"  缺失: {total_pairs - complete_pairs}")


if __name__ == "__main__":
    if "--stats" in sys.argv:
        stats()
    else:
        fix_backlinks(dry_run="--apply" not in sys.argv)
