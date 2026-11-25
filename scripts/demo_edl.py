#!/usr/bin/env python3
"""Print the short talking-head cut. Used by the demo recording."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins"
    / "business-skills"
    / "skills"
    / "talking-head-edit-plan"
    / "scripts"
    / "build_edl.py"
)
EXAMPLE = ROOT / "examples" / "talking-head-edit-plan" / "short.srt"


def load():
    spec = importlib.util.spec_from_file_location("build_edl", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load()
    cues, _fps = module.load_cues(EXAMPLE)
    plan = module.build_plan(cues)
    print(f"$ python scripts/build_edl.py {EXAMPLE.relative_to(ROOT)} --fps 30")
    print()
    print(f"source {plan['source_duration_ms']} ms  ->  program {plan['program_duration_ms']} ms")
    for item in plan["removed"]:
        label = item["text"] or f"{item['start_ms']}-{item['end_ms']} ms"
        print(f"removed  {item['reason']:<8} {label}")
    print()
    print(plan["edl"], end="" if plan["edl"].endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
