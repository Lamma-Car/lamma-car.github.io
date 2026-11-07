"""
Lamma Car sticker artwork (90 x 130 mm, portrait).

The artwork is drawn as vectors with reportlab. "NORMAL" is the design as it
must look from OUTSIDE the car. "MIRRORED" is the same artwork flipped
left-to-right for reverse (second-surface) printing on clear film.
See STICKER_PRINT_GUIDE.md for which one a print shop needs.

Uses the official Lamma Car logo (tools/brand/lamma-logo.png) and its colours.
"""

from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.colors import CMYKColor, CMYKColorSep
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = 90.0, 130.0          # trim size, mm
BLEED = 3.0                 # mm
CORNER = 6.0                # die-cut corner radius, mm
QR_SIZE = 62.0             # mm, QR modules only
QR_Y = 21.5                # mm, bottom edge of the QR
BAND = 13.5                # mm, navy footer band height
LOGO_W = 64.0              # mm
LOGO_FILE = Path(__file__).resolve().parent / "brand" / "lamma-logo.png"

# Brand colours from the official logo: navy #0E1428, orange #FD5D27.
NAVY = CMYKColor(0.90, 0.80, 0.40, 0.75)
ORANGE = CMYKColor(0, 0.75, 0.90, 0)
WHITE = CMYKColor(0, 0, 0, 0)
QR_BLACK = CMYKColor(0, 0, 0, 1)              # 100% K only: sharp module edges
MUTED = CMYKColor(0.45, 0.35, 0.20, 0.25)
CUT = CMYKColorSep(0, 1, 0, 0, spotName="CutContour")

_reshaper = arabic_reshaper.ArabicReshaper(configuration={"delete_harakat": False, "support_ligatures": True})
_fonts_ready = False
_logo_reader = None
LOGO_RATIO = 597 / 1507


def _logo():
    global _logo_reader, LOGO_RATIO
    if _logo_reader is None:
        from reportlab.lib.utils import ImageReader
        _logo_reader = ImageReader(str(LOGO_FILE))
        w, h = _logo_reader.getSize()
        LOGO_RATIO = h / w
    return _logo_reader


def _fonts(font_dir):
    global _fonts_ready
    if not _fonts_ready:
        font_dir = Path(font_dir)
        pdfmetrics.registerFont(TTFont("Plex", str(font_dir / "IBMPlexSansArabic-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("Plex-Bold", str(font_dir / "IBMPlexSansArabic-Bold.ttf")))
        _fonts_ready = True


def ar(text):
    return get_display(_reshaper.reshape(text))


def _center(c, text, font, size, y, color, max_w=None, tracking=0):
    while max_w and pdfmetrics.stringWidth(text, font, size) + tracking * (len(text) - 1) > max_w * mm:
        size -= 0.25
    c.setFillColor(color)
    if tracking:
        t = c.beginText()
        t.setFont(font, size)
        t.setCharSpace(tracking)
        w = pdfmetrics.stringWidth(text, font, size) + tracking * (len(text) - 1)
        t.setTextOrigin(W / 2 * mm - w / 2, y * mm)
        t.textOut(text)
        t.setCharSpace(0)  # Tc persists after ET; reset it
        c.drawText(t)
    else:
        c.setFont(font, size)
        c.drawCentredString(W / 2 * mm, y * mm, text)


def _qr(c, qr, x, y, size):
    """Draw QR modules (no border) as merged black runs inside a size x size mm square."""
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    m = size / n
    c.setFillColor(QR_BLACK)
    p = c.beginPath()
    for r, row in enumerate(matrix):
        col = 0
        while col < n:
            if row[col]:
                start = col
                while col < n and row[col]:
                    col += 1
                # tiny overlap avoids hairline gaps between rows in some RIPs
                p.rect((x + start * m) * mm, (y + (n - r - 1) * m) * mm,
                       (col - start) * m * mm, (m + 0.01) * mm)
            else:
                col += 1
    c.drawPath(p, stroke=0, fill=1)


def draw_sticker(c, ox, oy, code, qr, mirrored=False, bleed=BLEED):
    """Draw one sticker whose trim box starts at (ox, oy) mm."""
    c.saveState()
    if mirrored:
        c.translate((ox + W) * mm, oy * mm)
        c.scale(-1, 1)
    else:
        c.translate(ox * mm, oy * mm)

    # white background with bleed
    c.setFillColor(WHITE)
    c.rect(-bleed * mm, -bleed * mm, (W + 2 * bleed) * mm, (H + 2 * bleed) * mm, stroke=0, fill=1)

    # official logo (raster, transparent background)
    lw = LOGO_W
    lh = lw * LOGO_RATIO
    c.drawImage(_logo(), (W - lw) / 2 * mm, (H - 4.5 - lh) * mm, lw * mm, lh * mm, mask="auto")

    # call to action
    _center(c, ar("امسح الرمز للتواصل مع صاحب السيارة"), "Plex-Bold", 12.2, 93.2, NAVY, max_w=80)
    _center(c, "Scan to contact the vehicle owner", "Plex", 8.2, 88.9, MUTED, max_w=80)

    # QR on white; the white around it is the quiet zone (>= 4 modules)
    _qr(c, qr, (W - QR_SIZE) / 2, QR_Y, QR_SIZE)

    # navy footer band with the code
    c.setFillColor(NAVY)
    c.rect(-bleed * mm, -bleed * mm, (W + 2 * bleed) * mm, (BAND + bleed) * mm, stroke=0, fill=1)
    c.setFillColor(ORANGE)
    c.rect(-bleed * mm, BAND * mm, (W + 2 * bleed) * mm, 1.2 * mm, stroke=0, fill=1)
    _center(c, code, "Plex-Bold", 10, 5.4, WHITE, tracking=3)
    c.restoreState()


def _set_boxes(c, page_w, page_h, bleed):
    c.setBleedBox((0, 0, page_w * mm, page_h * mm))
    c.setTrimBox((bleed * mm, bleed * mm, (page_w - bleed) * mm, (page_h - bleed) * mm))


def single_pdf(path, items, mirrored, title):
    """One sticker per page: 96 x 136 mm page = 90 x 130 trim + 3 mm bleed."""
    pw, ph = W + 2 * BLEED, H + 2 * BLEED
    c = canvas.Canvas(str(path), pagesize=(pw * mm, ph * mm))
    c.setTitle(title)
    c.setAuthor("Lamma Car")
    for code, _url, qr in items:
        _set_boxes(c, pw, ph, BLEED)
        draw_sticker(c, BLEED, BLEED, code, qr, mirrored)
        c.showPage()
    c.save()


def _crop_marks(c, x, y):
    c.setStrokeColor(CMYKColor(0, 0, 0, 1))
    c.setLineWidth(0.25)
    L, off = 4.0, BLEED + 1.0
    for cx in (x, x + W):
        for cy, d in ((y, -1), (y + H, 1)):
            c.line(cx * mm, (cy + d * off) * mm, cx * mm, (cy + d * (off + L)) * mm)
    for cy in (y, y + H):
        for cx, d in ((x, -1), (x + W, 1)):
            c.line((cx + d * off) * mm, cy * mm, (cx + d * (off + L)) * mm, cy * mm)


def sheet_pdf(path, items, mirrored, title, label):
    """A4 portrait, 2 x 2 stickers with bleed and crop marks — for proofs and small runs."""
    from reportlab.lib.pagesizes import A4
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle(title)
    c.setAuthor("Lamma Car")
    aw, ah = 210.0, 297.0
    cell_w, cell_h = W + 2 * BLEED + 6, H + 2 * BLEED + 6
    x0 = (aw - 2 * cell_w) / 2 + 3 + BLEED
    y0 = (ah - 2 * cell_h) / 2 + 3 + BLEED
    slots = [(x0, y0 + cell_h), (x0 + cell_w, y0 + cell_h), (x0, y0), (x0 + cell_w, y0)]
    pages = [items[i:i + 4] for i in range(0, len(items), 4)]
    for pi, chunk in enumerate(pages, 1):
        for (code, _url, qr), (sx, sy) in zip(chunk, slots):
            draw_sticker(c, sx, sy, code, qr, mirrored)
            _crop_marks(c, sx, sy)
        c.setFillColor(CMYKColor(0, 0, 0, 0.7))
        c.setFont("Plex", 7)
        c.drawString(10 * mm, 6 * mm, "%s  ·  page %d/%d  ·  %s  ·  trim 90 x 130 mm, print at 100%% (no scaling)"
                     % (label, pi, len(pages), "MIRRORED (reverse print)" if mirrored else "NORMAL (outside view)"))
        c.showPage()
    c.save()


def render_batch(items, out_dir, batch_id, font_dir):
    _fonts(font_dir)
    out_dir = Path(out_dir)
    for mirrored, tag in ((True, "MIRRORED"), (False, "NORMAL")):
        single_pdf(out_dir / ("stickers-print-%s.pdf" % tag), items, mirrored,
                   "Lamma Car stickers %s (%s)" % (batch_id, tag))
        sheet_pdf(out_dir / ("proof-sheets-A4-%s.pdf" % tag), items, mirrored,
                  "Lamma Car proof sheets %s (%s)" % (batch_id, tag), batch_id)


def dieline_pdf(path):
    pw, ph = W + 2 * BLEED, H + 2 * BLEED
    c = canvas.Canvas(str(path), pagesize=(pw * mm, ph * mm))
    c.setTitle("Lamma Car sticker die line (CutContour)")
    _set_boxes(c, pw, ph, BLEED)
    c.setStrokeColor(CUT)
    c.setLineWidth(0.25)
    c.roundRect(BLEED * mm, BLEED * mm, W * mm, H * mm, CORNER * mm, stroke=1, fill=0)
    c.showPage()
    c.save()


def render_master(code, qr, out_dir, font_dir):
    """Master artwork files for the print shop and for approval."""
    _fonts(font_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    item = [(code, None, qr)]
    single_pdf(out_dir / "lamma-sticker-90x130-print-MIRRORED.pdf", item, True, "Lamma Car sticker master — MIRRORED")
    single_pdf(out_dir / "lamma-sticker-90x130-print-NORMAL.pdf", item, False, "Lamma Car sticker master — NORMAL")
    # outside view: trim size only, no bleed — what people see through the glass
    c = canvas.Canvas(str(out_dir / "lamma-sticker-90x130-outside-view.pdf"), pagesize=(W * mm, H * mm))
    c.setTitle("Lamma Car sticker — outside view")
    p = c.beginPath()
    p.roundRect(0, 0, W * mm, H * mm, CORNER * mm)
    c.clipPath(p, stroke=0, fill=0)
    draw_sticker(c, 0, 0, code, qr, False, bleed=0)
    c.showPage()
    c.save()
    dieline_pdf(out_dir / "lamma-sticker-90x130-dieline.pdf")
