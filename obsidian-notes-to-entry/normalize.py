# -*- coding: utf-8 -*-
r"""
Obsidian Notes to Entry —— 非标准笔记 → 标准条目转换器
检测笔记是否已标准化（H1 + 基本档案表格 + 关联板块），若否则提取信息生成标准骨架。

用法:
  python normalize.py <vault_root> <文件路径>              # 预览转换
  python normalize.py <vault_root> <文件路径> --apply      # 执行转换（自动 .bak 备份）

环境变量:
  ENTRY_FIELDS   基本档案字段（逗号分隔，默认"种族,阵营,职位,状态,核心标签"）
  LINK_SECTION   关联板块关键词（| 分隔，默认"关联板块|关联人物|related|backlinks"）
"""
import os, sys, re, shutil
from pathlib import Path

def get_vault():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    vault = args[0] if args else os.environ.get("VAULT_PATH", "")
    if not vault:
        print("用法: python normalize.py <vault_root> <文件路径> [--apply]")
        sys.exit(1)
    p = Path(vault)
    if not p.is_dir():
        print(f"[FAIL] vault 目录不存在: {vault}")
        sys.exit(1)
    return p

VAULT = get_vault()
ENTRY_FIELDS = [f.strip() for f in os.environ.get("ENTRY_FIELDS", "种族,阵营,职位,状态,核心标签").split(",") if f.strip()]
LINK_SECTION = os.environ.get("LINK_SECTION", "关联板块|关联人物|related|backlinks")

H1_RE = re.compile(r'^#\s+(.+)', re.MULTILINE)
WIKI_RE = re.compile(r'\[\[([^\]]+)\]\]')

# 自动生成检测正则
DETECT_PATTERNS = {}
for field in ENTRY_FIELDS:
    DETECT_PATTERNS[field] = re.compile(rf'(?:{re.escape(field)})[：:]\s*(.+)', re.IGNORECASE)

_R = "\033[91m"; _Y = "\033[93m"; _G = "\033[92m"; _B = "\033[1m"; _E = "\033[0m"
def color(t, n):
    m = {"red": _R, "yellow": _Y, "green": _G, "bold": _B}
    return f"{m.get(n, '')}{t}{_E}"


def read_text(f):
    try:
        return Path(f).read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def is_standardized(text):
    has_h1 = bool(H1_RE.search(text))
    has_table = "|" in text and any(kw in text[:3000] for kw in ["基本档案", "档案", "属性"])
    has_related = any(f"**{kw}**" in text or f"## {kw}" in text for kw in LINK_SECTION.split("|"))
    return has_h1 and has_table and has_related


def extract_name(text, fallback):
    m = H1_RE.search(text)
    return m.group(1).strip() if m else fallback


def extract_info(text):
    info = {}
    for key, pat in DETECT_PATTERNS.items():
        m = pat.search(text)
        if m:
            info[key] = m.group(1).strip()
    return info


def extract_wikilinks(text):
    links = []
    for m in WIKI_RE.finditer(text):
        raw = m.group(1).strip()
        cleaned = raw.replace("\\|", "|")
        target = cleaned.split("|")[0].strip().replace(".md", "")
        if target and target not in links:
            links.append(target)
    return links


def convert(file_rel, apply=False):
    path = (VAULT / file_rel)
    if not file_rel.endswith(".md"):
        path = path.with_suffix(".md")
    if not path.exists():
        print(f"{color('[ERR]', 'red')} 未找到: {path}")
        sys.exit(1)

    text = read_text(path)
    if is_standardized(text):
        print(f"{color('[OK]', 'green')} 已是标准格式，无需转换")
        return

    name = extract_name(text, path.stem)
    info = extract_info(text)
    wikilinks = extract_wikilinks(text)

    # 生成标准骨架
    lines = [f"# {name}", "", "> （待补充描述）", "", "## 基本档案", "", "| 项目 | 内容 |", "|------|------|"]
    for field in ENTRY_FIELDS:
        lines.append(f"| {field} | {info.get(field, '(待补充)')} |")
    lines.append("")

    # 保留原始正文（去掉已有的基本档案/关联板块等结构化部分）
    clean_lines = []
    in_skip = False
    skip_markers = ["基本档案", "档案"] + [f"**{kw}**" for kw in LINK_SECTION.split("|")] + [f"## {kw}" for kw in LINK_SECTION.split("|")]
    for line in text.split("\n"):
        stripped = line.strip()
        if any(m in stripped for m in skip_markers):
            in_skip = True
            continue
        if in_skip:
            if stripped.startswith("|"):
                continue
            if stripped and not stripped.startswith("|"):
                in_skip = False
        if not in_skip:
            clean_lines.append(line)

    body = "\n".join(clean_lines).strip()
    if body:
        lines.append(body)
        lines.append("")

    lines.extend(["---", ""])
    related_str = " · ".join(f"[[{w}]]" for w in wikilinks[:10]) if wikilinks else "(待补充)"
    lines.append(f"**关联板块**：{related_str}")
    result = "\n".join(lines)

    print(f"{color('── 预览 ──', 'bold')}")
    print(result[:2000] + ("..." if len(result) > 2000 else ""))
    print(f"\n{color('变更:', 'green')} {len(text)}B → {len(result)}B")

    if apply:
        bak = path.with_suffix(".md.bak")
        shutil.copy2(path, bak)
        path.write_text(result, encoding="utf-8-sig")
        print(f"{color('[OK]', 'green')} 已写入: {path.name}（备份: {bak.name}）")
    else:
        print(f"\n使用 {color('--apply', 'bold')} 写入")


if __name__ == "__main__":
    pos_args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(pos_args) < 2:
        print("用法: python normalize.py <vault_root> <文件路径> [--apply]")
        print("示例: python normalize.py /path/to/vault 角色/云朵 --apply")
        sys.exit(1)
    convert(pos_args[1], apply="--apply" in sys.argv)
