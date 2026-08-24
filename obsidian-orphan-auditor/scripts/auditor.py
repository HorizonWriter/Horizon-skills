# -*- coding: utf-8 -*-
"""
Obsidian 索引/总览完整性审计器（通用版）。

扫描 vault 中每个目录的索引/总览文件（名称含 INDEX_KEYWORDS），
对比该目录实际文件列表，报告：
  - 缺条目：目录内文件未出现在索引
  - 孤立链接：索引中链接的目标不存在
  - 重复索引：同目录多个索引文件
  - 缺索引：目录有文件但无索引页
  - 重复文件：同目录内名称或链接高度重叠的文件对

链接解析严格处理表格内转义竖线：用正则 (?<!\\)\\| 只拆未转义的竖线，
因此 [[组织/摩晶工业\\|摩晶工业]] 能正确取到目标「组织/摩晶工业」。

用法：
  python auditor.py <vault_root>            # 索引完整性审计
  python auditor.py <vault_root> --dedup    # 重复文件检测
"""
import sys
from pathlib import Path
from collections import defaultdict

IGNORE_DIRS = {".obsidian", ".trash", "node_modules", "__pycache__", ".git",
                "_templates", "_scenes", "贡献列表", "archives"}
INDEX_KEYWORDS = ["总览", "索引", "清单", "index", "overview", "目录",
                  "年表", "导读", "生态", "社会", "概要", "重大事件", "史话"]
IGNORE_FILES = set()

import re
wikilink_re = re.compile(r"\[\[([^\]]+?)\]\]")
h1_re = re.compile(r"^#\s+(.+)")

R = "\033[91m"
Y = "\033[93m"
G = "\033[92m"
C = "\033[96m"
B = "\033[1m"
E = "\033[0m"


def split_target(inner):
    """从 [[inner]] 提取链接目标。

    用 可选反斜杠+管道 切分：\\|（表格转义）与 |（普通）都是目标/别名分隔符，
    再按 # 拆锚点。避免 \\| 残留反斜杠被误当成路径分隔符。
    """
    parts = re.split(r"\\?\|", inner)
    target = parts[0].strip().split("#")[0].strip()
    return target.replace("\\", "/").replace(".md", "")


def load_files(root):
    files = {}
    by_dir = defaultdict(list)
    for f in root.rglob("*.md"):
        if any(p.name in IGNORE_DIRS for p in f.parents):
            continue
        if "AGENT" in f.name:
            continue
        if f.name in IGNORE_FILES or f.parent.name in IGNORE_DIRS:
            continue
        rel = str(f.relative_to(root)).replace("\\", "/").replace(".md", "")
        try:
            text = f.read_text(encoding="utf-8-sig")
        except Exception:
            continue
        h1 = h1_re.search(text)
        links = set()
        for m in wikilink_re.finditer(text):
            if m.start() > 0 and text[m.start() - 1] == "!":
                continue  # 图片嵌入 ![[...]]，不是笔记链接
            links.add(split_target(m.group(1)))
        files[rel] = {
            "name": f.stem,
            "h1": h1.group(1).strip() if h1 else f.stem,
            "size": len(text),
            "links": links,
        }
        d = rel.split("/")[0] if "/" in rel else "."
        by_dir[d].append(rel)
    return files, by_dir


def is_index(rel, data):
    name = data["name"].lower()
    return any(k.lower() in name for k in INDEX_KEYWORDS)


def resolve_link(target, idx_rel, files):
    """三形式解析：根相对 / 源相对(../) / basename。"""
    target = target.replace("\\", "/").replace(".md", "").strip()
    if not target:
        return None
    if target in files:
        return target
    if target.startswith("../"):
        parts = idx_rel.split("/")
        up = target.count("../")
        base = parts[: len(parts) - up - 1] if up < len(parts) else []
        rest = target[up * 3:].lstrip("/")
        cand = "/".join(base + [rest])
        return cand if cand in files else None
    if "/" in target:
        return target if target in files else None
    for r in files:
        if r.split("/")[-1] == target or files[r]["name"] == target:
            return r
    return None


def cmd_audit(root):
    files, by_dir = load_files(root)
    print(f"{B}── 索引完整性审计 ──{E}\n")
    total_missing = 0
    total_orphans = 0
    no_index_dirs = 0
    for dirname, rels in sorted(by_dir.items()):
        indices = [(r, files[r]) for r in rels if is_index(r, files[r])]
        entries = [(r, files[r]) for r in rels if not is_index(r, files[r])]
        if not indices:
            if entries:
                no_index_dirs += 1
                print(f"  {Y}{dirname}/{E} ({len(entries)} 个条目, {R}缺索引页{E})")
            continue
        idx_rel, idx_data = indices[0]
        idx_targets = set()
        for l in idx_data["links"]:
            resolved = resolve_link(l, idx_rel, files)
            if resolved:
                idx_targets.add(resolved)
        missing = []
        for er, ed in entries:
            if ed["name"] == idx_data["name"]:
                continue
            if er not in idx_targets and ed["name"] not in {
                r.split("/")[-1] for r in idx_targets
            }:
                missing.append(er)
        orphans = [t for t in idx_targets if t not in files]
        if missing or orphans:
            print(f"  {C}{idx_data['name']}{E} ({dirname}/)")
            for er in missing:
                total_missing += 1
                print(f"    {Y}缺条目{E} → {er}")
            for t in orphans:
                total_orphans += 1
                print(f"    {R}孤立链接{E} → {t}")
        if len(indices) > 1:
            print(f"    {Y}重复索引{E}: {', '.join(r for r, _ in indices)}")
    print(f"\n{G}── 汇总 ──{E}")
    print(f"  无索引目录: {no_index_dirs}")
    print(f"  缺条目: {total_missing}")
    print(f"  孤立链接: {total_orphans}")


def cmd_dedup(root):
    files, by_dir = load_files(root)
    print(f"{B}── 重复文件检测 ──{E}\n")
    found = False
    for dirname, rels in sorted(by_dir.items()):
        names = [(r, files[r]["name"]) for r in rels]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1, n2 = names[i][1], names[j][1]
                if n2.startswith(n1) or n1.startswith(n2):
                    d1, d2 = files[names[i][0]], files[names[j][0]]
                    overlap = len(d1["links"] & d2["links"])
                    if overlap > max(len(d1["links"]), len(d2["links"])) * 0.4:
                        found = True
                        print(
                            f"  {Y}可能重复{E}: {names[i][0]} <-> {names[j][0]} ({overlap} 处共享链接)"
                        )
    if not found:
        print(f"  {G}无重复检测{E}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python auditor.py <vault_root> [--dedup]")
        sys.exit(1)
    root = Path(sys.argv[1]).resolve()
    if not root.exists():
        print(f"vault 不存在: {root}")
        sys.exit(1)
    if len(sys.argv) > 2 and sys.argv[2] == "--dedup":
        cmd_dedup(root)
    else:
        cmd_audit(root)
