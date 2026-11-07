# Privacy guide

## The honest summary

GitHub Pages is **public static hosting**, and the repository is **public**. There is no private storage anywhere in this project.

- Every file in the repository can be read by anyone on github.com — including `batches/*.json`, which holds the names and numbers of **assigned, active and inactive** codes.
- Every page in `docs/` can be opened by anyone who has (or guesses) its URL.
- Git keeps history. Deleting or editing a record removes it from the current version, not from earlier commits.

So the rule is simple: **only enter a person's name and number once they've agreed to have them public.** Treat "saved in the repository" as "published".

## What the project does to limit exposure

- A scan opens one page with one person's name and mobile number only. No vehicle details, plate, address, photo or other records exist in the data at all.
- The website has no list, search, index or shared data file. Each page contains only its own record.
- Non-active codes (available, assigned, inactive) and unknown codes all show the same "unavailable" page, with no contact data in the HTML.
- Codes are random 6-character strings, not sequential numbers, so you can't reach other people's pages by counting.
- Pages carry `noindex, nofollow, noarchive` (asks search engines not to list them) and `no-referrer`.
- Activation requires a recorded consent date (`--consent`).
- `deactivate --erase` deletes the stored name and number.

These reduce casual exposure. They are **not** access control: someone browsing the repository on github.com can see every record and every code. Do not describe the service to customers as private.

## Consent

Before activating, tell the person plainly, and get their agreement (message or signed form, kept outside the repository):

> "Your name and mobile number will be shown on a public web page that opens when someone scans the sticker on your car. They will also be stored in a public GitHub repository. You can ask us to remove them at any time."

Record it with `--consent`. Keep the actual consent evidence off GitHub.

## Never put in the repository

Passwords, API keys, tokens, national ID numbers, licence plates, addresses, emails, car details, payment information, notes about customers, or consent forms.

## Removal requests

1. `python tools/lamma.py deactivate <code> --erase`, then upload the `batches` and `docs` folders (or commit and push). The page shows "unavailable" within minutes.
2. For full removal from history as well, rewrite the repository history (for example with `git filter-repo`) or, more simply, create a fresh repository from the current files with the same name. Contact GitHub Support to purge cached views if needed.

## Optional: keep management records off GitHub

If you'd rather not publish the batch files at all, add `batches/` (and `exports/`) to `.gitignore` and only publish `docs/`. Pages for active codes are still public, but assigned/inactive records and the full batch list are no longer on github.com. You then must back up `batches/` yourself — losing it means losing track of which code belongs to whom. Note that `docs/q/` still reveals which codes exist.

## Testing

Test with your own name and number (with your own consent), then `deactivate --erase`. Never use another real person's details for testing.
