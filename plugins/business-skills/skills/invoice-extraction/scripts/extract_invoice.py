#!/usr/bin/env python3
"""Extract a labeled invoice into validated JSON and CSV.

Text and JSON use the standard library. PDF text uses pypdf when it is
installed, and uncompressed PDF text operators otherwise. Photos are not
OCR'd here: transcribe them into the labeled format, then validate.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

MONEY = Decimal("0.01")
TOLERANCE = Decimal("0.01")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff", ".bmp"}
CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "CAD",
    "AUD",
    "NZD",
    "CHF",
    "JPY",
    "SEK",
    "NOK",
    "DKK",
    "INR",
    "SGD",
    "AED",
    "SAR",
}

HEADER_RE = {
    "invoice_number": re.compile(r"^invoice number:\s*(.+)$", re.I),
    "invoice_date": re.compile(r"^invoice date:\s*(.+)$", re.I),
    "due_date": re.compile(r"^due date:\s*(.+)$", re.I),
    "currency": re.compile(r"^currency:\s*(.+)$", re.I),
    "payment_terms": re.compile(r"^payment terms:\s*(.+)$", re.I),
}
SUBTOTAL_RE = re.compile(r"^subtotal:\s*([0-9,]+\.[0-9]{2})$", re.I)
TOTAL_RE = re.compile(r"^total:\s*([0-9,]+\.[0-9]{2})$", re.I)
TAX_RE = re.compile(
    r"^tax(?:\s*\(([0-9]+(?:\.[0-9]+)?)%\))?\s*:\s*([0-9,]+\.[0-9]{2})$",
    re.I,
)
TAX_ID_RE = re.compile(r"^tax id:\s*(.+)$", re.I)
ISO_DATE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
US_DATE = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
CSV_COLUMNS = [
    "invoice_number",
    "invoice_date",
    "due_date",
    "currency",
    "seller_name",
    "buyer_name",
    "sku",
    "description",
    "quantity",
    "unit_price",
    "amount",
    "subtotal",
    "tax",
    "total",
]


class InvoiceError(Exception):
    """The file is not an invoice this script can read."""


def quantize(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


def money_str(value: Decimal) -> str:
    return f"{quantize(value):.2f}"


def parse_money(raw: str) -> Decimal:
    return quantize(Decimal(raw.replace(",", "")))


def parse_date(raw: str) -> str | None:
    text = raw.strip()
    iso = ISO_DATE.match(text)
    if iso:
        year, month, day = (int(part) for part in iso.groups())
        return _iso(year, month, day)
    us = US_DATE.match(text)
    if us:
        month, day, year = (int(part) for part in us.groups())
        return _iso(year, month, day)
    return None


def _iso(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def render_text_pdf(text: str) -> bytes:
    """Build a one-page uncompressed PDF whose text operators carry `text`."""
    commands = ["BT", "/F1 11 Tf", "54 760 Td", "14 TL"]
    for line in text.splitlines() or [""]:
        safe = line.encode("latin-1", "replace").decode("latin-1")
        safe = safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"({safe}) Tj")
        commands.append("T*")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode("ascii")
        out += body
        out += b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    out += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        out += f"{offset:010d} 00000 n \n".encode("ascii")
    out += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode("ascii")
    return bytes(out)


def _pdf_text_fallback(data: bytes) -> str:
    raw = data.decode("latin-1", "replace")
    if "stream" in raw and "/FlateDecode" in raw:
        raise InvoiceError(
            "This PDF is compressed and pypdf is not installed. "
            "Transcribe the invoice into the labeled text format and run the script on the .txt file."
        )
    lines: list[str] = []
    for match in re.finditer(r"\((?:\\.|[^\\)])*\)\s*Tj", raw):
        token = match.group(0)
        inner = token[: token.rfind(")")].split("(", 1)[1]
        inner = inner.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
        lines.append(inner)
    if not lines:
        raise InvoiceError("No text operators found in this PDF.")
    return "\n".join(lines)


def read_pdf_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        from pypdf import PdfReader
    except ImportError:
        return _pdf_text_fallback(data)
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages).strip()
    if not text:
        return _pdf_text_fallback(data)
    return text


def load_source(path: Path) -> dict | str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        raise InvoiceError(
            "This script does not OCR photos. Read the image, transcribe it into "
            "the labeled text format (see references/field-rules.md), and run the script on that text."
        )
    if suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if suffix == ".pdf":
        return read_pdf_text(path)
    if suffix in {".txt", ".md", ""}:
        return path.read_text(encoding="utf-8")
    raise InvoiceError(f"Unsupported invoice file type: {suffix or 'none'}")


def _party(lines: list[str]) -> dict:
    name = ""
    tax_id = ""
    address: list[str] = []
    for line in lines:
        tax = TAX_ID_RE.match(line)
        if tax:
            tax_id = tax.group(1).strip()
            continue
        if not name:
            name = line.strip()
            continue
        address.append(line.strip())
    party = {"name": name, "address": ", ".join(address)}
    if tax_id:
        party["tax_id"] = tax_id
    return party


def parse_labeled_text(text: str) -> dict:
    lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n")]
    header: dict[str, str] = {}
    from_lines: list[str] = []
    bill_lines: list[str] = []
    item_lines: list[str] = []
    mode = "header"
    totals: dict[str, str] = {}
    tax_rate: str | None = None
    for line in lines:
        if not line:
            continue
        lowered = line.lower()
        if lowered == "from:":
            mode = "from"
            continue
        if lowered == "bill to:":
            mode = "bill"
            continue
        if lowered == "line items:":
            mode = "items"
            continue
        if mode == "header":
            matched = False
            for key, pattern in HEADER_RE.items():
                found = pattern.match(line)
                if found:
                    header[key] = found.group(1).strip()
                    matched = True
                    break
            if matched:
                continue
        if mode == "from":
            from_lines.append(line)
            continue
        if mode == "bill":
            bill_lines.append(line)
            continue
        if mode == "items":
            subtotal = SUBTOTAL_RE.match(line)
            tax = TAX_RE.match(line)
            total = TOTAL_RE.match(line)
            terms = HEADER_RE["payment_terms"].match(line)
            if subtotal:
                totals["subtotal"] = subtotal.group(1)
                mode = "totals"
                continue
            if "|" in line:
                item_lines.append(line)
                continue
        if mode in {"items", "totals"}:
            subtotal = SUBTOTAL_RE.match(line)
            tax = TAX_RE.match(line)
            total = TOTAL_RE.match(line)
            terms = HEADER_RE["payment_terms"].match(line)
            if subtotal:
                totals["subtotal"] = subtotal.group(1)
            elif tax:
                tax_rate = tax.group(1)
                totals["tax"] = tax.group(2)
            elif total:
                totals["total"] = total.group(1)
            elif terms:
                header["payment_terms"] = terms.group(1).strip()
    if "invoice_number" not in header and not item_lines:
        raise InvoiceError("No invoice number or line items found. Use the labeled text format.")
    items = []
    for raw in item_lines:
        parts = [part.strip() for part in raw.split("|")]
        if len(parts) != 5:
            items.append({"_raw": raw})
            continue
        sku, description, quantity, unit_price, amount = parts
        items.append(
            {
                "sku": sku,
                "description": description,
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": amount,
            }
        )
    seller = _party(from_lines)
    buyer = _party(bill_lines)
    return {
        "invoice_number": header.get("invoice_number", ""),
        "invoice_date": header.get("invoice_date", ""),
        "due_date": header.get("due_date", ""),
        "currency": header.get("currency", ""),
        "seller": seller,
        "buyer": {"name": buyer.get("name", ""), "address": buyer.get("address", "")},
        "line_items": items,
        "subtotal": totals.get("subtotal", ""),
        "tax_rate_percent": tax_rate,
        "tax": totals.get("tax", ""),
        "total": totals.get("total", ""),
        "payment_terms": header.get("payment_terms", ""),
    }


def _err(errors: list[dict], path: str, message: str) -> None:
    errors.append({"path": path, "message": message})


def _as_money(errors: list[dict], path: str, raw: object) -> Decimal | None:
    if not isinstance(raw, str) or not re.fullmatch(r"-?[0-9,]+\.[0-9]{2}", raw):
        _err(errors, path, "must be a decimal string with two places, such as 12.00")
        return None
    return parse_money(raw)


def validate_invoice(doc: dict) -> dict:
    """Return a normalized invoice with `valid` and `errors` recomputed."""
    errors: list[dict] = []
    number = doc.get("invoice_number")
    if not isinstance(number, str) or not number.strip():
        _err(errors, "invoice_number", "is required")
        number = ""
    dates = {}
    for field in ("invoice_date", "due_date"):
        raw = doc.get(field, "")
        if not isinstance(raw, str):
            _err(errors, field, "is required")
            dates[field] = ""
            continue
        parsed = parse_date(raw)
        if parsed is None:
            _err(errors, field, f"could not parse {raw!r} as a date")
            dates[field] = raw
        else:
            dates[field] = parsed
    if dates.get("invoice_date") and dates.get("due_date"):
        if dates["due_date"] < dates["invoice_date"]:
            _err(errors, "due_date", "is earlier than invoice_date")
    currency = str(doc.get("currency", "")).strip().upper()
    if currency not in CURRENCIES:
        _err(errors, "currency", f"{currency or 'blank'} is not a supported ISO currency")
    seller = doc.get("seller") if isinstance(doc.get("seller"), dict) else {}
    buyer = doc.get("buyer") if isinstance(doc.get("buyer"), dict) else {}
    if not str(seller.get("name", "")).strip():
        _err(errors, "seller.name", "is required")
    if not str(buyer.get("name", "")).strip():
        _err(errors, "buyer.name", "is required")
    items_in = doc.get("line_items")
    items_out = []
    running = Decimal("0.00")
    if not isinstance(items_in, list) or not items_in:
        _err(errors, "line_items", "must contain at least one item")
    else:
        for index, item in enumerate(items_in):
            path = f"line_items[{index}]"
            if not isinstance(item, dict) or "_raw" in item:
                _err(errors, path, "must have sku, description, quantity, unit price, and amount separated by |")
                continue
            sku = str(item.get("sku", "")).strip()
            description = str(item.get("description", "")).strip()
            if not sku:
                _err(errors, f"{path}.sku", "is required")
            if not description:
                _err(errors, f"{path}.description", "is required")
            qty_raw = str(item.get("quantity", "")).strip()
            if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", qty_raw):
                _err(errors, f"{path}.quantity", "must be a positive number")
                quantity = None
            else:
                quantity = Decimal(qty_raw)
                if quantity <= 0:
                    _err(errors, f"{path}.quantity", "must be greater than zero")
            unit = _as_money(errors, f"{path}.unit_price", str(item.get("unit_price", "")))
            amount = _as_money(errors, f"{path}.amount", str(item.get("amount", "")))
            if quantity is not None and unit is not None and amount is not None:
                expected = quantize(quantity * unit)
                if abs(expected - amount) > TOLERANCE:
                    _err(
                        errors,
                        f"{path}.amount",
                        f"{money_str(amount)} does not match quantity {qty_raw} times unit price {money_str(unit)} (expected {money_str(expected)})",
                    )
                running += amount
            if quantity is None or unit is None or amount is None:
                continue
            items_out.append(
                {
                    "sku": sku,
                    "description": description,
                    "quantity": qty_raw,
                    "unit_price": money_str(unit),
                    "amount": money_str(amount),
                }
            )
    subtotal = _as_money(errors, "subtotal", str(doc.get("subtotal", "")))
    tax = _as_money(errors, "tax", str(doc.get("tax", "")))
    total = _as_money(errors, "total", str(doc.get("total", "")))
    rate_raw = doc.get("tax_rate_percent")
    rate: Decimal | None
    if rate_raw in (None, ""):
        rate = None
    else:
        try:
            rate = Decimal(str(rate_raw))
        except Exception:
            _err(errors, "tax_rate_percent", "must be a number such as 8.5")
            rate = None
    if subtotal is not None and items_out and abs(running - subtotal) > TOLERANCE:
        _err(
            errors,
            "subtotal",
            f"{money_str(subtotal)} does not match the sum of line amounts {money_str(running)}",
        )
    if subtotal is not None and tax is not None and rate is not None:
        expected_tax = quantize(subtotal * rate / Decimal("100"))
        if abs(expected_tax - tax) > TOLERANCE:
            _err(
                errors,
                "tax",
                f"{money_str(tax)} does not match {rate}% of subtotal {money_str(subtotal)} (expected {money_str(expected_tax)})",
            )
    if subtotal is not None and tax is not None and total is not None:
        expected_total = quantize(subtotal + tax)
        if abs(expected_total - total) > TOLERANCE:
            _err(
                errors,
                "total",
                f"{money_str(total)} does not match subtotal plus tax {money_str(expected_total)}",
            )
    terms = doc.get("payment_terms", "")
    if not isinstance(terms, str) or not terms.strip():
        _err(errors, "payment_terms", "is required")
        terms = ""
    seller_out = {
        "name": str(seller.get("name", "")).strip(),
        "address": str(seller.get("address", "")).strip(),
    }
    if str(seller.get("tax_id", "")).strip():
        seller_out["tax_id"] = str(seller.get("tax_id")).strip()
    normalized = {
        "invoice_number": number.strip() if isinstance(number, str) else "",
        "invoice_date": dates.get("invoice_date", ""),
        "due_date": dates.get("due_date", ""),
        "currency": currency,
        "seller": seller_out,
        "buyer": {
            "name": str(buyer.get("name", "")).strip(),
            "address": str(buyer.get("address", "")).strip(),
        },
        "line_items": items_out,
        "subtotal": money_str(subtotal) if subtotal is not None else "",
        "tax_rate_percent": None if rate is None else format(rate.normalize(), "f"),
        "tax": money_str(tax) if tax is not None else "",
        "total": money_str(total) if total is not None else "",
        "payment_terms": terms.strip(),
        "valid": not errors,
        "errors": errors,
    }
    if normalized["tax_rate_percent"] is not None:
        normalized["tax_rate_percent"] = _trim_rate(rate)
    return normalized


def _trim_rate(rate: Decimal | None) -> str | None:
    if rate is None:
        return None
    text = format(rate, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def invoice_from_source(source: dict | str) -> dict:
    if isinstance(source, str):
        parsed = parse_labeled_text(source)
    elif isinstance(source, dict):
        parsed = source
    else:
        raise InvoiceError("Invoice JSON must be an object.")
    return validate_invoice(parsed)


def to_csv(doc: dict) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    items = doc.get("line_items") or []
    if not items:
        items = [
            {
                "sku": "",
                "description": "",
                "quantity": "",
                "unit_price": "",
                "amount": "",
            }
        ]
    for item in items:
        writer.writerow(
            {
                "invoice_number": doc.get("invoice_number", ""),
                "invoice_date": doc.get("invoice_date", ""),
                "due_date": doc.get("due_date", ""),
                "currency": doc.get("currency", ""),
                "seller_name": (doc.get("seller") or {}).get("name", ""),
                "buyer_name": (doc.get("buyer") or {}).get("name", ""),
                "sku": item.get("sku", ""),
                "description": item.get("description", ""),
                "quantity": item.get("quantity", ""),
                "unit_price": item.get("unit_price", ""),
                "amount": item.get("amount", ""),
                "subtotal": doc.get("subtotal", ""),
                "tax": doc.get("tax", ""),
                "total": doc.get("total", ""),
            }
        )
    return buffer.getvalue()


def format_report(doc: dict) -> str:
    seller = (doc.get("seller") or {}).get("name") or "—"
    buyer = (doc.get("buyer") or {}).get("name") or "—"
    status = "VALID" if doc.get("valid") else "INVALID"
    lines = [
        f"{doc.get('invoice_number') or 'Invoice'}  {status}",
        f"{seller}  ->  {buyer}",
        f"{doc.get('invoice_date') or '—'}  due {doc.get('due_date') or '—'}  {doc.get('currency') or ''}",
        "",
    ]
    for item in doc.get("line_items") or []:
        lines.append(
            f"  {item['sku']:<10} {item['quantity']:>6} x {item['unit_price']:>10} = {item['amount']:>10}  {item['description']}"
        )
    lines.append("")
    rate = doc.get("tax_rate_percent")
    tax_label = f"tax ({rate}%)" if rate else "tax"
    lines.append(f"  {'subtotal':<12} {doc.get('subtotal') or '—':>10}")
    lines.append(f"  {tax_label:<12} {doc.get('tax') or '—':>10}")
    lines.append(f"  {'total':<12} {doc.get('total') or '—':>10}")
    if doc.get("errors"):
        lines.append("")
        lines.append("Errors")
        for problem in doc["errors"]:
            lines.append(f"  {problem['path']}: {problem['message']}")
    return "\n".join(lines) + "\n"


def extract_path(path: Path) -> dict:
    return invoice_from_source(load_source(path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract and validate an invoice.")
    parser.add_argument("input", type=Path, help="Labeled .txt, .pdf, or invoice .json")
    parser.add_argument("--json", dest="json_out", type=Path, help="Write the invoice JSON here")
    parser.add_argument("--csv", dest="csv_out", type=Path, help="Write one CSV row per line item")
    parser.add_argument("--quiet", action="store_true", help="Print only the status word")
    args = parser.parse_args(argv)
    try:
        document = extract_path(args.input)
    except FileNotFoundError:
        print(f"File not found: {args.input}", file=sys.stderr)
        return 2
    except (InvoiceError, json.JSONDecodeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    payload = json.dumps(document, indent=2) + "\n"
    csv_text = to_csv(document)
    if args.json_out:
        args.json_out.write_text(payload, encoding="utf-8")
    if args.csv_out:
        args.csv_out.write_text(csv_text, encoding="utf-8")
    if args.quiet:
        print("VALID" if document["valid"] else "INVALID")
    else:
        sys.stdout.write(format_report(document))
    return 0 if document["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
