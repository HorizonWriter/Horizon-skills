# -*- coding: utf-8 -*-
"""link_utils 单元测试：wikilink 生成规范（表格内 \\| 转义、段落内不转义）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "obsidian-template-scaffolder" / "scripts"))

from link_utils import link, link_t, parse_ref


class TestLink:
    def test_link_no_alias(self):
        assert link("组织/摩晶工业") == "[[组织/摩晶工业]]"

    def test_link_with_alias(self):
        # 段落内：管道不转义
        assert link("角色/角色总览", "角色一览") == "[[角色/角色总览|角色一览]]"

    def test_link_strips_md_suffix(self):
        assert link("组织/摩晶工业.md") == "[[组织/摩晶工业]]"

    def test_link_strips_trailing_slash(self):
        assert link("组织/摩晶工业/") == "[[组织/摩晶工业]]"


class TestLinkT:
    def test_link_t_escapes_pipe(self):
        # 表格内：管道必须转义为 \\|
        assert link_t("种族/猫科亚人", "猫科亚人") == r"[[种族/猫科亚人\|猫科亚人]]"

    def test_link_t_no_alias(self):
        assert link_t("组织/摩晶工业") == "[[组织/摩晶工业]]"


class TestParseRef:
    def test_ref_with_alias(self):
        assert parse_ref("组织/玄机城|玄机城") == ("组织/玄机城", "玄机城")

    def test_ref_no_alias(self):
        assert parse_ref("组织/摩晶工业") == ("组织/摩晶工业", None)

    def test_ref_strips_whitespace(self):
        assert parse_ref(" 组织/玄机城 | 玄机城 ") == ("组织/玄机城", "玄机城")
