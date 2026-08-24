# -*- coding: utf-8 -*-
r"""
凌日星世界观条目脚手架 v2 —— 基于 _templates/ 模板元数据。

创建符合 Obsidian wikilink 规范的 vault 新条目：
  - 自动 H1 标题
  - 根据板块类型动态生成「基本档案」表格（表格内管道转义为 \\|）
  - 「关联板块」段落（vault 根相对链接，段落内不转义 |）
  - 可选的「创作提示词」注释块（供 AI 参考，不影响渲染）

关键约束：
  - 链接一律 vault 根相对（绝不写 ../）
  - 表格单元格内 wikilink 别名分隔符转义为 \\|
  - 只新建文件，不修改任何已有文件

用法：
  # 列出支持的板块类型
  python scaffold.py --list-types

  # 创建条目（输出到板块目录）
  python scaffold.py <vault_root> <板块类型> --name <名称> [--fields KEY=VALUE...] [--refs 目标|别名,...]

  # 创建条目（输出到 _scenes/ 供审阅）
  python scaffold.py <vault_root> <板块类型> --name <名称> --draft

  # 仅预览（不写文件）
  python scaffold.py <vault_root> <板块类型> --name <名称> --dry-run

示例：
  python scaffold.py /workspace/世界观 角色 --name 林夕 --fields "org=玄机城,race=猫科亚人,tags=神秘·剑客"
  python scaffold.py /workspace/世界观 组织 --name 暗星会 --fields "nature=秘密结社,status=现存"
  python scaffold.py /workspace/世界观 地理 --name 星光码头 --draft
"""

import sys
import os
import argparse
from pathlib import Path

# 确保脚本目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from template_registry import TEMPLATES, list_types, get_template, guess_type
from link_utils import link, link_t, parse_ref


def build_archive_table(template, fields_dict):
    """根据模板 fields 定义和用户输入构建基本档案表格。

    表格单元格内的 wikilink 使用 link_t()（管道转义），
    纯文本值直接填入。
    """
    rows = []
    rows.append("| 项目 | 内容 |")
    rows.append("|------|------|")
    for label, var in template["fields"]:
        value = fields_dict.get(var, "—")
        # 如果值看起来像 wikilink 目标（含 /），转成表格内链接
        if "/" in value and not value.startswith("[["):
            # 检查是否有别名（| 分隔）
            if "|" in value:
                tgt, als = value.split("|", 1)
                value = link_t(tgt.strip(), als.strip())
            else:
                value = link_t(value)
        rows.append(f"| {label} | {value} |")
    return "\n".join(rows)


def build_refs(template, extra_refs):
    """构建关联板块段落。

    合并 template.default_refs 和用户指定的 extra_refs，
    用 · 连接，段落内不转义 |。
    """
    ref_links = []
    seen = set()
    # 先加默认引用
    for r in template.get("default_refs", []):
        tgt, als = parse_ref(r)
        key = tgt.lower()
        if key not in seen:
            seen.add(key)
            ref_links.append(link(tgt, als))
    # 再加用户引用
    if extra_refs:
        for r in extra_refs.split(","):
            r = r.strip()
            if not r:
                continue
            tgt, als = parse_ref(r)
            key = tgt.lower()
            if key not in seen:
                seen.add(key)
                ref_links.append(link(tgt, als))
    return " · ".join(ref_links) if ref_links else "（待补充）"


def build_draft(template, name, fields_dict, refs_str, include_prompt=True):
    """构建完整的 .md 文件内容。"""
    parts = []

    # H1 标题
    parts.append(f"# {name}")
    parts.append("")

    # 引语
    parts.append(f"> （待补充）")
    parts.append("")

    # 基本档案表格
    parts.append("## 基本档案")
    parts.append("")
    parts.append(build_archive_table(template, fields_dict))
    parts.append("")

    # 正文占位
    prompt = template.get("prompt", "")
    if include_prompt and prompt:
        # 用 HTML 注释嵌入创作提示词（Obsidian 不渲染，但 AI 可读）
        parts.append("<!--")
        parts.append("创作提示词（来自 _templates）：")
        for line in prompt.strip().split("\n"):
            parts.append(f"  {line}")
        parts.append("-->")
        parts.append("")

    parts.append("## 概述")
    parts.append("")
    parts.append("（待补充）")
    parts.append("")

    # 关联板块
    parts.append(f"**关联板块**：{refs_str}")
    parts.append("")

    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(
        description="凌日星世界观条目脚手架 v2 —— 基于 _templates/ 模板元数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python scaffold.py /workspace/世界观 角色 --name 林夕 --fields "org=玄机城,race=猫科亚人"
  python scaffold.py /workspace/世界观 组织 --name 暗星会 --draft
  python scaffold.py /workspace/世界观 --list-types
""",
    )
    ap.add_argument("vault", nargs="?", help="vault 根目录")
    ap.add_argument("type", nargs="?", help="板块类型（角色/组织/种族/科技/地理/事件/历史/物品/文化/生物/疾病/军事/系统/凌日星概要）")
    ap.add_argument("--list-types", action="store_true", help="列出支持的板块类型")
    ap.add_argument("--name", help="条目显示名称")
    ap.add_argument("--fields", default="", help="档案字段，逗号分隔 KEY=VALUE 格式")
    ap.add_argument("--refs", default="", help="额外关联板块，逗号分隔 目标|别名 格式")
    ap.add_argument("--draft", action="store_true", help="输出到 _scenes/ 目录供审阅（默认输出到板块目录）")
    ap.add_argument("--output", help="指定输出路径（覆盖 --draft 和默认路径）")
    ap.add_argument("--dry-run", action="store_true", help="仅预览内容，不写入文件")
    ap.add_argument("--no-prompt", action="store_true", help="不嵌入创作提示词注释块")
    args = ap.parse_args()

    # --list-types
    if args.list_types:
        print("支持的板块类型（14 种）：")
        print()
        for k in list_types():
            t = TEMPLATES[k]
            print(f"  {k:8s}  →  {t['dir']}/{t['overview'].split('/')[-1]}  ({t['hint']})")
        print()
        print("别名：人物→角色  势力→组织  地点→地理  装备→物品  亚人→种族  等")
        return

    # 校验参数
    if not args.vault or not args.type:
        ap.print_help()
        sys.exit(1)

    root = Path(args.vault).resolve()
    if not root.is_dir():
        print(f"[FAIL] vault 目录不存在: {root}")
        sys.exit(1)

    template = get_template(args.type)
    if not template:
        print(f"[FAIL] 未知板块类型: {args.type}")
        print(f"       支持的类型: {', '.join(list_types())}")
        print(f"       使用 --list-types 查看详情")
        sys.exit(1)

    # 确定名称
    name = args.name
    if not name:
        print("[FAIL] 需要 --name 参数指定条目名称")
        sys.exit(1)

    # 解析 fields
    fields_dict = {}
    if args.fields:
        for kv in args.fields.split(","):
            kv = kv.strip()
            if "=" in kv:
                k, v = kv.split("=", 1)
                fields_dict[k.strip()] = v.strip()

    # 自动填入 name
    if "name" in [f[1] for f in template["fields"]] and "name" not in fields_dict:
        fields_dict["name"] = name

    # 构建内容
    refs_str = build_refs(template, args.refs)
    content = build_draft(template, name, fields_dict, refs_str, include_prompt=not args.no_prompt)

    # 确定输出路径
    if args.output:
        out_path = root / args.output
    elif args.draft:
        safe_name = name.replace("/", "·").replace("\\", "·")
        out_path = root / "_scenes" / f"{safe_name}.md"
    else:
        safe_name = name.replace("/", "·").replace("\\", "·")
        out_path = root / template["dir"] / f"{safe_name}.md"

    # 安全检查：必须落在 vault 内
    out_resolved = out_path.resolve()
    if not str(out_resolved).startswith(str(root)):
        print("[FAIL] 输出路径越界（必须位于 vault 内）")
        sys.exit(1)

    if args.dry_run:
        print(f"[DRY-RUN] 将创建: {out_path.relative_to(root)}")
        print(f"         板块类型: {template['key']} ({template['hint']})")
        print(f"         总览文件: {template['overview']}")
        print("=" * 60)
        print(content)
        print("=" * 60)
        return

    if out_path.exists():
        print(f"[FAIL] 文件已存在: {out_path.relative_to(root)}")
        print(f"       使用 --output 指定其他路径，或 --draft 输出到 _scenes/")
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    rel = out_path.relative_to(root)
    print(f"[OK] 创建条目: {rel}")
    print(f"     板块: {template['key']} ({template['hint']})")
    print(f"     总览: {template['overview']}")
    print(f"     规范: vault 根相对 ✓  表格内 \\| 转义 ✓  无 ../ ✓")
    if not args.no_prompt:
        print(f"     提示词: 已嵌入创作指南（来自 _templates/{template['key']}.md）")


if __name__ == "__main__":
    main()
