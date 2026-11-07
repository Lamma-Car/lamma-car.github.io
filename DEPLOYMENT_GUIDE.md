# Upload and deployment guide

**Live site address (after deployment):** https://shamelbyvezeeta.github.io/Lamma_Car/
**QR code addresses:** `https://shamelbyvezeeta.github.io/Lamma_Car/q/<code>/`

Everything in this package is already set to this address. You don't need to create or edit any file.

---

## Part 1 — Create the repository

1. Sign in to github.com with an account that can create repositories in **shamelbyvezeeta**.
2. Click **+** (top right) → **New repository**.
3. **Owner:** `shamelbyvezeeta` · **Repository name:** `Lamma_Car` (exactly: capital L and C, underscore).
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
5. Back in **Settings → Pages**, the top shows *Your site is live at https://shamelbyvezeeta.github.io/Lamma_Car/*.

## Part 4 — Check the live site

| Open this | You should see |
|---|---|
| https://shamelbyvezeeta.github.io/Lamma_Car/ | Lamma Car card: "امسح الملصق للتواصل مع صاحب السيارة" |
| https://shamelbyvezeeta.github.io/Lamma_Car/?lang=en | The same in English, left-to-right |
| https://shamelbyvezeeta.github.io/Lamma_Car/q/zzzzzz/ | "هذا الرمز غير متاح حالياً" (unknown code) with the same styling |

If the third page has no styling, the repository name isn't exactly `Lamma_Car`.

The package contains **no codes and no contacts** yet, so there are no contact pages until you create your first batch (Part 5).

## Part 5 — First batch and first customer (admin page)

1. On your computer, open the unzipped `lamma-car` folder → `tools` → double-click **`admin.html`**.
2. Create a GitHub token and connect (the page shows the steps; details in BATCH_MANAGEMENT_GUIDE.md).
3. **+ دفعة أكواد جديدة** → e.g. 40 → **إنشاء** → **نشر على الموقع**.
4. On the batch card, download **ملصقات للطباعة** for the print shop (read STICKER_PRINT_GUIDE.md first).
5. When a customer gets a sticker: find its code → **إضافة عميل** → name, mobile, consent → **حفظ** → **نشر على الموقع**.

No uploading by hand: the admin page saves directly to the repository, and GitHub Pages updates the site in 1–10 minutes.

## Part 6 — If you use the command-line tool instead

`python tools/lamma.py …` changes files on your computer only. Upload the changed `batches`, `docs` and `exports` folders with **Add file → Upload files** (files with the same names are replaced), or `git push`. If you switch between the admin page and the command line, first download the latest repository (**Code → Download ZIP**) so you start from what's on GitHub.

> Uploading through the website can add and replace files but cannot delete them. Nothing in normal operation needs deleting: deactivated codes keep their page, which shows "unavailable".

## Part 7 — Test before printing a batch

Before sending a batch to the printer:

1. In the admin page, add your own name and number to one code of the batch (your own consent) and publish.
2. Print that sticker (A4 تجربة), fix it inside a real rear windshield, scan it from outside, and check the Call and WhatsApp buttons.
3. Then **مسح البيانات** on that code and publish. Don't give that sticker to a customer afterwards: an erased code stays "unavailable".

STICKER_PRINT_GUIDE.md explains the mirrored/normal choice and the glass test.

## How GitHub Pages details are handled

- Contact pages use relative paths (`../../assets/…`), so they work under `/Lamma_Car/`. Only `404.html` uses the full `/Lamma_Car/…` path, as GitHub requires.
- Every code is a real folder with an `index.html`, so direct links and refreshing never give a 404.
- QR codes include the trailing `/`, which avoids a redirect.

## Never change after printing

`shamelbyvezeeta`, `Lamma_Car` and `github.io` are inside every printed QR code. Renaming the organization or repository, making it private, or switching Pages off breaks every sticker already on a car.
