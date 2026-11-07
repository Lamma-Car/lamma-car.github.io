# Upload and deployment guide

**Live site address (after deployment):** https://shamelbyvezeeta.github.io/lamma-car/
**QR code addresses:** `https://shamelbyvezeeta.github.io/lamma-car/q/<code>/`

Everything in this package is already set to this address. You don't need to create or edit any file.

---

## Part 1 — Create the repository

1. Sign in to github.com with an account that can create repositories in **shamelbyvezeeta**.
2. Click **+** (top right) → **New repository**.
3. **Owner:** `shamelbyvezeeta` · **Repository name:** `lamma-car` (exactly, lowercase).
4. **Visibility:** Public.
5. Leave "Add a README", ".gitignore" and "license" **unticked**.
6. Click **Create repository**.

## Part 2 — Upload the files

1. Unzip `lamma-car.zip` on your computer. You get a folder named `lamma-car`.
2. Open that folder. Inside you'll see `docs`, `tools`, `stickers`, `README.md` and so on.
3. On the new repository page, click the link **uploading an existing file**.
4. Select **everything inside** the `lamma-car` folder (not the folder itself) and drag it into the browser window. Wait until every file is listed.
   - Check the list shows paths such as `docs/index.html` and `tools/lamma.py`. If you see `lamma-car/docs/index.html`, you dragged the outer folder — cancel and drag its contents instead.
   - Hidden files (`.gitignore`, `docs/.nojekyll`) may not be uploaded by the browser. That's fine; the site works without them.
5. In **Commit changes**, keep "Commit directly to the `main` branch" and click **Commit changes**.

## Part 3 — Turn on GitHub Pages

1. In the repository, click **Settings** → **Pages** (left menu).
2. Under **Build and deployment** → **Source**, choose **Deploy from a branch**.
3. **Branch:** `main`, folder: **`/docs`**. Click **Save**.
4. Open the **Actions** tab. Wait for "pages build and deployment" to show a green tick (usually 1–3 minutes).
5. Back in **Settings → Pages**, the top shows *Your site is live at https://shamelbyvezeeta.github.io/lamma-car/*.

## Part 4 — Check the live site

| Open this | You should see |
|---|---|
| https://shamelbyvezeeta.github.io/lamma-car/ | Lamma Car card: "امسح الملصق للتواصل مع صاحب السيارة" |
| https://shamelbyvezeeta.github.io/lamma-car/?lang=en | The same in English, left-to-right |
| https://shamelbyvezeeta.github.io/lamma-car/q/zzzzzz/ | "هذا الرمز غير متاح حالياً" (unknown code) with the same styling |

If the third page has no styling, the repository name isn't exactly `lamma-car`.

The package contains **no codes and no contacts** yet, so there are no contact pages until you create your first batch (Part 5).

## Part 5 — First batch and first contact (on your computer)

You need Python 3.9 or newer (python.org). Open a terminal (Windows: Command Prompt) **inside the unzipped `lamma-car` folder** and run:

```bash
pip install -r tools/requirements.txt
python tools/lamma.py new-batch --count 40 --note "First print run"
```

(Windows: use `py` instead of `python` if needed.)

This creates the codes, their pages, the QR images and the sticker PDFs in `exports/LC-…/`. Then, for a customer who has received a sticker and agreed to be listed:

```bash
python tools/lamma.py assign <code> --name-ar "الاسم" --name-en "Name" --phone 01001234567 --consent --activate
python tools/lamma.py check
```

## Part 6 — Upload changes after using the tool

Every command changes files in `batches/`, `docs/` and, for new batches, `exports/`. To publish them:

1. In the repository, click **Add file → Upload files**.
2. Drag the folders **`batches`**, **`docs`** and (after a new batch) **`exports`** from your `lamma-car` folder into the browser. Files with the same names are replaced.
3. Click **Commit changes**. Wait for the green tick in **Actions**, then about 10 minutes for caching.
4. Scan the sticker or open its `q/<code>/` address to confirm.

If you later install git, `git add . && git commit -m "update" && git push` does the same in one step.

> Uploading through the website can add and replace files but cannot delete them. Nothing in normal operation needs deleting: deactivated codes keep their page, which shows "unavailable".

## Part 7 — Test before printing a batch

Before sending a batch to the printer:

1. Activate one code of the batch with your own name and number (your own consent).
2. Upload the changes (Part 6), scan the printed test sticker on a real rear windshield from outside, and check the call and WhatsApp buttons.
3. Then `python tools/lamma.py deactivate <code> --erase` and upload again (or hand that sticker to a real customer later — the code stays unique).

STICKER_PRINT_GUIDE.md explains the mirrored/normal choice and the glass test.

## How GitHub Pages details are handled

- Contact pages use relative paths (`../../assets/…`), so they work under `/lamma-car/`. Only `404.html` uses the full `/lamma-car/…` path, as GitHub requires.
- Every code is a real folder with an `index.html`, so direct links and refreshing never give a 404.
- QR codes include the trailing `/`, which avoids a redirect.

## Never change after printing

`shamelbyvezeeta`, `lamma-car` and `github.io` are inside every printed QR code. Renaming the organization or repository, making it private, or switching Pages off breaks every sticker already on a car.
