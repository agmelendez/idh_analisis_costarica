# -*- coding: utf-8 -*-
"""Constructores XML que replican el formato del informe revisado (v2 revisión filológica)."""
import re, copy
from xml.sax.saxutils import escape
from docx import Document
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')
NAVY = '1F3864'; GREY = '595959'
LANG = '<w:lang w:val="es-ES"/>'


def num(x, d=2, sign=False):
    """Formato con coma decimal."""
    s = f'{x:+.{d}f}' if sign else f'{x:.{d}f}'
    s = s.replace('.', ',')
    return s.replace('-', '−')


def pct(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',') + '%'


def pf(p):
    return '< 0,001' if p < 0.001 else f'{p:.3f}'.replace('.', ',')


def rpr(b=False, i=False, color=None, sz=None, font=None, extra=''):
    s = ''
    if font:
        s += f'<w:rFonts w:ascii="{font}" w:eastAsia="{font}" w:hAnsi="{font}" w:cs="{font}"/>'
    if b: s += '<w:b/><w:bCs/>'
    if i: s += '<w:i/><w:iCs/>'
    if color: s += f'<w:color w:val="{color}"/>'
    if sz: s += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    s += extra + LANG
    return f'<w:rPr>{s}</w:rPr>'


def run(text, **kw):
    return f'<w:r>{rpr(**kw)}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


_TOK = re.compile(r'(\*\*.+?\*\*|\*.+?\*|\^\{.+?\}|_\{.+?\})')


def runs(text, base=None):
    """Marcado ligero: **negrita**, *cursiva*, ^{sup}, _{sub}."""
    base = dict(base or {})
    out = []
    for part in _TOK.split(text):
        if not part: continue
        kw = dict(base)
        if part.startswith('**') and part.endswith('**'):
            kw['b'] = True; part = part[2:-2]
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            kw['i'] = True; part = part[1:-1]
        elif part.startswith('^{'):
            kw['extra'] = '<w:vertAlign w:val="superscript"/>'; part = part[2:-1]
        elif part.startswith('_{'):
            kw['extra'] = '<w:vertAlign w:val="subscript"/>'; part = part[2:-1]
        out.append(run(part, **kw))
    return ''.join(out)


def p_xml(inner, ppr=''):
    return f'<w:p {NS}><w:pPr>{ppr}<w:rPr>{LANG}</w:rPr></w:pPr>{inner}</w:p>'


def body(text, keep_next=False, after=110):
    ppr = ('<w:keepNext/>' if keep_next else '') + f'<w:spacing w:after="{after}" w:line="276" w:lineRule="auto"/><w:jc w:val="both"/>'
    return p_xml(runs(text), ppr)


def body_italic(text):
    base = dict(i=True, font='Calibri', sz=21)
    ppr = '<w:pStyle w:val="NormalWeb"/><w:spacing w:line="276" w:lineRule="auto"/><w:jc w:val="both"/>'
    return (f'<w:p {NS}><w:pPr>{ppr}<w:rPr><w:rFonts w:ascii="Calibri" w:eastAsia="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>'
            f'<w:i/><w:iCs/><w:sz w:val="21"/><w:szCs w:val="21"/>{LANG}</w:rPr></w:pPr>{runs(text, base)}</w:p>')


def h1(text, page_break=False):
    pb = '<w:pageBreakBefore/>' if page_break else ''
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="Heading1"/>{pb}<w:rPr>{LANG}</w:rPr></w:pPr>'
            f'<w:r><w:rPr>{LANG}</w:rPr><w:t>{escape(text)}</w:t></w:r></w:p>')


def h2(text):
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="Heading2"/><w:keepNext/><w:rPr>{LANG}</w:rPr></w:pPr>'
            f'<w:r><w:rPr>{LANG}</w:rPr><w:t>{escape(text)}</w:t></w:r></w:p>')


def subhead(text):
    """Subtítulo no numerado (estilo 'Acrónimos' del original)."""
    return (f'<w:p {NS}><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60"/><w:rPr>{LANG}</w:rPr></w:pPr>'
            + run(text, b=True, color=NAVY, sz=22) + '</w:p>')


def bullet(text):
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
            f'<w:spacing w:after="60" w:line="264" w:lineRule="auto"/><w:jc w:val="both"/><w:rPr>{LANG}</w:rPr></w:pPr>{runs(text)}</w:p>')


def caption(text, keep_next=False):
    kn = '<w:keepNext/>' if keep_next else ''
    return (f'<w:p {NS}><w:pPr>{kn}<w:spacing w:after="200"/><w:jc w:val="center"/><w:rPr>{LANG}</w:rPr></w:pPr>'
            + runs(text, dict(i=True, color=GREY, sz=18)) + '</w:p>')


def table_title(text):
    """Título de tabla sobre la tabla (la numeración de la v2 iba debajo; se conserva debajo)."""
    return caption(text)


def callout(label, text):
    return (f'<w:p {NS}><w:pPr><w:keepLines/><w:pBdr><w:left w:val="single" w:sz="16" w:space="10" w:color="{NAVY}"/></w:pBdr>'
            f'<w:spacing w:before="60" w:after="200" w:line="264" w:lineRule="auto"/><w:ind w:left="220"/><w:rPr>{LANG}</w:rPr></w:pPr>'
            + run(label + ' ', b=True, color=NAVY, sz=20)
            + runs(text, dict(i=True, color='3B3B3B', sz=20)) + '</w:p>')


def page_break():
    return f'<w:p {NS}><w:r><w:br w:type="page"/></w:r></w:p>'


def spacer(after=0):
    return f'<w:p {NS}><w:pPr><w:spacing w:after="{after}"/></w:pPr></w:p>'


def _cell(text, w, hdr=False, fill=None, sz=18, align='left', bold=False, italic=False, keep=False):
    shd = f'<w:shd w:val="clear" w:color="auto" w:fill="{NAVY if hdr else fill}"/>' if (hdr or fill) else ''
    jc = {'left': '', 'center': '<w:jc w:val="center"/>', 'right': '<w:jc w:val="right"/>'}[align]
    if hdr:
        inner = runs(text, dict(b=True, color='FFFFFF', sz=sz))
    else:
        inner = runs(text, dict(color='000000', sz=sz, b=bold, i=italic))
    return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shd}<w:tcMar><w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
            f'<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tcMar><w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr>{"<w:keepNext/>" if keep else ""}<w:spacing w:after="0"/>{jc}<w:rPr>{LANG}</w:rPr></w:pPr>{inner}</w:p></w:tc>')


def table(headers, rows, widths, aligns=None, sz=18, bold_first_col=False, hl_rows=()):
    """Tabla con el formato del informe: encabezado navy/blanco, bandas F2F2F2, bordes simples."""
    tot = sum(widths); keep = len(rows) <= 14
    aligns = aligns or ['left'] + ['center'] * (len(widths) - 1)
    t = (f'<w:tbl {NS}><w:tblPr><w:tblW w:w="{tot}" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>'
         + ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="auto"/>' for s in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV'])
         + '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="10" w:type="dxa"/><w:right w:w="10" w:type="dxa"/></w:tblCellMar>'
         '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr>'
         '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>')
    t += '<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' + ''.join(
        _cell(h, w, hdr=True, sz=sz, align='center' if i else 'left', keep=keep) for i, (h, w) in enumerate(zip(headers, widths))) + '</w:tr>'
    for ri, r in enumerate(rows):
        fill = 'F2F2F2' if ri % 2 == 1 else None
        if ri in hl_rows: fill = 'DCE6F2'
        t += '<w:tr><w:trPr><w:cantSplit/></w:trPr>' + ''.join(
            _cell(str(c), w, fill=fill, sz=sz, align=a, bold=(bold_first_col and ci == 0), keep=(keep or ri == len(rows) - 1))
            for ci, (c, w, a) in enumerate(zip(r, widths, aligns))) + '</w:tr>'
    return t + '</w:tbl>'


class Builder:
    def __init__(self, template, comments_drop=True):
        self.doc = Document(template)
        b = self.doc.element.body
        self.sect = copy.deepcopy(b.find(f'{{{W}}}sectPr'))
        for ch in list(b):
            b.remove(ch)
        self.body = b
        self._docpr = 100
        if comments_drop:
            part = self.doc.part
            for rid, rel in list(part.rels.items()):
                if any(k in rel.reltype for k in ('comments', 'commentsExtended', 'commentsIds', 'commentsExtensible')):
                    del part.rels[rid]
        # elimina imágenes viejas
        for rid, rel in list(self.doc.part.rels.items()):
            if rel.reltype.endswith('/image'):
                del self.doc.part.rels[rid]
        self.xml = []

    def add(self, s):
        self.xml.append(s)

    def figure(self, path, width_in, alt, name):
        rid, _ = self.doc.part.get_or_add_image(path)
        from PIL import Image
        im = Image.open(path); w, h = im.size
        cx = int(width_in * 914400); cy = int(cx * h / w)
        self._docpr += 1
        self.add(
            f'<w:p {NS}><w:pPr><w:keepNext/><w:spacing w:before="100" w:after="40"/><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:noProof/></w:rPr>'
            f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{self._docpr}" name="{escape(name)}" descr="{escape(alt, {chr(34): "&quot;"})}"/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
            f'<pic:nvPicPr><pic:cNvPr id="{self._docpr}" name="{escape(name)}" descr="{escape(alt, {chr(34): "&quot;"})}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')

    def save(self, out):
        b = self.body
        for s in self.xml:
            root = etree.fromstring(f'<w:root {NS}>{s}</w:root>')
            for el in list(root):
                b.append(el)
        b.append(self.sect)
        self.doc.save(out)
