# -*- coding: utf-8 -*-
r"""
Obsidian Rename —— 重命名 vault 文件，全库 wikilink 自动更新
支持匹配三种链接形式：根相对路径、裸名（basename）、../相对路径（兼容已有）。
写入的新链接保持原形式：根相对→根相对，裸名→裸名。绝不新注入 ../。

用法:
  python rename.py <vault_root> <旧路径> <新路径>              # 执行
  python rename.py <vault_root> <旧路径> <新路径> --dry-run    # 预览不写入

路径为 vault 根相对，如: 角色/云朵.md → 角色/云朵小天使.md
"""
import os, sys, re, shutil
from pathlib import Path

WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def vault_walk(vault):
    for dirpath, dirnames, filenames in os.walk(vault):
        dirnames[:] = [d for d in dirnames if d not in
                       (".obsidian", ".trash", "node_modules", "__pycache__", ".git")]
        for f in filenames:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


def read_text(f):
    try:
        with open(f, encoding="utf-8-sig") as fh:
            return fh.read()
    except Exception:
        return ""


def write_text(f, text):
    with open(f, "w", encoding="utf-8-sig") as fh:
        fh.write(text)


def replace_wikilinks(content, old_rel, new_rel, old_stem, new_stem, source_rel):
    """更新 content 中所有指向 old_rel 的 wikilink 为 new_rel。返回 (new_content, count)。"""
    old_noext = old_rel.replace(".md", "")
    new_noext = new_rel.replace(".md", "")
    # 从源文件视角的 ../ 相对路径（兼容已有 ../ 链接，但不新注入）
    src_dir = os.path.dirname(source_rel)
    old_from_src = os.path.relpath(old_noext, src_dir).replace("\\", "/") if src_dir else old_noext
    new_from_src = os.path.relpath(new_noext, src_dir).replace("\\", "/") if src_dir else new_noext

    count = 0

    def replacer(m):
        nonlocal count
        raw = m.group(1)
        cleaned = raw.replace("\\|", "|")
        idx = cleaned.find("|")
        if idx > -1:
            target = cleaned[:idx].strip()
            alias = cleaned[idx + 1:].strip()
            had_escape = "\\|" in raw
        else:
            target = cleaned.strip()
            alias = None
            had_escape = False

        new_target = None
        if target == old_noext or target == old_rel:
            new_target = new_noext
        elif target == old_stem:
            new_target = new_stem
        elif target == old_from_src:
            new_target = new_from_src
        else:
            return m.group(0)

        count += 1
        if alias:
            sep = "\\|" if had_escape else "|"
            return f"[[{new_target}{sep}{alias}]]"
        return f"[[{new_target}]]"

    return WIKILINK_RE.sub(replacer, content), count


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    dry = "--dry-run" in sys.argv
    if len(args) < 3:
        print("用法: python rename.py <vault_root> <旧路径> <新路径> [--dry-run]")
        print("示例: python rename.py /path/to/vault 角色/云朵.md 角色/云朵小天使.md")
        sys.exit(1)

    vault = args[0]
    old_rel = args[1].replace("\\", "/")
    new_rel = args[2].replace("\\", "/")

    old_abs = os.path.normpath(os.path.join(vault, old_rel))
    new_abs = os.path.normpath(os.path.join(vault, new_rel))

    if not os.path.exists(old_abs):
        print(f"[FAIL] 源文件不存在: {old_abs}")
        sys.exit(1)
    if os.path.exists(new_abs):
        print(f"[FAIL] 目标已存在: {new_abs}")
        sys.exit(1)

    old_stem = os.path.splitext(os.path.basename(old_rel))[0]
    new_stem = os.path.splitext(os.path.basename(new_rel))[0]

    print(f"重命名: {old_rel} → {new_rel}")
    print(f"匹配: '{old_stem}' → '{new_stem}'")
    if dry:
        print("[dry-run] 不实际写入\n")

    # Step 1: 扫描并预览引用更新
    total_changed = 0
    updated_files = []
    for fpath in vault_walk(vault):
        rel = os.path.relpath(fpath, vault).replace("\\", "/")
        content = read_text(fpath)
        new_content, n = replace_wikilinks(content, old_rel, new_rel, old_stem, new_stem, rel)
        if n > 0:
            total_changed += n
            updated_files.append((rel, n))
            if dry:
                print(f"  [{n}处] {rel}")

    print(f"\n将更新 {total_changed} 处链接，{len(updated_files)} 个文件")
    if dry:
        print("[dry-run] 未写入。去掉 --dry-run 执行。")
        return

    # Step 2: 备份 + 重命名
    bak = old_abs + ".rename.bak"
    shutil.copy2(old_abs, bak)
    print(f"[备份] {bak}")

    os.makedirs(os.path.dirname(new_abs), exist_ok=True)
    os.rename(old_abs, new_abs)
    print("[重命名] ✓")

    # Step 3: 更新所有引用
    for fpath in vault_walk(vault):
        rel = os.path.relpath(fpath, vault).replace("\\", "/")
        content = read_text(fpath)
        new_content, n = replace_wikilinks(content, old_rel, new_rel, old_stem, new_stem, rel)
        if n > 0:
            write_text(fpath, new_content)
            print(f"  [{n}处] {rel}")

    print(f"\n✓ 完成: {old_rel} → {new_rel}（更新 {total_changed} 处链接）")


if __name__ == "__main__":
    main()
