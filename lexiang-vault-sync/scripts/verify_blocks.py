#!/usr/bin/env python3
"""verify_blocks.py — 乐享重导后的内容一致性校验。

乐享平台陷阱：整页重导（entry_import_content_to_entry / force_write）后，旧版本的孤立块
仍可被 block_describe_block 按旧 block_id 读到，且内容与当前展示不一致。
**判定页面真实状态，必须以 block_fetch_page（当前块树）为准。**

本脚本提供两部分：
  A. normalize_and_compare(a, b) —— 纯文本/码点级比对（可独立运行，见 __main__）
  B. fetch_current_page(entry_id) —— 调用乐享 MCP 取当前块树的占位函数（由 agent 用
     mcp__lexiang-ol__block_fetch_page 执行，把返回块树拼成纯文本后喂给 A）

用法（本地比对两个文本文件）：
  python3 verify_blocks.py source.md fetched_page.txt
"""
import re, sys, argparse


def extract_text(block_tree):
    """从 block_fetch_page 返回的块树（dict/list）递归抽取纯文本。
    适配乐享块结构：块含 'text'/'content'/'children'。"""
    if isinstance(block_tree, str):
        return block_tree
    if isinstance(block_tree, list):
        return "\n".join(extract_text(b) for b in block_tree)
    if isinstance(block_tree, dict):
        parts = []
        for k in ("text", "content", "title", "desc"):
            if k in block_tree and isinstance(block_tree[k], str):
                parts.append(block_tree[k])
        if "children" in block_tree:
            parts.append(extract_text(block_tree["children"]))
        return "\n".join(p for p in parts if p)
    return ""


def normalize(text):
    """归一化：去首尾空白、折叠连续空白、去 Markdown 图片/链接语法差异，
    仅保留码点序列用于比对。"""
    t = text.strip()
    t = re.sub(r"!\[\[[^\]]+\]\]", "", t)          # Obsidian 图片语法
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", t)      # 乐享图片语法
    t = re.sub(r"\[\[([^\]|]+)(\|[^\]]+)?\]\]", r"\1", t)  # wikilink -> 目标
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)  # md link -> 文本
    t = re.sub(r"\s+", "", t)                       # 折叠空白
    return t


def normalize_and_compare(source_text, page_text):
    """返回比对结果 dict。重点：按码点比较，避免 CJK 近形字（是/昰）被肉眼漏掉。"""
    a = normalize(source_text)
    b = normalize(page_text)
    if a == b:
        return {"match": True, "len_a": len(a), "len_b": len(b)}
    # 找出首个分歧码点位置
    n = min(len(a), len(b))
    diff_pos = next((i for i in range(n) if a[i] != b[i]), n)
    return {
        "match": False,
        "len_a": len(a), "len_b": len(b),
        "first_diff_pos": diff_pos,
        "around_a": a[max(0, diff_pos-10):diff_pos+10],
        "around_b": b[max(0, diff_pos-10):diff_pos+10],
    }


def fetch_current_page(entry_id):
    """占位：由 agent 调用 mcp__lexiang-ol__block_fetch_page({entry_id: entry_id})
    取得当前块树后，extract_text() 转纯文本返回。此处不实现 MCP 调用。"""
    raise NotImplementedError(
        "调用 mcp__lexiang-ol__block_fetch_page 获取当前块树，再 extract_text() 后传入 normalize_and_compare"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("page_text")
    args = ap.parse_args()
    a = open(args.source, encoding="utf-8").read()
    b = open(args.page_text, encoding="utf-8").read()
    print(json.dumps(normalize_and_compare(a, b), ensure_ascii=False))


if __name__ == "__main__":
    import json
    main()
