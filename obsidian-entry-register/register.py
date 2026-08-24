# -*- coding: utf-8 -*-
r"""
Obsidian Entry Register —— 新条目自动注册到索引/总览页
创建新 .md 后，自动更新：对应板块总览、同板块提到该名称的文件关联板块、全局索引。

用法:
  python register.py <vault_root> <文件路径>              # 注册单个文件
  python register.py <vault_root> --all                  # 扫描所有未注册文件

环境变量:
  INDEX_MAP     板块→总览路径 JSON（如 '{"组织":"组织/组织总览.md","角色":"角色/角色总览.md"}'）
  INDEX_FILE    全局索引文件（默认"世界索引.md"，不存在则跳过）
  LINK_SECTION  关联板块关键词（| 分隔，默认"关联板块|关联人物|related|backlinks"）
"""
import os, sys, re, json
from pathlib import Path

def get_vault():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    vault = args[0] if args else os.environ.get("VAULT_PATH", "")
    if not vault:
        print("用法: python register.py <vault_root> <文件路径> [--all]")
        sys.exit(1)
    p = Path(vault)
    if not p.is_dir():
        print(f"[FAIL] vault 目录不存在: {vault}")
        sys.exit(1)
    return p

VAULT = get_vault()

try:
    INDEX_MAP = json.loads(os.environ.get("INDEX_MAP", "{}"))
except json.JSONDecodeError:
    INDEX_MAP = {}

INDEX_FILE = os.environ.get("INDEX_FILE", "世界索引.md")
LINK_SECTION = os.environ.get("LINK_SECTION", "关联板块|关联人物|related|backlinks")
IGNORE = {".obsidian", ".trash", "node_modules", "__pycache__", ".git", "_templates", "_scenes", "AGENT.md"}

H1_RE = re.compile(r'^#\s+(.+)', re.MULTILINE)


def read_text(f):
    try:
        return Path(f).read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def write_text(f, text):
    Path(f).write_text(text, encoding="utf-8-sig")


# --dry-run：只预览不写入
DRY_RUN = "--dry-run" in sys.argv


def commit(f, text):
    """写入文件；--dry-run 时仅打印将执行的写入。"""
    if DRY_RUN:
        print(f"    [dry-run] 将写入: {f}")
        return
    write_text(f, text)


def get_sector(filepath):
    parts = filepath.replace("\\", "/").split("/")
    return parts[0] if len(parts) > 1 else None


def get_h1(text):
    m = H1_RE.search(text)
    return m.group(1).strip() if m else None


def has_target(text, *targets):
    """精确判断文本中是否已存在指向任一目标的 wikilink。

    目标后必须紧跟 |（别名）、#（锚点）或 ]（结尾），
    避免子串误匹配（如 云朵 不应匹配 [[云朵小天使]]）。
    """
    for t in targets:
        if t and re.search(re.escape(t) + r'[\|#\]]', text):
            return True
    return False


def register(filepath):
    path = VAULT / filepath
    if not path.exists():
        print(f"[ERR] 文件不存在: {filepath}")
        return False
    text = read_text(path)
    name = filepath.replace("\\", "/").split("/")[-1].replace(".md", "")
    h1 = get_h1(text) or name
    sector = get_sector(filepath)
    rel = filepath.replace("\\", "/").replace(".md", "")
    changes = []

    # 1. 板块总览
    if sector and sector in INDEX_MAP:
        ov_path = VAULT / INDEX_MAP[sector]
        if ov_path.exists():
            ov_text = read_text(ov_path)
            if not has_target(ov_text, name, f"{sector}/{name}", rel):
                link = f"[[{rel}|{h1}]]"
                ov_text = ov_text.rstrip() + f"\n- {link} — \n"
                commit(ov_path, ov_text)
                changes.append(f"总览 {INDEX_MAP[sector]} 追加引用")

    # 2. 同板块提到该名称的文件的关联板块
    if sector:
        sector_dir = VAULT / sector
        if sector_dir.is_dir():
            for sf in sector_dir.glob("*.md"):
                if sf.name == filepath.split("/")[-1] or "总览" in sf.name:
                    continue
                sf_text = read_text(sf)
                if h1 in sf_text and any(kw in sf_text for kw in LINK_SECTION.split("|")):
                    if not has_target(sf_text, name, rel):
                        link = f"[[{rel}|{h1}]]"
                        for kw in LINK_SECTION.split("|"):
                            marker = f"**{kw}**"
                            if marker in sf_text:
                                sf_text = sf_text.replace(marker, f"{marker}：{link} · ", 1)
                                commit(sf, sf_text)
                                changes.append(f"{sf.name} 追加关联板块")
                                break

    # 3. 全局索引
    idx_path = VAULT / INDEX_FILE
    if idx_path.exists():
        idx_text = read_text(idx_path)
        if not has_target(idx_text, name, rel, f"{sector}/{name}"):
            link = f"[[{rel}|{h1}]]"
            idx_text = idx_text.rstrip() + f"\n- {link} — \n"
            commit(idx_path, idx_text)
            changes.append(f"{INDEX_FILE} 追加条目")

    if changes:
        print(f"[OK] {filepath} 注册完成:")
        for c in changes:
            print(f"     → {c}")
    else:
        print(f"[-] {filepath} 无需更新（可能已注册）")
    return True


if __name__ == "__main__":
    pos_args = [a for a in sys.argv[1:] if not a.startswith("-")]
    # pos_args[0] 是 vault（已由 get_vault 消费），pos_args[1] 是 filepath
    if "--all" in sys.argv:
        for f in sorted(VAULT.rglob("*.md")):
            if any(p.name in IGNORE for p in f.parents):
                continue
            rel = str(f.relative_to(VAULT)).replace("\\", "/")
            if rel.startswith("_templates/") or f.name in ("世界索引.md",):
                continue
            if f.stat().st_size < 50:
                continue
            register(rel)
    elif len(pos_args) >= 2:
        register(pos_args[1])
    else:
        print("用法: python register.py <vault_root> <文件路径> [--all]")
        sys.exit(1)
