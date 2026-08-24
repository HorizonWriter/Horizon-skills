# -*- coding: utf-8 -*-
"""
Obsidian 一致性扫描器（通用版）。

对任何 Obsidian vault 做九类一致性检查并输出分级报告。
已移除世界观特定的三层架构 / AGENT 统计，保留通用维度。
链接解析严格处理表格内转义竖线（正则 (?<!\\)\\|）只拆未转义的竖线。

用法：
  python check.py <vault_root>
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

IGNORE_DIRS = {".obsidian", ".trash", "node_modules", "__pycache__", ".git",
                "_templates"}
EMPTY_THRESHOLD = 80
MINI_THRESHOLD = 200
RELATED_KEYWORDS = ["关联板块", "关联页面", "related", "see also", "相关"]
wikilink_re = re.compile(r"\[\[([^\]]+?)\]\]")
h1_re = re.compile(r"^#\s+(.+)")


def split_target(inner):
    # 用 可选反斜杠+管道 切分：\\|（表格转义）与 |（普通）都是目标/别名分隔符
    parts = re.split(r"\\?\|", inner)
    target = parts[0].strip().split("#")[0].strip()
    return target.replace("\\", "/").replace(".md", "")


def load_all_md(root):
    files = []
    for f in root.rglob("*.md"):
        if any(p.name in IGNORE_DIRS for p in f.parents) or f.parent.name in IGNORE_DIRS:
            continue
        if "AGENT" in f.name:
            continue
        if f.is_file():
            files.append(f)
    return files


def main(root):
    root = Path(root).resolve()
    problems = {"red": [], "yellow": [], "blue": []}
    all_files = load_all_md(root)
    name_to_rel = {}
    rels_set = set()
    for f in all_files:
        rel = str(f.relative_to(root)).replace("\\", "/").replace(".md", "")
        rels_set.add(rel)
        name_to_rel[rel.split("/")[-1]] = rel

    link_sources = defaultdict(list)
    concept_values = defaultdict(list)
    h1_inventory = {}
    for f in all_files:
        rel = str(f.relative_to(root)).replace("\\", "/")
        if f.stat().st_size < EMPTY_THRESHOLD:
            problems["red"].append(f"空文件: {rel} ({f.stat().st_size} bytes)")
            continue
        if f.stat().st_size < MINI_THRESHOLD:
            problems["blue"].append(f"迷你文件: {rel} ({f.stat().st_size} bytes)")
        try:
            text = f.read_text(encoding="utf-8-sig")
        except Exception:
            problems["yellow"].append(f"{rel} -- 编码读取失败")
            continue

        # H1
        h1m = h1_re.search(text)
        if not h1m:
            problems["blue"].append(f"{rel}: 缺少 H1 标题")
        else:
            h1 = h1m.group(1).strip()
            if h1 in h1_inventory.values():
                problems["blue"].append(f"重复标题 H1: 「{h1}」 ({rel})")
            h1_inventory[rel] = h1

        # 关联板块
        low = text.lower()
        if not any(k.lower() in low for k in RELATED_KEYWORDS):
            if "总览" not in rel and "索引" not in rel and "世界索引" not in rel:
                problems["blue"].append(f"{rel}: 缺少关联板块/相关段落")

        # 重复段落
        paras = [
            p.strip()
            for p in text.split("\n\n")
            if p.strip() and len(p.strip()) >= 20 and not p.strip().startswith("#")
        ]
        seen = set()
        for p in paras:
            if p in seen:
                problems["blue"].append(f"{rel}: 重复段落 ({p[:40]}...)")
            else:
                seen.add(p)

        # 概念值
        for m in re.finditer(r"(\S+?率|危险级|等级)\s*(\d+\.?\d*(?:%|/10)?)", text):
            concept_values[m.group(1)].append((m.group(2), rel))

        # 表格内未转义管道（打散风险）
        for line in text.splitlines():
            if line.strip().startswith("|") and line.strip().endswith("|"):
                inner = line.strip()[1:-1]
                # 找表格单元格里的 wikilink，若其内部含未转义 | 则告警
                for m in wikilink_re.finditer(inner):
                    if re.search(r"(?<!\\)\|", m.group(1)):
                        problems["yellow"].append(
                            f"{rel}: 表格内 wikilink 含未转义 | → 表格可能被打散: {m.group(0)}"
                        )

        # 链接
        for m in wikilink_re.finditer(text):
            if m.start() > 0 and text[m.start() - 1] == "!":
                continue  # 图片嵌入 ![[...]]，不是笔记链接
            raw = m.group(1)
            if "`" in raw:
                continue  # 行内代码占位符
            t = split_target(raw)
            if t:
                link_sources[t].append(rel)

    # 死链
    for target, sources in link_sources.items():
        # 文件真实存在即放行（含 _templates/_scenes 等被 IGNORE 的目录）
        if Path(root, target + ".md").exists():
            continue
        if target in rels_set or target.split("/")[-1] in name_to_rel:
            continue
        problems["yellow"].append(f"死链: [[{target}]] (引用自 {sources[0]})")

    # 孤页
    all_refed = set(link_sources.keys())
    for rel in rels_set:
        if rel.endswith("世界索引"):
            continue
        if rel not in all_refed and rel.split("/")[-1] not in all_refed:
            problems["blue"].append(f"孤立页面: {rel}")

    # 概念值冲突
    for concept, entries in concept_values.items():
        unique = set(v for v, _ in entries)
        if len(unique) > 1:
            details = "; ".join(f"{v}@{s}" for v, s in entries)
            problems["red"].append(
                f"概念值冲突: 「{concept}」= {'/'.join(unique)} — {details}"
            )

    # 内容重复
    seen_cores = {}
    for f in all_files:
        rel = str(f.relative_to(root)).replace("\\", "/")
        if f.stat().st_size < EMPTY_THRESHOLD:
            continue
        text = f.read_text(encoding="utf-8")
        lines = [l for l in text.splitlines() if not l.startswith("#") and "关联" not in l]
        core = "\n".join(lines[:20])
        if len(core) > 100:
            if core in seen_cores:
                problems["yellow"].append(f"内容重复: {rel} 与 {seen_cores[core]}")
            else:
                seen_cores[core] = rel

    # 单向引用
    for target, sources in link_sources.items():
        if target in rels_set and len(sources) == 1:
            source = sources[0]
            tgt_refs = link_sources.get(source, [])
            if source.split("/")[-1] not in [s.split("/")[-1] for s in tgt_refs]:
                problems["blue"].append(f"单向引用: {target} ← {source}")

    print("Obsidian 一致性扫描报告")
    print(f"文件数: {len(all_files)}\n")
    sections = [("red", "[严重]"), ("yellow", "[警告]"), ("blue", "[建议]")]
    for color, label in sections:
        items = problems[color]
        if items:
            print(f"{label} ({len(items)})")
            for it in sorted(items):
                print(f"  {it}")
            print()
    if not any(problems[c] for c in problems):
        print("未发现问题。")
    print("── 摘要 ──")
    print(
        f"  严重: {len(problems['red'])} | 警告: {len(problems['yellow'])} | 建议: {len(problems['blue'])}"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check.py <vault_root>")
        sys.exit(1)
    main(sys.argv[1])
