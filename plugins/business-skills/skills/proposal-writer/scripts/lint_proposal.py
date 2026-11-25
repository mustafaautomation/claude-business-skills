#!/usr/bin/env python3
"""Check that a proposal draft follows the outline and only uses profile proof."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = ("Hook", "Understanding", "Approach", "Proof", "Timeline", "Questions")


def sections(markdown: str) -> dict[str, str]:
    parts = re.split(r"^##\s+", markdown, flags=re.M)
    found = {}
    for part in parts[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        found[title] = body
    return found


def proof_bullets(body: str) -> list[str]:
    bullets = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def questions(body: str) -> list[str]:
    return [line.strip()[2:].strip() for line in body.splitlines() if line.strip().startswith("- ") and line.strip().endswith("?")]


def lint_proposal(markdown: str, profile: dict) -> list[dict]:
    found = sections(markdown)
    problems = []
    for name in REQUIRED:
        if name not in found or not found[name].strip():
            problems.append({"path": name, "message": "section is missing or empty"})
    hook = found.get("Hook", "")
    hook_text = " ".join(hook.split())
    if hook and len(hook_text) > 400:
        problems.append({"path": "Hook", "message": f"is {len(hook_text)} characters; keep it under 400"})
    if hook and re.search(r"i hope this (email |message )?finds you well", hook, re.I):
        problems.append({"path": "Hook", "message": "drop the stock greeting"})
    allowed = [item.strip() for item in profile.get("proof") or []]
    used = proof_bullets(found.get("Proof", ""))
    if "Proof" in found and not used:
        problems.append({"path": "Proof", "message": "add at least one bullet copied from the profile"})
    for bullet in used:
        if bullet not in allowed:
            problems.append({"path": "Proof", "message": f"not in the profile proof list: {bullet}"})
    timeline = found.get("Timeline", "")
    if timeline and not re.search(r"\b(first|deliver|milestone)\b", timeline, re.I):
        problems.append({"path": "Timeline", "message": "name the first deliverable"})
    asked = questions(found.get("Questions", ""))
    if "Questions" in found and len(asked) < 2:
        problems.append({"path": "Questions", "message": "ask at least two questions that end with a question mark"})
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint a proposal against a profile.")
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        markdown = args.proposal.read_text(encoding="utf-8")
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        problems = lint_proposal(markdown, profile)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not problems:
        print("proposal ok")
        return 0
    for problem in problems:
        print(f"{problem['path']}: {problem['message']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
