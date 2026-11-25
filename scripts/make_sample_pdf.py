#!/usr/bin/env python3
"""Build examples/invoice-extraction/northwind.pdf from northwind.txt.

The PDF is a fixture for the invoice-extraction skill: a fictional
Northwind invoice, rendered with the skill's own `render_text_pdf` (one
uncompressed page, Helvetica, one text operator per line). The output is
byte-for-byte deterministic, so re-running this script never changes the file.

    python3 scripts/make_sample_pdf.py          # write the PDF
    python3 scripts/make_sample_pdf.py --check  # exit 1 if the PDF is stale
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "business-skills" / "skills" / "invoice-extraction" / "scripts" / "extract_invoice.py"
EXAMPLE = ROOT / "examples" / "invoice-extraction"
SOURCE = EXAMPLE / "northwind.txt"
TARGET = EXAMPLE / "northwind.pdf"


def load():
    spec = importlib.util.spec_from_file_location("extract_invoice", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def build() -> bytes:
    return load().render_text_pdf(SOURCE.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    data = build()
    if "--check" in argv:
        if not TARGET.is_file() or TARGET.read_bytes() != data:
            print(f"{TARGET.relative_to(ROOT)} is stale; run python3 scripts/make_sample_pdf.py", file=sys.stderr)
            return 1
        print(f"{TARGET.relative_to(ROOT)} is up to date")
        return 0
    TARGET.write_bytes(data)
    print(f"wrote {TARGET.relative_to(ROOT)} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
