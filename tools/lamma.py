#!/usr/bin/env python3
"""
Lamma Car — local management tool.

Runs on the owner's computer only. It edits the batch files in /batches,
regenerates the static contact pages in /docs (published by GitHub Pages),
and produces QR images and print-ready sticker PDFs in /exports.

Usage:  python tools/lamma.py <command> [options]
        python tools/lamma.py --help
"""

import argparse
import csv
import datetime as dt
import html
import json
import re
import secrets
import shutil
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
TEMPLATES = TOOLS / "templates"
FONTS = TOOLS / "fonts"
DOCS = ROOT / "docs"
BATCHES = ROOT / "batches"
EXPORTS = ROOT / "exports"
CONFIG_FILE = ROOT / "config.json"

PLACEHOLDER = "YOUR-USERNAME"
# 31 characters: lowercase letters and digits without look-alikes (0 o 1 i l).
ALPHABET = "23456789abcdefghjkmnpqrstuvwxyz"
CODE_LEN = 6
CODE_RE = re.compile(r"^[%s]{%d}$" % (ALPHABET, CODE_LEN))
STATUSES = ("available", "assigned", "active", "inactive")

WA_TEXT_AR = "مرحباً، وصلت لرقمك من ملصق لمّة كار على سيارتك."
WA_TEXT_EN = "Hello, I found your number on the Lamma Car sticker on your car."


# --------------------------------------------------------------------------- utils

def die(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def today():
    return dt.date.today().isoformat()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def load_config():
    if not CONFIG_FILE.exists():
        die("config.json is missing. Run: python tools/lamma.py setup --site-url https://USERNAME.github.io/REPOSITORY/")
    cfg = load_json(CONFIG_FILE)
    cfg["site_url"] = normalize_site_url(cfg["site_url"])
    return cfg


def normalize_site_url(url):
    url = url.strip()
    if not url.startswith("https://"):
        die("The site URL must start with https:// (got %r)" % url)
    if not url.endswith("/"):
        url += "/"
    return url


def site_is_configured(cfg):
    return PLACEHOLDER not in cfg["site_url"]


def base_path(site_url):
    """Path part of the site URL, e.g. '/lamma-car/'."""
    p = urllib.parse.urlparse(site_url).path or "/"
    return p if p.endswith("/") else p + "/"


def code_url(site_url, code):
    return "%sq/%s/" % (site_url, code)


def all_batches():
    out = []
    for p in sorted(BATCHES.glob("*.json")):
        out.append((p, load_json(p)))
    return out


def find_code(code):
    code = code.strip().lower()
    for path, batch in all_batches():
        for rec in batch["codes"]:
            if rec["code"] == code:
                return path, batch, rec
    die("Code %r was not found in any batch." % code)


def normalize_phone(raw, country_code):
    s = raw.strip()
    digits = re.sub(r"[^\d+]", "", s)
    if digits.startswith("+"):
        num = digits[1:]
    elif digits.startswith("00"):
        num = digits[2:]
    elif digits.startswith("0"):
        num = country_code + digits[1:]          # local format, e.g. 010… in Egypt
    else:
        num = digits
    if "+" in num or not num.isdigit() or not (8 <= len(num) <= 15):
        die("Phone number %r doesn't look valid. Use international format, e.g. +201001234567." % raw)
    return "+" + num


def format_phone(e164):
    d = e164[1:]
    for cc in ("1", "20", "966", "971", "965", "974", "973", "968", "962", "961", "212", "44"):
        if d.startswith(cc):
            rest = d[len(cc):]
            break
    else:
        cc, rest = d[:3], d[3:]
    if cc == "1" and len(rest) == 10:
        groups = [rest[:3], rest[3:6], rest[6:]]
    elif cc == "20" and len(rest) == 10:
        groups = [rest[:2], rest[2:6], rest[6:]]
    else:
        groups = [rest[i:i + 3] for i in range(0, len(rest), 3)]
        if len(groups) > 1 and len(groups[-1]) == 1:
            groups[-2] += groups.pop()
    return "+" + cc + " " + " ".join(groups)


def first_letter(name):
    for ch in name.strip():
        if ch.isalpha():
            return ch.upper()
    return "•"


# --------------------------------------------------------------------- pages

def tpl(name):
    return (TEMPLATES / name).read_text(encoding="utf-8")


def fill(text, values):
    for k, v in values.items():
        text = text.replace("{{%s}}" % k, v)
    return text


def page(body, assets, title_ar, title_en):
    return fill(tpl("page.html"), {
        "ASSETS": assets,
        "TITLE_AR": html.escape(title_ar),
        "TITLE_EN": html.escape(title_en),
        "BODY": body,
    })


def unavailable_page(assets):
    body = fill(tpl("unavailable.html"), {
        "TITLE_AR": "هذا الرمز غير متاح حالياً",
        "TITLE_EN": "This code isn't available right now",
        "TEXT_AR": "لا توجد بيانات تواصل مفعّلة لهذا الملصق. إذا كان الملصق لك، تواصل مع لمّة كار لتفعيله.",
        "TEXT_EN": "There are no active contact details for this sticker. If it's yours, contact Lamma Car to activate it.",
    })
    return page(body, assets, "غير متاح · لمّة كار", "Unavailable · Lamma Car")


def home_page(assets):
    body = fill(tpl("unavailable.html"), {
        "TITLE_AR": "امسح الملصق للتواصل مع صاحب السيارة",
        "TITLE_EN": "Scan the sticker to contact the vehicle owner",
        "TEXT_AR": "لمّة كار تربطك بصاحب السيارة عبر ملصق QR على الزجاج الخلفي. افتح كاميرا هاتفك ووجّهها نحو الملصق.",
        "TEXT_EN": "Lamma Car connects you with a vehicle's owner through the QR sticker on its rear window. Point your phone camera at the sticker.",
    })
    return page(body, assets, "لمّة كار", "Lamma Car")


def contact_page(rec, assets):
    c = rec["contact"]
    name_ar = c.get("name_ar") or c.get("name_en")
    name_en = c.get("name_en") or c.get("name_ar")
    digits = c["phone"][1:]
    wa = ""
    if c.get("whatsapp", True):
        wa = fill(tpl("whatsapp.html"), {
            "WA_AR": "https://wa.me/%s?text=%s" % (digits, urllib.parse.quote(WA_TEXT_AR)),
            "WA_EN": "https://wa.me/%s?text=%s" % (digits, urllib.parse.quote(WA_TEXT_EN)),
        })
    body = fill(tpl("contact.html"), {
        "INITIAL_AR": html.escape(first_letter(name_ar)),
        "INITIAL_EN": html.escape(first_letter(name_en)),
        "NAME_AR": html.escape(name_ar),
        "NAME_EN": html.escape(name_en),
        "PHONE_DISPLAY": html.escape(format_phone(c["phone"])),
        "TEL": c["phone"],
        "WHATSAPP": wa.rstrip("\n"),
    })
    return page(body, assets, "تواصل مع صاحب السيارة · لمّة كار", "Contact the owner · Lamma Car")


def build_site(cfg, quiet=False):
    """Regenerate every page in /docs from the batch files."""
    qdir = DOCS / "q"
    qdir.mkdir(parents=True, exist_ok=True)
    known = set()
    counts = {s: 0 for s in STATUSES}
    for _, batch in all_batches():
        for rec in batch["codes"]:
            code = rec["code"]
            known.add(code)
            counts[rec["status"]] += 1
            if rec["status"] == "active" and rec.get("contact"):
                out = contact_page(rec, "../../assets/")
            else:
                out = unavailable_page("../../assets/")   # no contact data at all
            target = qdir / code / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(out, encoding="utf-8")
    # Remove folders for codes that are no longer in any batch (should not normally happen).
    for d in qdir.iterdir():
        if d.is_dir() and d.name not in known:
            shutil.rmtree(d)
    (DOCS / "index.html").write_text(home_page("assets/"), encoding="utf-8")
    # 404 page is served for any unknown path, at any depth, so it needs absolute asset paths.
    (DOCS / "404.html").write_text(unavailable_page(base_path(cfg["site_url"]) + "assets/"), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    if not quiet:
        print("Site rebuilt: %d pages (%s)." % (
            len(known), ", ".join("%d %s" % (n, s) for s, n in counts.items())))


# --------------------------------------------------------------------- QR + PDF

def qr_for(url):
    import segno
    return segno.make(url, error="h", micro=False)


def export_batch(cfg, batch, quiet=False):
    import stickers  # local module in /tools
    bid = batch["batch_id"]
    out = EXPORTS / bid
    qr_dir = out / "qr"
    if out.exists():
        shutil.rmtree(out)
    qr_dir.mkdir(parents=True)
    rows = []
    items = []
    for rec in batch["codes"]:
        url = code_url(batch["site_url"], rec["code"])
        q = qr_for(url)
        q.save(str(qr_dir / ("%s.png" % rec["code"])), scale=24, border=4, dark="#000000", light="#ffffff")
        q.save(str(qr_dir / ("%s.svg" % rec["code"])), scale=10, border=4, dark="#000000", light="#ffffff", xmldecl=False)
        rows.append([rec["code"], url, rec["status"], "version %s / error H" % q.version])
        items.append((rec["code"], url, q))
    with open(out / "summary.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "url", "status_at_export", "qr"])
        w.writerows(rows)
    stickers.render_batch(items, out, bid, FONTS)
    lines = [
        "# Batch %s" % bid,
        "",
        "- Created: %s" % batch["created"],
        "- Exported: %s" % today(),
        "- Codes: %d" % len(batch["codes"]),
        "- QR target: %sq/<code>/" % batch["site_url"],
        "- Note: %s" % (batch.get("note") or "-"),
        "",
        "## Files",
        "",
        "- `qr/` — one PNG and one SVG per code (black on white, error correction H).",
        "- `summary.csv` — code, URL and status at export time.",
        "- `stickers-print-MIRRORED.pdf` — one 90 × 130 mm sticker per page, 3 mm bleed, mirrored (reverse print).",
        "- `stickers-print-NORMAL.pdf` — same, not mirrored. This is also the outside view.",
        "- `proof-sheets-A4-MIRRORED.pdf` / `proof-sheets-A4-NORMAL.pdf` — 4 stickers per A4 with crop marks, for test prints.",
        "",
        "Read STICKER_PRINT_GUIDE.md before sending either file to the print shop.",
        "",
    ]
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")
    if not quiet:
        print("Exported %d codes to %s" % (len(items), out.relative_to(ROOT)))


# --------------------------------------------------------------------- commands

def cmd_setup(args):
    url = normalize_site_url(args.site_url)
    cfg = load_json(CONFIG_FILE) if CONFIG_FILE.exists() else {}
    cfg["site_url"] = url
    if args.country_code:
        cfg["default_country_code"] = args.country_code.lstrip("+")
    cfg.setdefault("default_country_code", "20")
    save_json(CONFIG_FILE, cfg)
    print("Site URL set to %s" % url)
    for path, batch in all_batches():
        if batch["site_url"] != url:
            print("NOTE: batch %s keeps its original URL %s (its stickers may already be printed)."
                  % (batch["batch_id"], batch["site_url"]))
    build_site(cfg)


def new_code(taken):
    while True:
        c = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LEN))
        if c not in taken and not c.isdigit():
            taken.add(c)
            return c


def cmd_new_batch(args):
    cfg = load_config()
    if not site_is_configured(cfg):
        die("Set your GitHub Pages URL first: python tools/lamma.py setup --site-url https://USERNAME.github.io/REPOSITORY/")
    if not 1 <= args.count <= 1000:
        die("--count must be between 1 and 1000.")
    taken = {rec["code"] for _, b in all_batches() for rec in b["codes"]}
    if (DOCS / "q").exists():
        taken |= {d.name for d in (DOCS / "q").iterdir()}
    prefix = "LC-%s-" % dt.date.today().strftime("%Y%m%d")
    n = 1
    while (BATCHES / ("%s%02d.json" % (prefix, n))).exists():
        n += 1
    bid = "%s%02d" % (prefix, n)
    batch = {
        "batch_id": bid,
        "created": today(),
        "note": args.note or "",
        "site_url": cfg["site_url"],
        "codes": [{"code": new_code(taken), "status": "available", "contact": None, "updated": today()}
                  for _ in range(args.count)],
    }
    save_json(BATCHES / (bid + ".json"), batch)
    print("Created batch %s with %d codes." % (bid, args.count))
    build_site(cfg)
    export_batch(cfg, batch)


def contact_from_args(args, cfg, existing=None):
    c = dict(existing or {})
    if args.name_ar is not None:
        c["name_ar"] = args.name_ar.strip()
    if args.name_en is not None:
        c["name_en"] = args.name_en.strip()
    if args.phone is not None:
        c["phone"] = normalize_phone(args.phone, cfg.get("default_country_code", "20"))
    if getattr(args, "whatsapp", None) is not None:
        c["whatsapp"] = args.whatsapp
    c.setdefault("whatsapp", True)
    if getattr(args, "consent", False):
        c["consent_date"] = today()
    if not (c.get("name_ar") or c.get("name_en")):
        die("A name is required (--name-ar and/or --name-en).")
    if not c.get("phone"):
        die("A phone number is required (--phone).")
    return c


def cmd_assign(args):
    cfg = load_config()
    path, batch, rec = find_code(args.code)
    if rec["status"] != "available":
        die("Code %s is '%s'. Only 'available' codes can be assigned. Use 'update' to change details."
            % (rec["code"], rec["status"]))
    rec["contact"] = contact_from_args(args, cfg)
    rec["status"] = "assigned"
    rec["updated"] = today()
    save_json(path, batch)
    print("Assigned %s to %s (%s). Status: assigned — not visible yet."
          % (rec["code"], rec["contact"].get("name_ar") or rec["contact"].get("name_en"), rec["contact"]["phone"]))
    if args.activate:
        activate(path, batch, rec, cfg)
    else:
        build_site(cfg)


def cmd_update(args):
    cfg = load_config()
    path, batch, rec = find_code(args.code)
    if not rec.get("contact"):
        die("Code %s has no contact yet. Use 'assign' first." % rec["code"])
    rec["contact"] = contact_from_args(args, cfg, rec["contact"])
    rec["updated"] = today()
    save_json(path, batch)
    print("Updated %s." % rec["code"])
    build_site(cfg)


def activate(path, batch, rec, cfg):
    if not rec.get("contact"):
        die("Code %s has no contact. Assign one first." % rec["code"])
    if not rec["contact"].get("consent_date"):
        die("Code %s has no recorded consent. Once the person has approved public display of their "
            "name and number, run: python tools/lamma.py activate %s --consent" % (rec["code"], rec["code"]))
    rec["status"] = "active"
    rec["updated"] = today()
    save_json(path, batch)
    print("Activated %s → %s" % (rec["code"], code_url(batch["site_url"], rec["code"])))
    build_site(cfg)


def cmd_activate(args):
    cfg = load_config()
    path, batch, rec = find_code(args.code)
    if args.consent and rec.get("contact"):
        rec["contact"]["consent_date"] = today()
    activate(path, batch, rec, cfg)


def cmd_deactivate(args):
    cfg = load_config()
    path, batch, rec = find_code(args.code)
    if rec["status"] == "available":
        die("Code %s was never assigned." % rec["code"])
    rec["status"] = "inactive"
    if args.erase:
        rec["contact"] = None
    rec["updated"] = today()
    save_json(path, batch)
    print("Deactivated %s%s." % (rec["code"], " and erased its contact details" if args.erase else ""))
    build_site(cfg)


def cmd_build(args):
    build_site(load_config())


def cmd_export(args):
    cfg = load_config()
    batches = all_batches()
    if args.batch == "all":
        chosen = [b for _, b in batches]
    else:
        chosen = [b for _, b in batches if b["batch_id"] == args.batch]
        if not chosen:
            die("Batch %r not found. Existing: %s" % (args.batch, ", ".join(b["batch_id"] for _, b in batches)))
    for b in chosen:
        export_batch(cfg, b)


def cmd_master(args):
    """Sticker master artwork. Without a code, the QR is a sample that opens the site's landing page."""
    import stickers
    cfg = load_config()
    if args.code:
        path, batch, rec = find_code(args.code)
        label, url = rec["code"], code_url(batch["site_url"], rec["code"])
    else:
        label, url = "sample", cfg["site_url"]
    stickers.render_master(label, qr_for(url), ROOT / "stickers", FONTS)
    print("Sticker master files written to stickers/ (QR → %s)" % url)


def cmd_list(args):
    for _, b in all_batches():
        if args.batch and b["batch_id"] != args.batch:
            continue
        counts = {s: sum(1 for r in b["codes"] if r["status"] == s) for s in STATUSES}
        print("\n%s  (%s%s)  %s" % (b["batch_id"], b["created"], "",
                                    "  ".join("%s:%d" % kv for kv in counts.items())))
        for r in b["codes"]:
            if args.status and r["status"] != args.status:
                continue
            c = r.get("contact") or {}
            who = c.get("name_ar") or c.get("name_en") or ""
            print("  %s  %-9s  %s %s" % (r["code"], r["status"], who, c.get("phone", "")))


def cmd_show(args):
    path, batch, rec = find_code(args.code)
    print(json.dumps(dict(rec, batch=batch["batch_id"], url=code_url(batch["site_url"], rec["code"])),
                     ensure_ascii=False, indent=2))


def cmd_check(args):
    cfg = load_config()
    problems = []
    seen = {}
    for path, b in all_batches():
        if b["site_url"] != cfg["site_url"]:
            problems.append("batch %s points to %s but config.json says %s"
                            % (b["batch_id"], b["site_url"], cfg["site_url"]))
        for r in b["codes"]:
            code = r["code"]
            if not CODE_RE.match(code):
                problems.append("bad code format: %s" % code)
            if code in seen:
                problems.append("duplicate code %s in %s and %s" % (code, seen[code], b["batch_id"]))
            seen[code] = b["batch_id"]
            if r["status"] not in STATUSES:
                problems.append("%s has unknown status %r" % (code, r["status"]))
            if r["status"] in ("assigned", "active") and not r.get("contact"):
                problems.append("%s is %s but has no contact" % (code, r["status"]))
            if r["status"] == "active" and not (r.get("contact") or {}).get("consent_date"):
                problems.append("%s is active without recorded consent" % code)
            page_file = DOCS / "q" / code / "index.html"
            if not page_file.exists():
                problems.append("%s has no page — run: python tools/lamma.py build" % code)
            else:
                text = page_file.read_text(encoding="utf-8")
                has_tel = "tel:" in text
                if r["status"] == "active" and not has_tel:
                    problems.append("%s is active but its page shows no contact — run build" % code)
                if r["status"] != "active" and has_tel:
                    problems.append("%s is %s but its page still shows contact details — run build" % (code, r["status"]))
    if not site_is_configured(cfg):
        problems.append("config.json still has the placeholder site URL — run setup")
    if problems:
        print("Problems found:")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("All good: %d codes checked." % len(seen))


def main():
    ap = argparse.ArgumentParser(prog="lamma", description="Lamma Car — batch, QR and page management (local only).")
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("setup", help="Set the GitHub Pages URL (do this once).")
    p.add_argument("--site-url", required=True, help="e.g. https://USERNAME.github.io/REPOSITORY/")
    p.add_argument("--country-code", help="Default country code for local numbers (default 20 = Egypt).")
    p.set_defaults(func=cmd_setup)

    p = sp.add_parser("new-batch", help="Create a batch of new codes, with QR images and sticker PDFs.")
    p.add_argument("--count", type=int, required=True)
    p.add_argument("--note", help="Free text, e.g. print shop or order reference.")
    p.set_defaults(func=cmd_new_batch)

    def contact_args(p, required):
        p.add_argument("code")
        p.add_argument("--name-ar", help="Name in Arabic.")
        p.add_argument("--name-en", help="Name in English.")
        p.add_argument("--phone", required=required, help="Mobile, e.g. 01001234567 or +201001234567.")
        g = p.add_mutually_exclusive_group()
        g.add_argument("--whatsapp", dest="whatsapp", action="store_true", default=None, help="Show the WhatsApp button (default).")
        g.add_argument("--no-whatsapp", dest="whatsapp", action="store_false", help="Hide the WhatsApp button.")
        p.add_argument("--consent", action="store_true", help="Record today's date as the date the person approved public display.")

    p = sp.add_parser("assign", help="Attach a contact to an available code (not visible until activated).")
    contact_args(p, True)
    p.add_argument("--activate", action="store_true", help="Activate immediately (needs --consent).")
    p.set_defaults(func=cmd_assign)

    p = sp.add_parser("update", help="Change the name, phone or WhatsApp setting of a code.")
    contact_args(p, False)
    p.set_defaults(func=cmd_update)

    p = sp.add_parser("activate", help="Publish the contact page for a code.")
    p.add_argument("code")
    p.add_argument("--consent", action="store_true", help="Record that the person approved public display today.")
    p.set_defaults(func=cmd_activate)

    p = sp.add_parser("deactivate", help="Hide a code's contact page (shows 'unavailable').")
    p.add_argument("code")
    p.add_argument("--erase", action="store_true", help="Also delete the stored name and phone.")
    p.set_defaults(func=cmd_deactivate)

    p = sp.add_parser("build", help="Regenerate all pages in /docs from the batch files.")
    p.set_defaults(func=cmd_build)

    p = sp.add_parser("export", help="Regenerate QR images and PDFs for a batch ('all' for every batch).")
    p.add_argument("batch")
    p.set_defaults(func=cmd_export)

    p = sp.add_parser("master", help="Rebuild the sticker master files in /stickers (sample QR, or one code's QR).")
    p.add_argument("code", nargs="?")
    p.set_defaults(func=cmd_master)

    p = sp.add_parser("list", help="List batches and codes.")
    p.add_argument("batch", nargs="?")
    p.add_argument("--status", choices=STATUSES)
    p.set_defaults(func=cmd_list)

    p = sp.add_parser("show", help="Show one code's record and URL.")
    p.add_argument("code")
    p.set_defaults(func=cmd_show)

    p = sp.add_parser("check", help="Validate batches and generated pages before publishing.")
    p.set_defaults(func=cmd_check)

    args = ap.parse_args()
    sys.path.insert(0, str(TOOLS))
    args.func(args)


if __name__ == "__main__":
    main()
