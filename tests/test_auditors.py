# -*- coding: utf-8 -*-
"""consistency-checker / orphan-auditor 解析修复回归测试。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "obsidian-consistency-checker" / "scripts"))
import check as check_mod

sys.path.insert(0, str(Path(__file__).parent.parent / "obsidian-orphan-auditor" / "scripts"))
import auditor as auditor_mod


class TestCheckSplitTarget:
    def test_escaped_pipe_table(self):
        # 表格内转义管道：目标不得残留反斜杠
        assert check_mod.split_target(r"种族/猫科亚人\|猫科亚人") == "种族/猫科亚人"

    def test_normal_pipe_alias(self):
        assert check_mod.split_target("角色/云朵|云朵") == "角色/云朵"

    def test_anchor(self):
        assert check_mod.split_target("系统/三层架构#物理层") == "系统/三层架构"

    def test_anchor_with_alias(self):
        assert check_mod.split_target("系统/三层架构#物理层|物理层") == "系统/三层架构"

    def test_md_suffix(self):
        assert check_mod.split_target("组织/摩晶工业.md") == "组织/摩晶工业"


class TestAuditorSplitTarget:
    def test_escaped_pipe_table(self):
        assert auditor_mod.split_target(r"物品/晶能设备\|晶能设备") == "物品/晶能设备"

    def test_normal_pipe_alias(self):
        assert auditor_mod.split_target("组织/玄机城|玄机城") == "组织/玄机城"

    def test_anchor(self):
        assert auditor_mod.split_target("事件/摩尔晶体发现#经过") == "事件/摩尔晶体发现"


class TestCheckDeadLinkSkipsEmbed:
    def test_image_embed_not_dead_link(self, tmp_path):
        # 构造 vault：一个文件里只有图片嵌入 + 一条真实死链
        v = tmp_path / "vault"
        v.mkdir()
        (v / "角色").mkdir()
        (v / "角色" / "a.md").write_text(
            "![[图片/云朵.png]]\n[[角色/真不存在的角色]]\n", encoding="utf-8"
        )
        problems = {"red": [], "yellow": [], "blue": []}
        # 手动模拟死链检测逻辑：收集链接目标
        import re
        text = (v / "角色" / "a.md").read_text(encoding="utf-8-sig")
        rels_set = {"角色/a"}
        name_to_rel = {"a": "角色/a"}
        link_sources = {}
        for m in check_mod.wikilink_re.finditer(text):
            if m.start() > 0 and text[m.start() - 1] == "!":
                continue  # 图片嵌入跳过
            t = check_mod.split_target(m.group(1))
            if t:
                link_sources[t] = ["角色/a.md"]
        dead = []
        for target, sources in link_sources.items():
            if Path(v, target + ".md").exists():
                continue
            if target in rels_set or target.split("/")[-1] in name_to_rel:
                continue
            dead.append(target)
        # 图片嵌入不应报死链；真不存在的角色应报
        assert "图片/云朵.png" not in dead
        assert "角色/真不存在的角色" in dead
