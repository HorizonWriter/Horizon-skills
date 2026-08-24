# -*- coding: utf-8 -*-
"""doctor.py 单元测试：P0 修复回归（表格转义保留 [[）、链接解析正确性。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "obsidian-vault-doctor"))

import doctor


class TestNormTarget:
    def test_plain_target(self):
        assert doctor.norm_target("组织/摩晶工业") == "组织/摩晶工业"

    def test_with_alias_unescaped_pipe(self):
        assert doctor.norm_target("组织/摩晶工业|摩晶工业") == "组织/摩晶工业"

    def test_with_escaped_pipe(self):
        # 表格内转义管道：不得被错误切成含别名的假路径
        assert doctor.norm_target(r"种族/猫科亚人\|猫科亚人") == "种族/猫科亚人"

    def test_with_anchor(self):
        assert doctor.norm_target("系统/三层架构#物理层") == "系统/三层架构"


class TestFixPreservesBrackets:
    """回归测试：fix() 转义表格内管道时必须保留 [[ 前缀（P0 bug）。"""

    def _apply_fix(self, vault):
        doctor.fix(str(vault), backup=None)
        return vault

    def test_table_link_escaped_with_brackets(self, tmp_path):
        # 构造含未转义管道表格链接的迷你 vault
        v = tmp_path / "vault"
        v.mkdir()
        (v / "角色").mkdir()
        (v / "角色" / "云朵.md").write_text(
            "| 种族 | [[种族/猫科亚人|猫科亚人]] |\n", encoding="utf-8"
        )
        self._apply_fix(v)
        content = (v / "角色" / "云朵.md").read_text(encoding="utf-8")
        # [[ 必须保留，管道必须转义为 \|
        assert r"[[种族/猫科亚人\|猫科亚人]]" in content
        assert "| 种族 | [[" in content

    def test_image_embed_kept(self, tmp_path):
        v = tmp_path / "vault"
        v.mkdir()
        (v / "角色").mkdir()
        (v / "角色" / "云朵.md").write_text(
            "| 图 | ![[图片/云朵.png]] |\n", encoding="utf-8"
        )
        self._apply_fix(v)
        content = (v / "角色" / "云朵.md").read_text(encoding="utf-8")
        assert "![[图片/云朵.png]]" in content  # 嵌入标记 ! 保留

    def test_already_escaped_untouched(self, tmp_path):
        v = tmp_path / "vault"
        v.mkdir()
        (v / "角色").mkdir()
        # 已是正确转义的形式，fix 不应破坏
        (v / "角色" / "云朵.md").write_text(
            r"| 种族 | [[种族/猫科亚人\|猫科亚人]] |" + "\n", encoding="utf-8"
        )
        self._apply_fix(v)
        content = (v / "角色" / "云朵.md").read_text(encoding="utf-8")
        assert r"[[种族/猫科亚人\|猫科亚人]]" in content
        # 不得出现双 [[ 或丢失 [[
        assert content.count("[[") == 1


class TestAudit:
    def test_audit_clean_vault(self, tmp_path):
        v = tmp_path / "vault"
        v.mkdir()
        (v / "角色").mkdir()
        (v / "角色" / "云朵.md").write_text(
            "| 种族 | [[种族/猫科亚人\\|猫科亚人]] |\n", encoding="utf-8"
        )
        # 目标文件存在
        (v / "种族").mkdir()
        (v / "种族" / "猫科亚人.md").write_text("# 猫科亚人\n", encoding="utf-8")
        r = doctor.audit(str(v))
        assert r["dead"] == []
        assert r["pipe_unesc"] == []
        assert r["dotdot"] == []
