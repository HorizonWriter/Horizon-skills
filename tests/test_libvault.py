# -*- coding: utf-8 -*-
"""libvault 单元测试：vault 根探测、wikilink 解析、文件读写。"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared-vault-lib" / "scripts"))

import libvault


class TestDetectVaultRoot:
    def test_env_var_priority(self, tmp_path, monkeypatch):
        # 设置一个不存在 + 一个存在的环境变量，应优先存在的
        fake = tmp_path / "fake_vault"
        fake.mkdir()
        (fake / ".obsidian").mkdir()
        monkeypatch.setenv("LR_VAULT", str(fake))
        monkeypatch.setenv("VAULT_PATH", "/nonexistent/xxx")
        assert libvault._detect_vault_root() == fake

    def test_detect_upward_from_obsidian(self, tmp_path, monkeypatch):
        # 清空环境变量后，从 cwd 向上探测 .obsidian/
        v = tmp_path / "proj" / "vault"
        v.mkdir(parents=True)
        (v / ".obsidian").mkdir()
        monkeypatch.delenv("LR_VAULT", raising=False)
        monkeypatch.delenv("VAULT_PATH", raising=False)
        monkeypatch.chdir(v)
        assert libvault._detect_vault_root() == v

    def test_fallback_to_cwd(self, tmp_path, monkeypatch):
        monkeypatch.delenv("LR_VAULT", raising=False)
        monkeypatch.delenv("VAULT_PATH", raising=False)
        monkeypatch.chdir(tmp_path)
        assert libvault._detect_vault_root() == tmp_path


class TestWikilinkParsing:
    def test_all_wikilinks_plain(self):
        text = "见 [[组织/摩晶工业]] 和 [[角色/云朵|云朵]]"
        assert libvault.all_wikilinks(text) == ["组织/摩晶工业", "角色/云朵"]

    def test_all_wikilinks_anchor_and_alias(self):
        text = "[[系统/三层架构#物理层|物理层]]"
        assert libvault.all_wikilinks(text) == ["系统/三层架构"]

    def test_all_wikilinks_image_embed(self):
        # 图片嵌入 ![[...]] 也应被解析为目标（调用方自行区分）
        text = "![[图片/云朵.png]]"
        assert libvault.all_wikilinks(text) == ["图片/云朵.png"]

    def test_all_wikilinks_escaped_pipe_in_table(self):
        # 表格内转义管道 \| ：目标应取 | 之前
        text = "| [[种族/猫科亚人\\|猫科亚人]] |"
        assert libvault.all_wikilinks(text) == ["种族/猫科亚人"]

    def test_count_refs(self):
        text = "[[a]] [[b|c]] [[d]]"
        assert libvault.count_refs(text) == 3


class TestFileIO:
    def test_read_file_missing_default(self, tmp_path):
        assert libvault.read_file(tmp_path / "nope.md") == ""

    def test_read_file_missing_strict(self, tmp_path):
        import pytest
        with pytest.raises(FileNotFoundError):
            libvault.read_file(tmp_path / "nope.md", strict=True)

    def test_read_file_normal(self, tmp_path):
        p = tmp_path / "a.md"
        p.write_text("hello", encoding="utf-8")
        assert libvault.read_file(p) == "hello"

    def test_write_file_with_backup(self, tmp_path):
        p = tmp_path / "a.md"
        p.write_text("v1", encoding="utf-8")
        libvault.write_file(p, "v2", backup=True)
        # write_file 使用 utf-8-sig（带 BOM，Obsidian 兼容），读取需用同一编码
        assert p.read_text(encoding="utf-8-sig") == "v2"
        assert (tmp_path / "a.md.bak").exists()
        assert (tmp_path / "a.md.bak").read_text(encoding="utf-8-sig") == "v1"


class TestVaultFiles:
    def test_vault_files_excludes_ignored(self, tmp_path, monkeypatch):
        v = tmp_path / "vault"
        v.mkdir()
        (v / ".obsidian").mkdir()
        (v / "角色").mkdir()
        (v / "角色" / "云朵.md").write_text("# 云朵", encoding="utf-8")
        (v / "_templates").mkdir()
        (v / "_templates" / "角色.md").write_text("# 模板", encoding="utf-8")
        (v / "SKILL.md").write_text("skill", encoding="utf-8")
        monkeypatch.setattr(libvault, "VAULT_ROOT", v)
        files = libvault.vault_files()
        names = [f.name for f in files]
        assert "云朵.md" in names
        assert "角色.md" not in names          # _templates 被排除
        assert "SKILL.md" not in names         # SKILL.md 被排除
