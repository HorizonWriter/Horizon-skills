"""shared-vault-lib: 被多个 worldbuilding skill 共用的 vault 访问与工具函数。

原先缺失（F:/世界观/skills/shared-vault-lib/scripts/libvault.py 不存在），
导致 6 个 skill（ghost-detector / entry-expander-advisor / scene-canon-tracker /
timeline-checker / plot-hook-tracker / backlink-completer）导入即崩溃、完全跑不起来。
现补齐，所有 skill 共用同一份实现。

vault 根目录优先读环境变量 VAULT_PATH，否则回退到 F:/世界观/世界观。
注意：不要把路径写死成 C:/Users/.../Downloads（该目录已不存在）。
"""
import os
import re
import shutil
import sys
from pathlib import Path


def _detect_vault_root():
    """跨平台定位 vault 根目录：
    1. 环境变量 LR_VAULT / VAULT_PATH（兼容旧名）
    2. 从当前工作目录向上查找含 .obsidian/ 的目录
    3. 兜底：当前目录
    不再硬编码任何 Windows 路径。
    """
    for var in ("LR_VAULT", "VAULT_PATH"):
        v = os.environ.get(var)
        if v:
            p = Path(v)
            if p.is_dir():
                return p
            print(f"[warn] 环境变量 {var}={v} 指向不存在的目录，继续探测", file=sys.stderr)
    cwd = Path.cwd().resolve()
    for p in (cwd, *cwd.parents):
        if (p / ".obsidian").is_dir():
            return p
    return cwd


VAULT_ROOT = _detect_vault_root()

IGNORE_DIRS = {".obsidian", ".trash", "node_modules", "__pycache__",
               "_scenes", "_templates", "贡献列表", ".workbuddy", ".git"}
# 被排除的非目录条目：vault 根下的 skill 文档、索引等不应被当作物料扫描
IGNORE_FILES = {"SKILL.md", "AGENT.md", "世界索引.md"}

# 目标排除 ] | # 和 \（反斜杠仅出现在表格内转义管道 \| 前）；
# 可选锚点 #[...]，可选别名分隔符支持 \\|（表格转义）与 |（普通）
WIKILINK_RE = re.compile(r'\[\[([^\]|#\\]+?)(?:#[^\]|]*)?(?:\\?\|[^\]]*)?\]\]')


def vault_files():
    """遍历 vault 下所有 .md 文件（排除 IGNORE_DIRS 目录与 IGNORE_FILES 文件）。"""
    result = []
    for f in VAULT_ROOT.rglob("*.md"):
        if any(p.name in IGNORE_DIRS for p in f.parents):
            continue
        if f.name in IGNORE_FILES:
            continue
        result.append(f)
    return result


def read_file(f, strict=False):
    """读取文件。

    strict=False（默认）：文件不存在/读取失败时返回 ""（向后兼容旧调用方）。
    strict=True：失败时抛出明确异常，便于调用方区分"空文件"与"读取失败"。
    """
    try:
        return Path(f).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        if strict:
            raise
        return ""
    except Exception as exc:  # 权限、编码等错误
        if strict:
            raise
        print(f"[warn] read_file 读取失败: {f} ({exc})", file=sys.stderr)
        return ""


def write_file(f, text, backup=False):
    p = Path(f)
    if backup and p.exists():
        shutil.copy2(p, p.parent / (p.name + ".bak"))
    p.write_text(text, encoding="utf-8-sig")
    return True


_COLORS = {
    "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
    "cyan": "\033[96m", "bold": "\033[1m",
}
_END = "\033[0m"


def color(text, name):
    return f"{_COLORS.get(name, '')}{text}{_END}"


def all_wikilinks(text):
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(text or "")]


def count_refs(text):
    return len(all_wikilinks(text))
