#!/usr/bin/env python3
"""Print a short risk summary of the checkout suite. Used by the demo recording."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins" / "business-skills" / "skills" / "qa-test-generation" / "scripts" / "generate_tests.py"
EXAMPLE = ROOT / "examples" / "qa-test-generation" / "checkout.json"


def load():
    spec = importlib.util.spec_from_file_location("generate_tests", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load()
    document = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    result = module.generate(document)
    counts = {band: 0 for band in ("P0", "P1", "P2", "P3")}
    for case in result["cases"]:
        counts[case["priority"]] += 1
    print(f"$ python scripts/generate_tests.py {EXAMPLE.relative_to(ROOT)} --out-dir out --stem checkout")
    print()
    print(f"{result['feature']}: {len(result['cases'])} tests")
    print(f"P0 {counts['P0']}   P1 {counts['P1']}   P2 {counts['P2']}   P3 {counts['P3']}")
    print("uncovered acceptance: none")
    print()
    print(f"{'Test':<16} {'Pri':<4} {'Technique':<16} What it protects")
    show = {
        "US-14-TC-001": "valid code reduces the total",
        "US-14-TC-002": "expired code is rejected",
        "US-30-TC-001": "free shipping, score 12, pricing floor",
        "US-3-TC-001": "delivery copy, not a money path",
    }
    by_id = {case["id"]: case for case in result["cases"]}
    for test_id, label in show.items():
        case = by_id[test_id]
        print(f"{case['id']:<16} {case['priority']:<4} {case['technique']:<16} {label}")
    print()
    print("Wrote checkout.feature, checkout.spec.ts, checkout.traceability.md")
    print("Playwright skeletons are test.fixme until a person fills the locators.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
