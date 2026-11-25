# Invoice field rules

The script checks arithmetic. It does not decide whether a tax rate is legally correct, and it does not book the invoice into an accounting system.

## Labeled text

Use this shape. Descriptions must not contain `|`.

```
Invoice Number: INV-1042
Invoice Date: 2026-03-02
Due Date: 2026-03-16
Currency: USD

From:
Northwind QA Studio
12 Harbor Lane
Austin, TX 78701
Tax ID: 74-2938104

Bill To:
Quvantic Labs
88 Market Street
San Francisco, CA 94105

Line Items:
QA-AUTO | Playwright regression suite | 12 | 85.00 | 1020.00

Subtotal: 1660.00
Tax (8.5%): 141.10
Total: 1801.10
Payment Terms: Net 14
```

Dates may also be `MM/DD/YYYY`. Money always has two decimal places. `Tax:` without a parenthetical rate is allowed; the rate check is then skipped and the total check remains.

## What is validated

- Invoice number, both party names, payment terms, and at least one line item are present.
- Currency is one of USD, EUR, GBP, CAD, AUD, NZD, CHF, JPY, SEK, NOK, DKK, INR, SGD, AED, SAR.
- Due date is on or after the invoice date.
- Each line amount matches quantity times unit price within 0.01.
- Subtotal matches the sum of line amounts within 0.01.
- When a rate is present, tax matches that percent of the subtotal within 0.01.
- Total matches subtotal plus tax within 0.01.

Money uses half-up rounding to the cent.

## Photos

Do not pass a PNG or JPEG to the script. Read the image, transcribe it into the labeled format above, then run the script on the text file. If a field is unreadable, leave it blank and let the validator report the path. Do not guess a total.

## PDF

`pypdf` is used when it is installed. An uncompressed PDF still parses without it. A compressed PDF without `pypdf` stops with an error: transcribe the text and rerun.

## Output

JSON keys match `assets/invoice.schema.json`. CSV has one row per line item and repeats the invoice header on each row. Exit 0 when `valid` is true, 1 when the file parsed but the checks failed, 2 when the file could not be read.
