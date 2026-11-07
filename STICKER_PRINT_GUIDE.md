# Sticker print guide

**Size:** 90 × 130 mm portrait · **Bleed:** 3 mm on every side (PDF page 96 × 136 mm) · **Corners:** 6 mm radius · **Placement:** inside of the rear windshield, read from outside.

## Files

| File | Use |
|---|---|
| `stickers/lamma-sticker-90x130-outside-view.pdf` | How the sticker must look from outside. Use for approval. |
| `stickers/lamma-sticker-90x130-print-NORMAL.pdf` | Print master, not mirrored. |
| `stickers/lamma-sticker-90x130-print-MIRRORED.pdf` | Print master, mirrored left-to-right. |
| `stickers/lamma-sticker-90x130-dieline.pdf` | Cut line as a `CutContour` spot colour. |
| `stickers/lamma-sticker-preview.png` | Digital preview. |
| `exports/<batch>/stickers-print-*.pdf` | The real batch: one unique sticker per page. |
| `exports/<batch>/proof-sheets-A4-*.pdf` | Four per A4 with crop marks, for test prints. |

The masters use a **sample** QR that opens the landing page, and show the word "sample" where a code normally goes. They are for approval and print-shop setup only. For production, always send the batch files from `exports/<batch>/` — every page there has its own unique code.

## Mirrored or normal? It depends on where the ink sits

The outside viewer must see the artwork the right way round. Which file achieves that depends on how the print shop builds the sticker. Ask them this one question:

> "Seen from outside the car, will people look **through the clear film** to reach the ink, or is the ink **on the glass side** of the film?"

| Construction (from outside → inside) | Ink is seen… | Send |
|---|---|---|
| glass · adhesive · **film** · ink · white backing — *reverse / second-surface print on clear film* | through the film | **MIRRORED** |
| glass · adhesive · ink · white backing · film — *face-adhesive, printed on the glass side* | directly | **NORMAL** |
| glass · **opaque printed vinyl**, adhesive on the printed face | directly | **NORMAL** |

If the shop can't answer clearly, don't guess. Do the test below with both files.

## White layer — required

The car's interior is dark. A QR printed in black on clear film has no contrast and won't scan. Ask for an **opaque white layer behind the whole artwork**, as seen from outside (a "white flood" or "white underbase"). The white background of this design also needs it: without white ink, "white" areas on clear film are simply transparent.

## Test before the full run (mandatory)

1. Print one page of the batch's `proof-sheets-A4` file (or one real sticker) in each orientation.
2. Fix it to the **inside** of a rear windshield the way it will be installed.
3. From **outside**, check: Arabic text reads right-to-left correctly, English isn't reversed, and the code under the QR reads normally (e.g. `k7m3qx`), not mirrored.
4. Scan it from outside with an iPhone camera and an Android camera, at about 30 cm, 60 cm and 1 m, in daylight and in shade.
5. Check that it opens the correct `/q/<code>/` page.

Only approve the run when all of that works. Some phone cameras can read a mirrored QR, so "it scanned" alone does not prove the orientation is right — always check the text too.

## QR readability

- Error correction **H** (about 30% of the code can be dirty or covered and it still scans).
- The QR is about 62–63 mm wide; each module is about 1.5 mm. That reads comfortably from 20 cm to well over 1 m.
- Pure black (100% K) modules on a white panel, with a 4-module quiet zone inside the white panel. Don't let the shop shrink the panel, add a border or change the colours.
- Print at **100% scale**. "Fit to page" changes the size.
- Install in a clean, flat area **between the rear defroster heater lines** if possible, and below any dark tint band at the top of the glass. Heavily tinted glass reduces contrast: test on the darkest glass you expect.
- Clean the glass with alcohol before application, and press out bubbles across the QR area.
- Matte or anti-glare lamination reduces reflections; glossy finish facing the glass is fine.

## Print specification to send the shop

> 90 × 130 mm sticker, portrait, 6 mm rounded corners (die line attached). For inside-of-glass application, readable from outside. PDF includes 3 mm bleed and TrimBox. Full-colour CMYK with an opaque white layer behind all artwork. Do not scale. One unique QR code per sticker — keep the page order. Supply one proof before the full run.

## Changing the design

The layout is in `tools/stickers.py` (colours at the top, positions in `draw_sticker`); the logo is `tools/brand/lamma-logo.png`. After changes run `python tools/lamma.py master` and `python tools/lamma.py export <batch>`, and re-test readability.
