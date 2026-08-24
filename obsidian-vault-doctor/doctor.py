# -*- coding: utf-8 -*-
r"""
Obsidian Vault Doctor —— 审计 + 可选修复
用法:
  python doctor.py <vault_root>            # 仅审计
  python doctor.py <vault_root> --fix      # 审计并修复(自动备份)
  python doctor.py <vault_root> --fix --backup DIR

正确处理:
  - 表格内 wikilink 别名分隔符必须转义为 \\|
  - 目标提取按 re.split(r'\\?\|', inner)[0]，兼容转义管道
  - ![[img]] 按资源校验，不当笔记
  - .canvas 节点(file 与 text)一并扫描
"""
import os, re, sys, json, shutil, argparse

IMG_EXT = {'.png', '.webp', '.jpg', '.jpeg', '.gif', '.svg', '.bmp', '.canvas', '.html'}
WIKI_RE = re.compile(r'(!?)\[\[([^\]]+)\]\]')
INLINE_CODE = re.compile(r'`[^`]*`')
EXCLUDE = {'.workbuddy', 'node_modules', '.git'}

# --- 合并自原 cjk-glyph-guard 微 skill（vault 治理轮次）---
GLYPH_TABLE = os.path.join(os.path.dirname(__file__), 'references', 'cjk_glyph_table.md')


def load_glyph_blacklist(table_path):
    """从 cjk_glyph_table.md 解析需报警的"易错字"集合（格式：`昰` U+6630）。"""
    bad = set()
    if not os.path.exists(table_path):
        return bad
    txt = open(table_path, encoding='utf-8').read()
    for m in re.finditer(r'`([^`]+)`\s*U\+([0-9A-Fa-f]{4,})', txt):
        if len(m.group(1)) == 1:
            bad.add(m.group(1))
    return bad


GLYPH_BLACKLIST = load_glyph_blacklist(GLYPH_TABLE)


def collect(vault):
    md, bn, alias = [], {}, {}
    for dp, ds, fs in os.walk(vault):
        ds[:] = [d for d in ds if d not in EXCLUDE]
        for f in fs:
            fp = os.path.join(dp, f)
            if f.endswith('.md'):
                md.append(fp)
                bn.setdefault(f[:-3], set()).add(fp)
                try:
                    t = open(fp, encoding='utf-8').read()
                except Exception:
                    continue
                m = re.match(r'^---\n(.*?)\n---', t, re.S)
                if m:
                    am = re.search(r'aliases:\s*\n((?:\s*-\s*.+\n?)*)', m.group(1))
                    if am:
                        for line in am.group(1).split('\n'):
                            a = re.match(r'\s*-\s*"?([^"]+)"?', line)
                            if a:
                                alias.setdefault(a.group(1).strip().lower(), set()).add(fp)
    return md, bn, alias


def resolve(target, vault, bn, alias):
    target = target.strip()
    if target.lower().endswith('.md'):
        target = target[:-3]
    if '/' in target:
        return os.path.exists(os.path.join(vault, *target.split('/')) + '.md')
    if target in bn:
        return True
    if target.lower() in alias:
        return True
    return False


def norm_target(inner):
    # 兼容转义管道：按 可选反斜杠+管道 切，第一节即目标；再去锚点
    return re.split(r'\\?\|', inner)[0].split('#')[0].strip()


def audit(vault):
    md, bn, alias = collect(vault)
    R = {'dead': [], 'dotdot': [], 'mdsuffix': [], 'pipe_unesc': [],
         'img_fail': [], 'ambiguous': [], 'canvas_broken': [],
         'escaped_embed': [], 'missing_fm': [], 'cjk_glyph': []}
    for fp in md:
        rel = os.path.relpath(fp, vault)
        raw = open(fp, encoding='utf-8').read()
        lines = raw.split('\n')
        cleaned = []
        in_fence = False
        for ln in lines:
            if re.match(r'^```', ln):
                in_fence = not in_fence
                cleaned.append('')
                continue
            if in_fence:
                cleaned.append('')
                continue
            cleaned.append(INLINE_CODE.sub('', ln))
        text = '\n'.join(cleaned)
        # 表格行内未转义管道
        for i, ln in enumerate(lines):
            if re.match(r'^\|.*\|\s*$', ln.strip()):
                for m in WIKI_RE.finditer(ln):
                    if re.search(r'(?<!\\)\|', m.group(2)):
                        R['pipe_unesc'].append((rel, i + 1))
        for m in WIKI_RE.finditer(text):
            is_embed, inner = m.group(1) == '!', m.group(2)
            tgt = norm_target(inner)
            if not tgt:
                continue
            ext = os.path.splitext(tgt)[1].lower()
            if is_embed and ext in IMG_EXT and ext != '':
                # 图片/资源
                found = False
                if '/' in tgt:
                    found = os.path.exists(os.path.join(vault, *tgt.split('/')))
                else:
                    for dp2, ds2, fs2 in os.walk(vault):
                        ds2[:] = [d for d in ds2 if d not in EXCLUDE]
                        if tgt in fs2:
                            found = True
                            break
                if not found:
                    R['img_fail'].append((rel, inner))
                continue
            if '../' in tgt or tgt.startswith('./'):
                R['dotdot'].append((rel, inner))
            if tgt.endswith('.md'):
                R['mdsuffix'].append((rel, inner))
            if not resolve(tgt, vault, bn, alias):
                R['dead'].append((rel, inner))
        # --- 新增探测器（vault 治理轮次合并）---
        # 1) 转义嵌入 \![[ 导致图片不渲染（vault 内曾 8 处因此不显示）
        for m in re.finditer(r'\\!\[\[', raw):
            R['escaped_embed'].append((rel, m.start()))
        # 2) 内容条目缺 frontmatter（排除 _templates/_scenes/.trash）
        parts = rel.split(os.sep)
        if not parts[0].startswith('_') and '.trash' not in parts and not raw.startswith('---'):
            R['missing_fm'].append((rel,))
        # 3) CJK 近形字码点校验（是/昰 等）
        if GLYPH_BLACKLIST:
            for ch in raw:
                if ch in GLYPH_BLACKLIST:
                    R['cjk_glyph'].append((rel, ch, 'U+%04X' % ord(ch)))
    # canvas 扫描
    for dp, ds, fs in os.walk(vault):
        ds[:] = [d for d in ds if d not in EXCLUDE]
        for f in fs:
            if not f.endswith('.canvas'):
                continue
            cf = os.path.join(dp, f)
            try:
                data = json.load(open(cf, encoding='utf-8'))
            except Exception:
                continue
            rel = os.path.relpath(cf, vault)
            for n in data.get('nodes', []):
                refs = []
                if n.get('type') == 'file' and n.get('file'):
                    refs.append(n['file'])
                for mm in re.findall(r'\[\[([^\]]+)\]\]', n.get('text', '') or ''):
                    refs.append(mm.split('|')[0].split('#')[0])
                for r in refs:
                    r = r.strip()
                    if not r:
                        continue
                    if '/' in r:
                        ok = os.path.exists(os.path.join(vault, *r.split('/')) + ('' if r.endswith('.md') else '.md'))
                    else:
                        ok = (r in bn) or (r.lower() in alias)
                    if not ok:
                        R['canvas_broken'].append((rel, r))
    return R


def fix(vault, backup, add_frontmatter=False):
    if backup and not os.path.exists(backup):
        os.makedirs(os.path.dirname(backup) or '.', exist_ok=True)
        shutil.copytree(vault, backup)
        print('已备份 ->', backup)
    for fp in [os.path.join(dp, f) for dp, ds, fs in os.walk(vault) for f in fs if f.endswith('.md')]:
        if '.workbuddy' in fp.split(os.sep):
            continue
        raw = open(fp, encoding='utf-8').read()
        lines = raw.split('\n')
        out = []
        for ln in lines:
            if re.match(r'^\|.*\|\s*$', ln.strip()):
                def rlink(m):
                    # m.group(1) 是可选的 '!'（图片嵌入标记），'[[' 必须显式保留
                    inner = m.group(2)
                    new = re.sub(r'(?<!\\)\|', r'\\|', inner)
                    return m.group(1) + '[[' + new + ']]'
                ln = re.sub(r'(!?)\[\[([^\]]+)\]\]', rlink, ln)
            out.append(ln)
        new_raw = '\n'.join(out)
        # 路径归一化: [[../a/b.md|alias]] -> [[a/b|alias]]
        def norm(m):
            is_e, inner = m.group(1), m.group(2)
            parts = inner.split('|')
            tgt = parts[0].strip()
            if tgt.startswith('../') or tgt.startswith('./'):
                tgt = tgt[3:] if tgt.startswith('../') else tgt[2:]
            if tgt.endswith('.md'):
                tgt = tgt[:-3]
            alias = parts[1] if len(parts) > 1 else ''
            return f'{is_e}[[{tgt}|{alias}]]' if alias else f'{is_e}[[{tgt}]]'
        new_raw2 = re.sub(r'(!?)\[\[([^\]]+)\]\]', norm, new_raw)
        # --- 新增修复（vault 治理轮次合并）---
        fixed = new_raw2
        # 转义嵌入修复：仅图片嵌入 \![[图片/...]] -> ![[图片/...]]，不动文档示例
        fixed = re.sub(r'\\!\[\[图片/', '![[图片/', fixed)
        # 缺 frontmatter 补骨架（--add-frontmatter，仅内容条目）
        if add_frontmatter:
            parts = os.path.relpath(fp, vault).split(os.sep)
            if not parts[0].startswith('_') and '.trash' not in parts and not fixed.startswith('---'):
                fixed = '---\ntags:\n  - \n---\n\n' + fixed
        if fixed != raw:
            open(fp, 'w', encoding='utf-8').write(fixed)
    # canvas 归一化
    for dp, ds, fs in os.walk(vault):
        for f in fs:
            if not f.endswith('.canvas'):
                continue
            cf = os.path.join(dp, f)
            try:
                data = json.load(open(cf, encoding='utf-8'))
            except Exception:
                continue
            changed = False
            for n in data.get('nodes', []):
                if n.get('type') == 'file' and n.get('file'):
                    nf = n['file']
                    if nf.startswith('../') or nf.startswith('./') or nf.endswith('.md'):
                        n['file'] = (nf[3:] if nf.startswith('../') else (nf[2:] if nf.startswith('./') else nf))[:-3] if nf.endswith('.md') else nf
                        changed = True
            if changed:
                json.dump(data, open(cf, 'w', encoding='utf-8'), ensure_ascii=False, indent='\t')
    print('修复完成。')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('vault')
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('--add-frontmatter', action='store_true',
                    help='给缺 frontmatter 的内容条目补 ---/tags:/--- 骨架')
    ap.add_argument('--backup', default='')
    args = ap.parse_args()
    if args.fix:
        bk = args.backup or (args.vault.rstrip('/\\') + '_doctor_backup')
        fix(args.vault, bk, add_frontmatter=args.add_frontmatter)
    R = audit(args.vault)
    print('=== 审计结果 ===')
    for k in ['dead', 'dotdot', 'mdsuffix', 'pipe_unesc', 'img_fail', 'ambiguous',
              'canvas_broken', 'escaped_embed', 'missing_fm', 'cjk_glyph']:
        print(f'{k}: {len(R[k])}')
        for item in R[k][:20]:
            print('   ', item)
