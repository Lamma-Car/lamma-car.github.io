# Lamma Car · لمّة كار

One QR code → one contact page → one registered person.

A sticker on the inside of a car's rear windshield carries a QR code. Scanning it opens a small contact card with the owner's name, mobile number, a **Call** button and a **WhatsApp** button. Nothing else.

The whole product is static files hosted free on **GitHub Pages**. There is no server, database, login or build step on GitHub. All management (batches, assigning contacts, QR images, sticker PDFs) happens on the owner's own computer: in the admin page `tools/admin.html` (opens in the browser and publishes straight to GitHub), or with the equivalent Python script.

## How it works

```
batches/LC-….json  ──►  python tools/lamma.py build  ──►  docs/q/<code>/index.html  ──►  GitHub Pages
 (source of truth)        (run on your computer)          (one static page per code)       (public)
```

- Every code gets its own folder: `docs/q/<code>/index.html`. A QR URL is `https://lamma-car.github.io/q/<code>/`.
- **Active** codes get a contact page. **Available, assigned and inactive** codes get an "unavailable" page that contains no contact data at all.
- Unknown codes hit `docs/404.html`, which shows the same "unavailable" message, so nobody can tell a real code from a made-up one.
- Each page holds only its own record. There is no list, search or shared data file on the site.
- Codes are 6 random characters (e.g. `k7m3qx`) from 31 unambiguous letters and digits (~887 million combinations), so they cannot be guessed by counting.

## Repository structure

```
lamma-car/
├── docs/                      ← the published website (GitHub Pages: branch main, folder /docs)
│   ├── index.html             neutral landing page (no records listed)
│   ├── 404.html               "unavailable" page for unknown codes
│   ├── .nojekyll
│   ├── assets/css/lamma.css   contact card styles (RTL/LTR, brand colours)
│   ├── assets/fonts/          IBM Plex Sans Arabic, subset WOFF2 (~37 KB each, OFL licence)
│   ├── assets/images/         official logo (web) and icon
│   └── q/<code>/index.html    one page per code (created by the tool — don't edit by hand)
├── batches/                   one JSON file per batch: codes, statuses, contacts
├── exports/<batch>/           QR PNG/SVG, summary.csv, sticker PDFs (generated)
├── stickers/                  sticker master artwork, die line and preview
├── tools/
│   ├── admin.html             admin page: open on your computer, publishes via the GitHub API
│   ├── lamma.py               the same management tasks from the command line
│   ├── stickers.py            sticker artwork and PDF layout
│   ├── templates/             HTML templates for the pages
│   ├── fonts/                 fonts used in the PDFs
│   ├── brand/                 official logo, full resolution, and the sticker base used by admin.html
│   └── requirements.txt
├── config.json                your GitHub Pages URL and default country code
├── DEPLOYMENT_GUIDE.md        step-by-step upload and GitHub Pages setup
├── BATCH_MANAGEMENT_GUIDE.md  batches, contacts, activation, exports
├── STICKER_PRINT_GUIDE.md     mirrored vs normal printing, readability
└── PRIVACY_GUIDE.md           what is public and how to handle consent
```

## Quick start

Live address: **https://lamma-car.github.io/** (already set in `config.json`).

1. Upload and publish: follow **DEPLOYMENT_GUIDE.md** step by step.
2. Double-click **`tools/admin.html`**, connect with a GitHub token (BATCH_MANAGEMENT_GUIDE.md explains how to create one), then:
   - **+ دفعة أكواد جديدة** → **نشر على الموقع** → download the sticker PDFs;
   - **إضافة عميل** on a code → **نشر على الموقع**.

Prefer the command line? The same tasks:

```bash
pip install -r tools/requirements.txt
python tools/lamma.py new-batch --count 40 --note "First print run"
python tools/lamma.py assign <code> --name-ar "…" --name-en "…" --phone 01001234567 --consent --activate
python tools/lamma.py check
```

then upload the changed `batches`, `docs` and `exports` folders. On Windows use `py` instead of `python` if `python` isn't recognised.

## Command-line tool (`tools/lamma.py`)

| Command | What it does |
|---|---|
| `setup --site-url URL` | Change the GitHub Pages URL (already set — only for a new repository before any printing). |
| `new-batch --count N [--note TEXT]` | New codes + pages + QR images + sticker PDFs. |
| `assign CODE --name-ar --name-en --phone [--consent] [--activate] [--no-whatsapp]` | Attach a contact to an available code. |
| `activate CODE [--consent]` | Publish the contact page. Needs recorded consent. |
| `update CODE [--name-ar] [--name-en] [--phone] [--whatsapp/--no-whatsapp]` | Change details. URL stays the same. |
| `deactivate CODE [--erase]` | Show "unavailable". `--erase` also deletes the stored name and number. |
| `export BATCH` or `export all` | Re-create QR images and PDFs. |
| `master [CODE]` | Re-create the sticker master files in `stickers/` (sample QR, or a given code). |
| `list [BATCH] [--status S]`, `show CODE` | Look things up. |
| `build` | Re-generate every page (the other commands already do this). |
| `check` | Validate everything before you publish. |

## What's in this package

Production-ready, with **no codes and no contact data**. `batches/` and `exports/` are empty until you run `new-batch`; `docs/` contains only the landing page, the "unavailable" 404 page and the shared assets. The sticker masters in `stickers/` use a sample QR that opens the landing page; real stickers come from each batch's export.

## Branding

- **Logo:** the official Lamma Car logo, not redrawn. The tagline "Find it. Sell it. Easy." is removed everywhere at the owner's request; only the mark and the "Lamma Car" wordmark are used.
  - `tools/brand/lamma-logo.png` — full resolution, used on the stickers.
  - `docs/assets/images/lamma-logo.png` — web version (10 KB).
  - `docs/assets/images/icon.png` — browser/phone icon made from the logo's L mark.
- **Colours** (taken from the logo): navy `#0E1428`, orange `#FD5D27`. WhatsApp button stays WhatsApp green so people recognise it.
- **Font:** IBM Plex Sans Arabic (Arabic + English, OFL licence).
- **Web page:** navy background, white card with the logo, navy Call button, green WhatsApp button, orange accents.
- **Sticker:** white background (so the navy logo reads clearly through the glass), logo at the top, QR in the middle, navy band with the code at the bottom.

To swap the logo later, replace both PNG files with the same names, then run `build`, `master` and `export all`.
