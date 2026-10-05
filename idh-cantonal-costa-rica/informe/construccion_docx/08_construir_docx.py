# -*- coding: utf-8 -*-
"""Construye el informe v3 (DOCX) con el formato del informe revisado. Dos pasadas para la tabla de contenido."""
import sys, subprocess, re, json, os, shutil
from ctx import *
import c1, c2, c3
from docx_lib import Builder, NS, LANG
from xml.sax.saxutils import escape

TEMPLATE = os.environ.get('TEMPLATE', '/home/claude/work/informe.docx')
OUT = os.environ.get('OUT', f'{ROOT}/Informe_Tecnico_Unificado_Cantonal_v3_revision_externa.docx')


def toc_xml(heads, pages):
    out = []; n = len(heads)
    for i, (lvl, txt) in enumerate(heads):
        pg = str(pages.get(txt, '')); ind = 0 if lvl == 1 else 300
        sz = 21 if lvl == 1 else 20
        fld_b = ('<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r>'
                 '<w:r><w:fldChar w:fldCharType="separate"/></w:r>') if i == 0 else ''
        fld_e = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if i == n - 1 else ''
        bold = lvl == 1
        out.append(f'<w:p {NS}><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="10060"/></w:tabs><w:spacing w:before="{60 if lvl==1 else 0}" w:after="20"/><w:ind w:left="{ind}"/><w:rPr>{LANG}</w:rPr></w:pPr>'
                   + fld_b + D.run(txt, b=bold, sz=sz) + f'<w:r><w:rPr>{LANG}</w:rPr><w:tab/></w:r>' + D.run(pg, b=bold, sz=sz) + fld_e + '</w:p>')
    return ''.join(out)


def build(pages):
    heads.clear()
    for f in (f'{TAB}/_x',): pass
    import ctx; ctx._used_t.clear(); ctx._used_f.clear()
    B = Builder(TEMPLATE); c = Ctx(B)
    c1.run(c); c2.run(c); c3.run(c)
    i = c.toc_index
    title = D.p_xml(D.run('Contenido', b=True, color=D.NAVY, sz=26), '<w:spacing w:after="120"/>')
    B.xml[i] = title + toc_xml(heads, pages)
    B.save(OUT)
    return list(heads)


def render(docx):
    d = os.path.dirname(docx); subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', d, docx], check=True, capture_output=True)
    return docx.replace('.docx', '.pdf')


def find_pages(pdf, hs):
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    txt = [subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), '-layout', pdf, '-'], capture_output=True, text=True).stdout for p in range(1, n + 1)]
    pages = {}; start = 3
    for lvl, h in hs:
        for p in range(start, n + 1):
            lines = [l.strip() for l in txt[p - 1].splitlines()]
            if any(l == h or (l.startswith(h) and len(l) < len(h) + 4) for l in lines):
                pages[h] = p; start = p; break
    return pages, n


if __name__ == '__main__':
    hs = build({})
    pdf = render(OUT); pages, n = find_pages(pdf, hs)
    miss = [h for _, h in hs if h not in pages]; print('páginas:', n, '| sin ubicar:', miss)
    json.dump(pages, open(f'{ROOT}/_pages.json', 'w'), ensure_ascii=False, indent=1)
    hs = build(pages); pdf = render(OUT); pages2, n2 = find_pages(pdf, hs)
    print('2.ª pasada: páginas', n2, '| TOC estable:', pages2 == pages)
    if pages2 != pages:
        json.dump(pages2, open(f'{ROOT}/_pages.json', 'w'), ensure_ascii=False, indent=1); hs = build(pages2); pdf = render(OUT)
    print(OUT)
