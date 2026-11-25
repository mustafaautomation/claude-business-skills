#!/usr/bin/env python3
"""Check a repurposed content pack against channel length and structure rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HASHTAG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{1,30}$")
CTA_CUES = ("follow", "reply", "newsletter", "link", "read", "watch")


def _check(checks: list[dict], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": ok, "detail": detail})


def spoken_words(pack: dict) -> int:
    beats = (pack.get("short_video") or {}).get("beats") or []
    return sum(len(str(beat.get("spoken", "")).split()) for beat in beats if isinstance(beat, dict))


def check_pack(pack: dict) -> dict:
    checks: list[dict] = []
    if not isinstance(pack, dict):
        return {"ok": False, "checks": [{"name": "pack", "ok": False, "detail": "pack must be a JSON object"}]}
    title = pack.get("source_title")
    _check(checks, "source_title", isinstance(title, str) and bool(title.strip()), "source title is required")

    linkedin = pack.get("linkedin") if isinstance(pack.get("linkedin"), dict) else {}
    hook = str(linkedin.get("hook", ""))
    body = str(linkedin.get("body", ""))
    _check(checks, "linkedin.hook", 40 <= len(hook) <= 150, f"hook is {len(hook)} characters; need 40-150")
    _check(checks, "linkedin.body", 500 <= len(body) <= 1800, f"body is {len(body)} characters; need 500-1800")
    tags = linkedin.get("hashtags")
    tags_ok = (
        isinstance(tags, list)
        and 3 <= len(tags) <= 5
        and all(isinstance(tag, str) and HASHTAG_RE.fullmatch(tag) for tag in tags)
    )
    _check(checks, "linkedin.hashtags", tags_ok, "use 3 to 5 hashtags, letters and digits only, no # sign")

    thread = pack.get("x_thread")
    thread_ok = isinstance(thread, list) and 5 <= len(thread) <= 9
    _check(checks, "x_thread.count", thread_ok, f"thread has {len(thread) if isinstance(thread, list) else 0} posts; need 5-9")
    if isinstance(thread, list):
        for index, post in enumerate(thread, start=1):
            text = str(post.get("text", "")) if isinstance(post, dict) else ""
            _check(
                checks,
                f"x_thread.{index}.length",
                1 <= len(text) <= 280,
                f"post {index} is {len(text)} characters; need 1-280",
            )
        if thread:
            first = str(thread[0].get("text", "")) if isinstance(thread[0], dict) else ""
            last = str(thread[-1].get("text", "")) if isinstance(thread[-1], dict) else ""
            _check(checks, "x_thread.hook", not first[:1].isdigit(), "the first post should not start with a number")
            _check(
                checks,
                "x_thread.cta",
                any(cue in last.lower() for cue in CTA_CUES),
                "the last post needs a cue such as follow, reply, read, watch, link, or newsletter",
            )

    news = pack.get("newsletter") if isinstance(pack.get("newsletter"), dict) else {}
    subjects = news.get("subject_options")
    subjects_ok = (
        isinstance(subjects, list)
        and len(subjects) == 3
        and all(isinstance(item, str) and 15 <= len(item) <= 70 for item in subjects)
    )
    _check(checks, "newsletter.subjects", subjects_ok, "exactly 3 subject lines, each 15-70 characters")
    preview = str(news.get("preview_text", ""))
    _check(checks, "newsletter.preview", 40 <= len(preview) <= 120, f"preview text is {len(preview)} characters; need 40-120")
    sections = news.get("sections")
    sections_ok = (
        isinstance(sections, list)
        and len(sections) >= 2
        and all(
            isinstance(section, dict)
            and str(section.get("heading", "")).strip()
            and len(str(section.get("body", ""))) >= 40
            for section in sections
        )
    )
    _check(checks, "newsletter.sections", sections_ok, "at least two sections, each with a heading and 40 or more characters")

    video = pack.get("short_video") if isinstance(pack.get("short_video"), dict) else {}
    duration = video.get("duration_seconds")
    duration_ok = isinstance(duration, int) and not isinstance(duration, bool) and 20 <= duration <= 45
    _check(checks, "short_video.duration", duration_ok, "duration_seconds must be an integer from 20 to 45")
    video_hook = str(video.get("hook", ""))
    _check(checks, "short_video.hook", 0 < len(video_hook) <= 90, "hook is required and must be 90 characters or fewer")
    beats = video.get("beats")
    beats_ok = (
        isinstance(beats, list)
        and len(beats) >= 3
        and all(
            isinstance(beat, dict) and str(beat.get("spoken", "")).strip() and str(beat.get("on_screen", "")).strip()
            for beat in beats
        )
    )
    _check(checks, "short_video.beats", beats_ok, "at least 3 beats, each with spoken words and on-screen text")
    cta = str(video.get("cta", "")).strip()
    _check(checks, "short_video.cta", bool(cta), "a call to action is required")
    if duration_ok and beats_ok:
        words = spoken_words(pack)
        expected = words / 150 * 60
        _check(
            checks,
            "short_video.pace",
            abs(expected - duration) <= 8,
            f"{words} spoken words is about {expected:.1f}s at 150 wpm; duration is {duration}s",
        )
    return {"ok": all(item["ok"] for item in checks), "checks": checks}


def format_report(result: dict) -> str:
    lines = ["PASS" if result["ok"] else "FAIL", ""]
    for item in result["checks"]:
        mark = "ok" if item["ok"] else "no"
        lines.append(f"  {mark}  {item['name']}: {item['detail']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a content pack JSON file.")
    parser.add_argument("pack", type=Path)
    parser.add_argument("--json", dest="json_out", type=Path)
    args = parser.parse_args(argv)
    try:
        pack = json.loads(args.pack.read_text(encoding="utf-8"))
        result = check_pack(pack)
    except FileNotFoundError:
        print(f"File not found: {args.pack}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json_out:
        args.json_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(format_report(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
