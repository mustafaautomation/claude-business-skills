---
name: invoice-extraction
description: Extracts supplier, customer, dates, currency, line items, tax, and totals from invoice text or PDFs into validated JSON and CSV, and checks that line math and totals agree. Use when the user uploads an invoice, receipt, or bill and wants structured data, a spreadsheet, or a check that the numbers add up. For a photo, transcribe it first, then validate.
license: MIT
compatibility: Requires Python 3.11 or newer. No network calls. PDF text uses pypdf when that package is already installed.
metadata:
  author: Mustafa
  version: "1.0.0"
---

# Invoice extraction

Turn an invoice into JSON and CSV only after the money checks pass. Arithmetic is the job. Tax law, payment, and bookkeeping are not.

## Inputs

Accept labeled text, a PDF, or JSON that already uses the invoice shape. Reject a photo path: read the image yourself, write the labeled text from [field rules](references/field-rules.md), then run the script. If a digit is unclear, leave the field blank. Do not invent a total that makes the invoice balance.

## Steps

1. Identify the file type.
2. For text or PDF, run the script below. For a photo, transcribe first, save a `.txt` file, then run the same command.
3. Read `valid` and `errors`. Quote the path and message when you tell the user what failed.
4. Hand over the JSON and CSV only when exit code is 0. On exit code 1, show the report and do not silently "fix" the vendor's numbers. Ask which source value is wrong.
5. On exit code 2, say what the script could not read and which format it needs.

Run from this skill directory:

```bash
python scripts/extract_invoice.py invoice.txt --json invoice.json --csv invoice.csv
```

A worked invoice, a PDF of the same text, a broken-tax twin, and the expected JSON and CSV live in the project `examples/invoice-extraction/` directory.

## Rules the script enforces

- Quantity times unit price matches the line amount within one cent.
- Line amounts sum to the subtotal within one cent.
- A stated tax rate has to produce the stated tax within one cent.
- Subtotal plus tax matches the total within one cent.
- The due date is not earlier than the invoice date.
- Money is half-up to two decimal places. JSON stores money as strings so a cent is not lost to binary floats.

The schema is `assets/invoice.schema.json`. If the user already has JSON, still run the script on that file so the checks run again.

## What to say when it fails

Name the field path. `tax: 100.00 does not match 8.5% of subtotal 1660.00 (expected 141.10)` is the whole finding. Do not add a paragraph about what the vendor might have meant.

## Out of scope

Do not pay the invoice, email the vendor, or decide whether the rate is the right rate for a jurisdiction. Say that the check is arithmetic when the user asks "is this tax correct?"
