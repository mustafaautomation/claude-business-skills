"""Load skill scripts by path so the tests do not install a package."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins" / "business-skills" / "skills"
EXAMPLES = ROOT / "examples"


def load_script(skill: str, filename: str):
    path = SKILLS / skill / "scripts" / filename
    module_name = f"skill_{skill.replace('-', '_')}_{filename[:-3]}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
