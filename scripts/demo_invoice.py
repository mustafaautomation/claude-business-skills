#!/usr/bin/env python3
"""Print the invoice example and the broken-tax twin. Used by the demo recording."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "business-skills" / "skills" / "invoice-extraction" / "scripts" / "extract_invoice.py"
EXAMPLE = ROOT / "examples" / "invoice-extraction"


def load():
    spec = importlib.util.spec_from_file_location("extract_invoice", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def show(module, path: Path) -> None:
    print(f"$ python scripts/extract_invoice.py {path.relative_to(ROOT)}")
    print()
    sys.stdout.write(module.format_report(module.extract_path(path)))
    print()


def main() -> int:
    module = load()
    show(module, EXAMPLE / "northwind.txt")
    show(module, EXAMPLE / "northwind-bad-tax.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
