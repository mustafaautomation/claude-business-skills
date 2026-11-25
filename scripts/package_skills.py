#!/usr/bin/env python3
"""Write one upload zip per skill. Timestamps are fixed so the zip is reproducible."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins" / "business-skills" / "skills"
SKIP_PARTS = {"__pycache__", ".pytest_cache"}


def iter_files(skill_dir: Path) -> list[Path]:
    files = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix == ".pyc":
            continue
        files.append(path)
    return sorted(files)


def package_skill(skill_dir: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w") as archive:
        for path in iter_files(skill_dir):
            relative = path.relative_to(skill_dir).as_posix()
            info = zipfile.ZipInfo(f"{skill_dir.name}/{relative}", date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o644 & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    return dest


def package_all(dist: Path | None = None) -> list[Path]:
    dist = dist or (ROOT / "dist")
    written = []
    for skill in sorted(path for path in SKILLS.iterdir() if (path / "SKILL.md").is_file()):
        written.append(package_skill(skill, dist / f"{skill.name}.zip"))
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Zip each skill for upload.")
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    for path in package_all(args.dist):
        print(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
