# -*- coding: utf-8 -*-
r"""
Obsidian Section Filler —— 扫描空文件/迷你文件，自动生成骨架内容
用法:
  python filler.py <vault_root> --list-all              # 列出所有空文件
  python filler.py <vault_root> --status <板块名>        # 查看板块填充状态
  python filler.py <vault_root> --fill-empty            # 自动填充所有空文件

环境变量:
  MIN_SIZE       判定为"空文件"的大小阈值（默认 50 字节）
  TEMPLATE_FILE  模板文件名后缀（默认 ".template.md"，目录下有则读取）
"""
import os, sys, re
from pathlib import Path

def get_vault():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    vault = args[0] if args else os.environ.get("VAULT_PATH", "")
    if not vault:
        print("用法: python filler.py <vault_root> [--list-all|--status <板块>|--fill-empty]")
        sys.exit(1)
    p = Path(vault)
    if not p.is_dir():
        print(f"[FAIL] vault 目录不存在: {vault}")
        sys.exit(1)
    return p

VAULT = get_vault()
MIN_SIZE = int(os.environ.get("MIN_SIZE", "50"))
TEMPLATE_SUFFIX = os.environ.get("TEMPLATE_FILE", ".template.md")
IGNORE = {".obsidian", ".trash", "node_modules", "__pycache__", ".git", "_templates", "_scenes"}


def read_text(f):
    try:
        return Path(f).read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def write_text(f, text):
    Path(f).write_text(text, encoding="utf-8-sig")


def scan_sections():
    """自动扫描 vault 顶层目录作为板块。"""
    result = []
    for d in sorted(VAULT.iterdir()):
        if d.is_dir() and d.name not in IGNORE:
            result.append(d)
    return result


def find_section(name):
    for d in scan_sections():
        if name in d.name:
            return d
    return None


def read_template(section_dir):
    """读取目录下的模板文件（如有）。"""
    for f in section_dir.iterdir():
        if f.suffix == ".md" and TEMPLATE_SUFFIX in f.name:
            return f.read_text(encoding="utf-8-sig")
    return None


def read_index(section_dir):
    for f in section_dir.iterdir():
        if f.is_file() and f.suffix == ".md" and ("总览" in f.name or "index" in f.name.lower()):
            return f
    return None


def list_pending(section_dir):
    pending = []
    for f in section_dir.iterdir():
        if not (f.is_file() and f.suffix == ".md"):
            continue
        if TEMPLATE_SUFFIX in f.name or "总览" in f.name or "index" in f.name.lower():
            continue
        content = read_text(f)
        sz = f.stat().st_size
        if "待补充" in content or sz < MIN_SIZE:
            reason = "待补充" if "待补充" in content else f"空文件({sz}b)"
            pending.append((f.name, reason))
    return pending


def generate_skeleton(section_name, entry_name):
    """生成通用骨架内容。"""
    name = entry_name.replace(".md", "")
    idx_file = read_index(Path(VAULT) / section_name)
    related = f"- [[{section_name}/{idx_file.stem}|{idx_file.stem}]]" if idx_file else "(待补充)"
    return (
        f"# {name}\n"
        f"\n"
        f"> 待补充\n"
        f"\n"
        f"## 基本档案\n"
        f"\n"
        f"| 属性 | 内容 |\n"
        f"|------|------|\n"
        f"|  |  |\n"
        f"\n"
        f"## 概述\n"
        f"\n"
        f"<!-- 待补充 -->\n"
        f"\n"
        f"## 详细信息\n"
        f"\n"
        f"<!-- 待补充 -->\n"
        f"\n"
        f"---\n"
        f"\n"
        f"**关联板块**：{related}\n"
    )


def list_all_empty():
    print(f"空文件 / 待补充清单\n")
    total = 0
    for section_dir in scan_sections():
        pending = list_pending(section_dir)
        if pending:
            print(f"[{section_dir.name}] ({len(pending)})")
            for name, reason in pending:
                print(f"  - {name} ({reason})")
                total += 1
            print()
    print(f"共 {total} 个文件待填充")


def show_status(section_dir):
    total = filled = 0
    pending = []
    for f in section_dir.iterdir():
        if not (f.is_file() and f.suffix == ".md"):
            continue
        if TEMPLATE_SUFFIX in f.name or "总览" in f.name or "index" in f.name.lower():
            continue
        total += 1
        sz = f.stat().st_size
        if sz < MIN_SIZE or "待补充" in read_text(f):
            pending.append(f.name)
        else:
            filled += 1
    idx_file = read_index(section_dir)
    print(f"\n板块: {section_dir.name}")
    if idx_file:
        print(f"索引: {idx_file.name}")
    print(f"总条目: {total}  |  已填充: {filled}  |  待填充: {len(pending)}")
    if pending:
        print("待填充:")
        for p in pending:
            print(f"  - {p}")


def fill_all_empty(dry_run=False):
    """自动填充所有空文件为骨架内容。dry_run=True 时仅预览。"""
    filled = 0
    for section_dir in scan_sections():
        for f in section_dir.iterdir():
            if not (f.is_file() and f.suffix == ".md"):
                continue
            if TEMPLATE_SUFFIX in f.name or "总览" in f.name or "index" in f.name.lower():
                continue
            sz = f.stat().st_size
            if sz == 0 or (sz < MIN_SIZE and len(read_text(f).strip()) < 20):
                content = generate_skeleton(section_dir.name, f.name)
                if dry_run:
                    print(f"  [dry-run] 将填充: {section_dir.name}/{f.name}")
                else:
                    write_text(f, content)
                filled += 1
    print(f"\n共 {'将' if dry_run else ''}填充 {filled} 个文件")


def main():
    pos_args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if "--list-all" in sys.argv:
        list_all_empty()
        return
    if "--fill-empty" in sys.argv:
        dry_run = "--dry-run" in sys.argv
        print("即将自动填充所有空文件（生成骨架内容）。")
        print("已存在的非空文件不会被覆盖。")
        if dry_run:
            fill_all_empty(dry_run=True)
            return
        confirm = input("确认？(y/N): ").strip().lower()
        if confirm == "y":
            fill_all_empty()
        else:
            print("已取消")
        return
    if "--status" in sys.argv:
        idx = sys.argv.index("--status")
        section_name = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        if not section_name:
            print("用法: python filler.py <vault> --status <板块名>")
            print(f"可用板块: {[d.name for d in scan_sections()]}")
            sys.exit(1)
        section_dir = find_section(section_name)
        if not section_dir:
            print(f"未找到板块: {section_name}")
            print(f"可用板块: {[d.name for d in scan_sections()]}")
            sys.exit(1)
        show_status(section_dir)
        return

    print("用法:")
    print("  python filler.py <vault> --list-all              # 列出所有空文件")
    print("  python filler.py <vault> --status <板块名>        # 查看板块填充状态")
    print("  python filler.py <vault> --fill-empty            # 自动填充所有空文件")
    print(f"\n板块: {[d.name for d in scan_sections()]}")
    sys.exit(1)


if __name__ == "__main__":
    main()
