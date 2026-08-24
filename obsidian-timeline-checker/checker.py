# -*- coding: utf-8 -*-
r"""
Obsidian Timeline Checker —— 时间线矛盾检测器
扫描 vault 中的时间引用、年龄线索、占位年份，跨文件交叉对比，输出疑似矛盾列表。

用法:
  python checker.py <vault_root>

环境变量:
  ERA_PATTERN   自定义纪年正则（如 "凌日纪年[前]?约?(\d+)年" 或 "公元(\d+)年"）
                 设了则同时匹配通用年份 + 自定义纪年；不设则只匹配通用 "\d{1,4}年"
  PLACEHOLDER   占位符模式（默认 "■■■|???|TBD|待定"）
  IGNORE_DIRS   额外忽略目录（逗号分隔）
"""
import os, sys, re
from pathlib import Path

def get_vault():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    vault = args[0] if args else os.environ.get("VAULT_PATH", "")
    if not vault:
        print("用法: python checker.py <vault_root>")
        sys.exit(1)
    p = Path(vault)
    if not p.is_dir():
        print(f"[FAIL] vault 目录不存在: {vault}")
        sys.exit(1)
    return p

VAULT = get_vault()

EXTRA_IGNORE = set(d.strip() for d in os.environ.get("IGNORE_DIRS", "").split(",") if d.strip())
IGNORE_DIRS = {".obsidian", ".trash", "node_modules", "__pycache__",
               "_templates", "_scenes", ".git"} | EXTRA_IGNORE

# 纪年模式：默认通用年份，可通过 ERA_PATTERN 追加自定义
_DEFAULT_YEAR = re.compile(r'(\d{1,4})\s*年')
_era = os.environ.get("ERA_PATTERN", "")
ERA_RES = [_DEFAULT_YEAR]
if _era:
    try:
        ERA_RES.append(re.compile(_era))
    except re.error:
        pass

# 用完整匹配串（含纪年前缀）做分布统计
YEAR_FULL_RES = []
if _era:
    YEAR_FULL_RES.append(re.compile(_era))
YEAR_FULL_RES.append(re.compile(r'[前]?约?(\d{1,4})\s*年'))

PLACEHOLDER_RE = re.compile(os.environ.get("PLACEHOLDER", r"■■■|\?\?\?|TBD|待定"))
AGE_RE = re.compile(r'(约?)(\d+)\s*岁')
FIRST_APPEAR_RE = re.compile(r'首次(?:出现|登场)[：:]\s*([^。\n]+)')
BIRTH_RE = re.compile(r'(?:出生|诞生)于([^。\n]+)')

_R = "\033[91m"; _Y = "\033[93m"; _G = "\033[92m"; _C = "\033[96m"; _B = "\033[1m"; _E = "\033[0m"
def color(text, name):
    m = {"red": _R, "yellow": _Y, "green": _G, "cyan": _C, "bold": _B}
    return f"{m.get(name, '')}{text}{_E}"


def vault_files():
    result = []
    for f in VAULT.rglob("*.md"):
        if any(p.name in IGNORE_DIRS for p in f.parents):
            continue
        result.append(f)
    return result


def read_text(f):
    try:
        return Path(f).read_text(encoding="utf-8-sig")
    except Exception:
        return ""


def scan():
    years = {}
    placeholders = {}
    ages = {}
    first_appears = {}
    births = {}

    for f in vault_files():
        content = read_text(f)
        if not content:
            continue
        rel = str(f.relative_to(VAULT)).replace("\\", "/")
        for pat in YEAR_FULL_RES:
            for m in pat.finditer(content):
                years.setdefault(m.group(0), []).append(rel)
        for m in PLACEHOLDER_RE.finditer(content):
            line_num = content[:m.start()].count("\n") + 1
            placeholders.setdefault(rel, []).append(line_num)
        for m in AGE_RE.finditer(content):
            prefix = content[max(0, m.start() - 40):m.start()]
            ages.setdefault(f"{m.group(0)}({prefix})", []).append(rel)
        for m in FIRST_APPEAR_RE.finditer(content):
            first_appears.setdefault(m.group(1).strip(), []).append(rel)
        for m in BIRTH_RE.finditer(content):
            births.setdefault(m.group(1).strip(), []).append(rel)

    return years, placeholders, ages, first_appears, births


def main():
    years, placeholders, ages, first_appears, births = scan()
    contradictions = []

    print(f"\n  {color('时间线矛盾报告', 'cyan')}\n")

    print(f"  {color('时间引用分布', 'bold')}")
    for yr, files in sorted(years.items()):
        print(f"    {yr} → {', '.join(files)}")

    if placeholders:
        print(f"\n  {color('占位年份分布', 'yellow')}")
        for f, lines in sorted(placeholders.items(), key=lambda x: -len(x[1])):
            print(f"    {f}: {len(lines)} 处 (行 {', '.join(map(str, lines[:5]))}{'...' if len(lines) > 5 else ''})")

    # 矛盾检测：同一年份关键词出现在同一文件（可能描述不同事件 → 疑似矛盾）
    yr_keys = list(years.keys())
    for i in range(len(yr_keys)):
        for j in range(i + 1, len(yr_keys)):
            k1, k2 = yr_keys[i], yr_keys[j]
            shared = set(years[k1]) & set(years[k2])
            if shared:
                contradictions.append((k1, k2, list(shared)))

    if contradictions:
        print(f"\n  {color('疑似矛盾', 'red')}")
        for k1, k2, shared in contradictions:
            print(f"    {k1} 与 {k2} 出现在同一文件: {', '.join(shared)}")

    if first_appears:
        print(f"\n  {color('首次出现/诞生描述', 'cyan')}")
        for desc, files in sorted(first_appears.items()):
            print(f"    「{desc}」 → {', '.join(files)}")
        for desc, files in sorted(births.items()):
            print(f"    「{desc}」 → {', '.join(files)}")

    if not contradictions:
        print(f"\n  {color('✔ 未发现硬性时间矛盾', 'green')}")
    else:
        print(f"\n  {color(f'⚠ 发现 {len(contradictions)} 处疑点，建议人工核实', 'yellow')}")


if __name__ == "__main__":
    main()
