# -*- coding: utf-8 -*-
"""
Wikilink 工具函数。

遵守 Obsidian wikilink 规范：
  - vault 根相对路径（禁止 ../）
  - 段落/列表内：管道 | 不转义
  - 表格单元格内：管道 | 转义为 \\|
"""


def link(target, alias=None):
    """生成段落/列表内的 wikilink。

    示例:
        link("角色/角色总览", "角色一览")  →  [[角色/角色总览|角色一览]]
        link("组织/摩晶工业")              →  [[组织/摩晶工业]]
    """
    target = target.replace(".md", "").replace("\\", "/").rstrip("/")
    if alias:
        return f"[[{target}|{alias}]]"
    return f"[[{target}]]"


def link_t(target, alias=None):
    """生成表格单元格内的 wikilink，管道转义为 \\|。

    示例:
        link_t("种族/猫科亚人", "猫科亚人")  →  [[种族/猫科亚人\\|猫科亚人]]
        link_t("组织/摩晶工业")              →  [[组织/摩晶工业]]
    """
    target = target.replace(".md", "").replace("\\", "/").rstrip("/")
    if alias:
        return f"[[{target}\\|{alias}]]"
    return f"[[{target}]]"


def parse_ref(ref_str):
    """解析关联板块字符串 "目标|别名" 或 "目标" → (target, alias_or_None)。"""
    ref_str = ref_str.strip()
    if "|" in ref_str:
        t, a = ref_str.split("|", 1)
        return t.strip(), a.strip()
    return ref_str, None
