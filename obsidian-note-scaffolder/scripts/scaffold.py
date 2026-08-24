# -*- coding: utf-8 -*-
"""
Obsidian 规范条目脚手架（通用版）。

创建符合 Obsidian 规范的 vault 新条目：
  - 自动 H1 标题
  - 「基本档案」表格
  - 「关联板块」段落（vault 根相对链接，段落内不转义 |）
  - 如需在表格单元格内放链接，使用 link_t() 转义为 \\|

关键：链接一律 vault 根相对（绝不写 ../），从源头预防死链与表格打散。
只新建文件，不修改任何已有文件。

用法：
  python scaffold.py <vault_root> <板块/文件名.md> [--type 人物] [--name 全名] [--org 阵营] [--refs 目标|别名,目标2]
"""
import sys
import os
import argparse
from pathlib import Path

# 板块模板（通用骨架；可自由增删）。模板里表格单元格默认用纯文本（无链接），
# 因此无需转义；若将来在表格内放链接，请用 link_t()。
SECTION_TEMPLATES = {
    "人物": {
        "basic": """## 基本档案

| 项目 | 内容 |
|------|------|
| 全名 | {name} |
| 阵营 | {org} |
| 状态 | 现存 |
| 核心标签 | — |

## 概述

（待补充）

## 经历

（待补充）
""",
    },
    "组织": {
        "basic": """## 基本档案

| 项目 | 内容 |
|------|------|
| 全称 | {name} |
| 性质 | — |
| 现状 | 现存 |
| 核心标签 | — |

## 概况

（待补充）

## 关联人物

- （待补充）
""",
    },
    "地点": {
        "basic": """## 基本档案

| 项目 | 内容 |
|------|------|
| 名称 | {name} |
| 类型 | — |
| 状态 | 现存 |

## 概述

（待补充）
""",
    },
}

DEFAULT_TEMPLATE = {
    "basic": "（待补充）\n",
}


def link(target, alias=None):
    """生成段落/列表内 wikilink：vault 根相对，不转义 |。"""
    if alias:
        return f"[[{target}|{alias}]]"
    return f"[[{target}]]"


def link_t(target, alias=None):
    """生成表格单元格内 wikilink：别名分隔符必须转义为 \\|。"""
    if alias:
        return f"[[{target}\\|{alias}]]"
    return f"[[{target}]]"


def main():
    ap = argparse.ArgumentParser(description="创建规范化 vault 条目")
    ap.add_argument("vault", help="vault 根目录")
    ap.add_argument("path", help="相对路径，如 角色/林夕.md")
    ap.add_argument("--type", help="条目类型（对应板块模板）")
    ap.add_argument("--name", help="显示名称（默认取自文件名）")
    ap.add_argument("--org", default="—", help="所属组织/阵营")
    ap.add_argument("--refs", help="预设关联链接，逗号分隔，格式 目标|别名 或 目标")
    args = ap.parse_args()

    root = Path(args.vault).resolve()
    if not root.exists():
        print(f"[FAIL] vault 不存在: {root}")
        sys.exit(1)

    filepath = (root / args.path).resolve()
    # 防越界：新文件必须落在 vault 内
    if not str(filepath).startswith(str(root)):
        print("[FAIL] 路径越界（必须位于 vault 内）")
        sys.exit(1)
    if filepath.exists():
        print(f"[FAIL] 文件已存在: {args.path}")
        sys.exit(1)

    name = args.name or Path(args.path).stem
    section = args.type or args.path.split("/")[0]

    tpl = SECTION_TEMPLATES.get(section, DEFAULT_TEMPLATE)
    basic = tpl["basic"].format(name=name, org=args.org)

    refs_parts = []
    if args.refs:
        for r in args.refs.split(","):
            r = r.strip()
            if "|" in r:
                t, a = r.split("|", 1)
                # 段落内链接不转义
                refs_parts.append(link(t.strip(), a.strip()))
            else:
                refs_parts.append(link(r))
    refs = " · ".join(refs_parts) if refs_parts else "（待补充）"

    content = f"""# {name}

> （待补充）

{basic}

**关联板块**：{refs}
"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    print(f"[OK] 创建: {args.path} (板块: {section})")
    print(f"     链接规范: vault 根相对 + 表格内 \\| 转义 ✓  无 ../ ✓")


if __name__ == "__main__":
    main()
