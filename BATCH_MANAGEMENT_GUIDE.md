# Batch management guide

Everything here runs on your own computer. Nothing on the website can change data — a person scanning a sticker only ever receives one static page.

## The admin page (recommended)

`tools/admin.html` is a management page that runs in your browser on your own computer. It is **not** part of the website (GitHub Pages only publishes `docs/`), and it can do nothing without your GitHub token.

**Open it:** double-click `tools/admin.html` in your unzipped `lamma-car` folder (Chrome, Edge or Safari, internet connection needed).

**Connect (first time):**

1. On GitHub: your photo → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens** → **Generate new token**.
2. **Resource owner:** `Lamma-Car`. **Repository access:** Only select repositories → `lamma-car.github.io`.
3. **Repository permissions** → **Contents: Read and write**. Nothing else.
4. Generate, copy the token, paste it into the admin page, click **اتصال**.
   - Tick "افتكر الـ Token" only on your own computer.
   - If GitHub says the token is pending approval, an owner of the `Lamma-Car` organization must approve it (Organization settings → Personal access tokens).

**What you can do:**

| Task | How |
|---|---|
| New batch of codes | **+ دفعة أكواد جديدة** → number of codes → **إنشاء** → **نشر على الموقع** |
| Print files | On the batch card: **ملصقات للطباعة · معكوس** / **عادي** (one sticker per page), **A4 تجربة** (4 per A4 with crop marks), **صور QR (ZIP)** (PNG + SVG + summary CSV) |
| Add a customer | Find the sticker's code → **إضافة عميل** → name, mobile, tick the consent box → **حفظ** → **نشر على الموقع** |
| Edit / stop / remove | **تعديل**, **إيقاف**, **تفعيل**, **مسح البيانات** on the code's row, then **نشر على الموقع** |
| See a code's QR | **QR** on the row (with PNG download) |

Changes stay on your screen (orange bar) until you click **نشر على الموقع**, which saves everything to GitHub in one step. The site updates within 1–10 minutes.

The page uses the same templates, rules and file format as `tools/lamma.py`, so you can use either. If someone else changed the same batch on GitHub in the meantime, the page refuses to publish and asks you to reload rather than overwrite.

Everything below describes the command-line tool, which does the same things.

## One-time setup

```bash
pip install -r tools/requirements.txt
```

The site address (`https://lamma-car.github.io/`) is already saved in `config.json`. Default country code for local numbers is **20 (Egypt)**, so `01001234567` is saved as `+201001234567`. Numbers written with `+` or `00` are kept as typed.

## Code statuses

| Status | Meaning | What a scan shows |
|---|---|---|
| `available` | Printed or printable, not given to anyone | Unavailable |
| `assigned` | Contact saved, not yet published | Unavailable |
| `active` | Published | Name, number, Call, WhatsApp |
| `inactive` | Switched off | Unavailable |

A code's URL never changes. A code is never moved to a different person: the physical sticker is still on the first car. For a new customer, use a new code.

## 1. Create a batch

```bash
python tools/lamma.py new-batch --count 40 --note "Print run 1 — Shop name, order 123"
```

This creates:

- `batches/LC-YYYYMMDD-NN.json` — the record of which codes belong to the batch;
- `docs/q/<code>/index.html` for every code (all "unavailable" for now);
- `exports/LC-YYYYMMDD-NN/` with:
  - `qr/<code>.png` and `qr/<code>.svg` — every QR on its own;
  - `summary.csv` — code, full URL and status (opens in Excel);
  - `stickers-print-MIRRORED.pdf` and `stickers-print-NORMAL.pdf` — one 90 × 130 mm sticker per page with 3 mm bleed, for the print shop;
  - `proof-sheets-A4-MIRRORED.pdf` and `proof-sheets-A4-NORMAL.pdf` — four stickers per A4 page with crop marks, for test prints and small runs;
  - `README.md` — batch summary.

Read STICKER_PRINT_GUIDE.md to decide between MIRRORED and NORMAL. Commit and push after creating the batch so the "unavailable" pages exist before stickers go out.

## 2. Add a new contact and activate a code

When a customer receives sticker `k7m3qx` and agrees to have their name and number shown publicly:

```bash
python tools/lamma.py assign k7m3qx --name-ar "أحمد علي" --name-en "Ahmed Ali" --phone 01001234567 --consent --activate
```

Or in two steps (e.g. register now, publish after they confirm):

```bash
python tools/lamma.py assign k7m3qx --name-ar "أحمد علي" --name-en "Ahmed Ali" --phone 01001234567
python tools/lamma.py activate k7m3qx --consent
```

- Give at least one name. If only one language is given, it's used for both.
- `--no-whatsapp` hides the WhatsApp button for people who don't use it.
- `--consent` records today's date as the approval date. Activation is refused without it.

Then publish:

```bash
python tools/lamma.py check
git add . && git commit -m "Activate k7m3qx" && git push
```

(Or upload the `batches` and `docs` folders on github.com — see DEPLOYMENT_GUIDE.md, Part 6.) Scan the sticker after a few minutes to confirm.

## 3. Update details

```bash
python tools/lamma.py update k7m3qx --phone 01112223344
python tools/lamma.py update k7m3qx --name-en "Ahmed M. Ali" --no-whatsapp
```

The URL and the printed sticker stay the same. Commit and push.

## 4. Deactivate

```bash
python tools/lamma.py deactivate k7m3qx            # hide the page, keep the record
python tools/lamma.py deactivate k7m3qx --erase    # hide the page and delete name + number
python tools/lamma.py activate k7m3qx --consent    # switch back on (if not erased)
```

Use `--erase` when someone sells the car, asks to be removed or withdraws consent. Note that git history still contains old versions — see PRIVACY_GUIDE.md for full removal.

## 5. Look things up

```bash
python tools/lamma.py list                         # all batches
python tools/lamma.py list LC-20261201-01 --status available
python tools/lamma.py show k7m3qx
```

## 6. Re-export or rebuild

```bash
python tools/lamma.py export LC-20261201-01        # QR images + PDFs again (e.g. after a design change)
python tools/lamma.py export all
python tools/lamma.py build                        # pages again (e.g. after editing templates or CSS)
python tools/lamma.py master                       # sticker master files in stickers/
```

Exports always use the URL stored in the batch, so reprinting an old batch gives identical QR codes.

## Batch file format

```json
{
  "batch_id": "LC-20261201-01",
  "created": "2026-12-01",
  "note": "Print run 1",
  "site_url": "https://lamma-car.github.io/",
  "codes": [
    { "code": "k7m3qx", "status": "active", "updated": "2026-12-03",
      "contact": { "name_ar": "أحمد علي", "name_en": "Ahmed Ali",
                   "phone": "+201001234567", "whatsapp": true, "consent_date": "2026-12-03" } },
    { "code": "p4tz9w", "status": "available", "contact": null, "updated": "2026-12-01" }
  ]
}
```

You can edit these files by hand if needed; run `python tools/lamma.py check` and `build` afterwards.

## Before every push

```bash
python tools/lamma.py check
```

It confirms codes are unique and well-formed, active codes have consent, every code has a page, active pages show contact details and non-active pages don't.
