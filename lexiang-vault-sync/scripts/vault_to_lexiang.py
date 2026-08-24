#!/usr/bin/env python3
"""vault_to_lexiang.py — 把 Obsidian vault 的 markdown 转换为乐享可导入的 markdown。

转换规则：
  - 图片嵌入 ![[图片/x.jpg]] 或 ![[x.jpg]]  ->  COS 基础 URL（来自 img_map，按文件名查）
  - wikilink [[文件夹/笔记|别名]] 或 [[文件夹/笔记]]  ->  /pages/{entry_id}（来自 page_map，按路径查）
  - 表格内转义管道 \|  保留不动（乐享同样需要）

用法：
  python3 vault_to_lexiang.py --vault-root /workspace/世界观 \
      --page-map /workspace/lexiang_page_map.json \
      --img-map  /workspace/lexiang_img_map.json \
      --out-dir  /tmp/lexiang_out

只打印转换统计；如需落盘加 --write。
"""
import os, re, json, argparse


def load_map(path):
    if not path or not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def convert(text, page_map, img_map):
    stats = {"images": 0, "images_missing": 0, "links": 0, "links_missing": 0}

    # 图片嵌入: ![[...]]  （非转义）
    def img_repl(m):
        inner = m.group(1).strip()
        name = os.path.basename(inner)
        url = img_map.get(name) or img_map.get(inner)
        stats["images"] += 1
        if url:
            return f"![]({url})"
        stats["images_missing"] += 1
        return m.group(0)  # 保留原样，交由后续上传

    text = re.sub(r'(?<!\\)!\[\[([^\]]+)\]\]', img_repl, text)

    # wikilink: [[目标|别名]] 或 [[目标]]
    def link_repl(m):
        inner = m.group(1)
        target = inner.split("|")[0].strip().rstrip("\\")
        alias = inner.split("|")[1].strip() if "|" in inner else ""
        # 规范化路径：去 .md 后缀
        key = target[:-3] if target.endswith(".md") else target
        entry_id = page_map.get(key) or page_map.get(target)
        stats["links"] += 1
        if entry_id:
            label = alias or os.path.basename(target)
            return f"[{label}](/pages/{entry_id})"
        stats["links_missing"] += 1
        return m.group(0)

    text = re.sub(r'(?<!\\)\[\[([^\]]+)\]\]', link_repl, text)
    return text, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault-root", required=True)
    ap.add_argument("--page-map", default="/workspace/lexiang_page_map.json")
    ap.add_argument("--img-map", default="/workspace/lexiang_img_map.json")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    page_map = load_map(args.page_map)
    img_map = load_map(args.img_map)

    total = {"images": 0, "images_missing": 0, "links": 0, "links_missing": 0}
    for root, _, files in os.walk(args.vault_root):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            text = open(p, encoding="utf-8").read()
            new_text, st = convert(text, page_map, img_map)
            for k in total:
                total[k] += st[k]
            if args.write and args.out_dir and new_text != text:
                rel = os.path.relpath(p, args.vault_root)
                out = os.path.join(args.out_dir, rel)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                open(out, "w", encoding="utf-8").write(new_text)

    print(json.dumps({"converted": total}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
