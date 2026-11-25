#!/usr/bin/env python3
"""Score a job post against a profile. The draft must not outrun this score."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KNOWN_TOOLS = (
    "python",
    "playwright",
    "selenium",
    "cypress",
    "pytest",
    "postman",
    "jira",
    "sql",
    "typescript",
    "appium",
    "k6",
    "premiere",
    "davinci",
    "ffmpeg",
)
RED_FLAGS = (
    ("unpaid-sample", re.compile(r"\b(unpaid|free)\s+(sample|test|trial|edit)\b", re.I), 20),
    ("equity-only", re.compile(r"\bequity[-\s]?only\b", re.I), 25),
    ("hype-language", re.compile(r"\b(rockstar|ninja|guru)\b", re.I), 5),
    ("urgent", re.compile(r"\b(urgent|asap|yesterday)\b", re.I), 10),
)
HOURLY_RE = re.compile(r"\$(\d+)\s*-\s*\$?(\d+)\s*/\s*hr", re.I)
HOURLY_SINGLE_RE = re.compile(r"\$(\d+)\s*/\s*hr", re.I)
FIXED_RE = re.compile(r"\$(\d{1,3}(?:,\d{3})*|\d+)\s+fixed", re.I)


class FitError(Exception):
    """The job post or the profile could not be scored."""


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9+#.]+", text.lower()))


def matched_skills(job: str, skills: list[str]) -> list[str]:
    haystack = job.lower()
    words = _words(job)
    found = []
    for skill in skills:
        token = skill.strip()
        if not token:
            continue
        lowered = token.lower()
        if len(lowered) <= 3:
            hit = lowered in words
        else:
            hit = lowered in haystack
        if hit:
            found.append(lowered)
    return sorted(set(found))


def must_have_sentences(job: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", job)
    return [sentence for sentence in sentences if re.search(r"\bmust have\b|\bmust be\b", sentence, re.I)]


def missing_tools(job: str, skills: list[str]) -> list[str]:
    owned = {skill.lower() for skill in skills}
    missing = []
    for sentence in must_have_sentences(job):
        lowered = sentence.lower()
        for tool in KNOWN_TOOLS:
            if re.search(rf"\b{re.escape(tool)}\b", lowered) and tool not in owned and not any(tool in skill for skill in owned):
                missing.append(tool)
    return sorted(set(missing))


def parse_budget(job: str) -> dict | None:
    hourly = HOURLY_RE.search(job)
    if hourly:
        return {
            "kind": "hourly",
            "low": int(hourly.group(1)),
            "high": int(hourly.group(2)),
            "currency": "USD",
        }
    single = HOURLY_SINGLE_RE.search(job)
    if single:
        amount = int(single.group(1))
        return {"kind": "hourly", "low": amount, "high": amount, "currency": "USD"}
    fixed = FIXED_RE.search(job)
    if fixed:
        return {
            "kind": "fixed",
            "amount": int(fixed.group(1).replace(",", "")),
            "currency": "USD",
        }
    return None


def band_for(score: int) -> str:
    if score >= 75:
        return "recommend"
    if score >= 55:
        return "conditional"
    return "decline"


def recommended_move(flags: list[str], band: str) -> str:
    if "unpaid-sample" in flags:
        return "Ask for a paid pilot. Do not start with an unpaid sample."
    if "equity-only" in flags:
        return "Decline equity-only work unless cash is part of the offer."
    if band == "recommend":
        return "Bid. Lead with the closest proof point and a scoped first step."
    if band == "conditional":
        return "Bid only if the first milestone is small enough to price from the post."
    return "Skip, or answer with a narrower paid slice instead of a full yes."


def score_fit(job: str, profile: dict) -> dict:
    if not job.strip():
        raise FitError("The job post is empty.")
    if not isinstance(profile, dict):
        raise FitError("The profile must be a JSON object.")
    skills = [str(item) for item in profile.get("skills") or []]
    proof = [str(item) for item in profile.get("proof") or []]
    matched = matched_skills(job, skills)
    missing = missing_tools(job, skills)
    flags = []
    penalty = 0
    for name, pattern, weight in RED_FLAGS:
        if pattern.search(job):
            flags.append(name)
            penalty += weight
    score = 40 + min(40, 10 * len(matched)) - 15 * len(missing) - penalty
    score = max(0, min(100, score))
    return {
        "fit_score": score,
        "band": band_for(score),
        "matched_skills": matched,
        "missing_must_haves": missing,
        "red_flags": flags,
        "budget": parse_budget(job),
        "recommended_move": recommended_move(flags, band_for(score)),
        "proof_points_allowed": proof,
        "profile_name": str(profile.get("name", "")).strip(),
    }


def format_report(result: dict) -> str:
    budget = result["budget"]
    if not budget:
        budget_line = "budget not stated"
    elif budget["kind"] == "hourly":
        budget_line = f"${budget['low']}-{budget['high']}/hr"
    else:
        budget_line = f"${budget['amount']} fixed"
    lines = [
        f"Fit {result['fit_score']}  {result['band']}  {budget_line}",
        f"Matched: {', '.join(result['matched_skills']) or 'none'}",
        f"Missing must-haves: {', '.join(result['missing_must_haves']) or 'none'}",
        f"Flags: {', '.join(result['red_flags']) or 'none'}",
        result["recommended_move"],
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score a job post against a profile.")
    parser.add_argument("--job", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--json", dest="json_out", type=Path)
    args = parser.parse_args(argv)
    try:
        job = args.job.read_text(encoding="utf-8")
        profile = json.loads(args.profile.read_text(encoding="utf-8"))
        result = score_fit(job, profile)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (FitError, json.JSONDecodeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(format_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
