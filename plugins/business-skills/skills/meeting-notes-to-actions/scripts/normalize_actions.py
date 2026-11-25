#!/usr/bin/env python3
"""Normalize extracted meeting actions: dates, owners, duplicates, and a follow-up note.

The model extracts decisions and actions from messy notes. This script checks
that extraction. It does not summarize a transcript by itself.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


class MeetingError(Exception):
    """The extracted meeting file cannot be normalized."""


def parse_meeting_date(raw: str) -> date:
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError as exc:
        raise MeetingError(f"meeting_date must be YYYY-MM-DD, got {raw!r}") from exc


def resolve_due(raw: object, meeting: date) -> tuple[str | None, str]:
    text = str(raw or "").strip()
    if not text:
        return None, "missing"
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat(), "explicit"
    except ValueError:
        pass
    lowered = text.lower()
    if lowered == "today":
        return meeting.isoformat(), "relative"
    if lowered == "tomorrow":
        return (meeting + timedelta(days=1)).isoformat(), "relative"
    if lowered in WEEKDAYS:
        delta = (WEEKDAYS[lowered] - meeting.weekday()) % 7
        return (meeting + timedelta(days=delta)).isoformat(), "relative"
    return None, "unparsed"


def action_key(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text.strip().lower())
    return collapsed.strip(" .")


def normalize(document: dict) -> dict:
    if not isinstance(document, dict):
        raise MeetingError("Meeting JSON must be an object.")
    title = str(document.get("title", "")).strip()
    if not title:
        raise MeetingError("title is required")
    meeting = parse_meeting_date(str(document.get("meeting_date", "")))
    decisions = [str(item).strip() for item in document.get("decisions") or [] if str(item).strip()]
    questions = [str(item).strip() for item in document.get("open_questions") or [] if str(item).strip()]
    grouped: dict[str, dict] = {}
    order: list[str] = []
    for raw in document.get("actions") or []:
        if not isinstance(raw, dict):
            raise MeetingError("each action must be an object")
        text = str(raw.get("text", "")).strip()
        if not text:
            raise MeetingError("an action is missing text")
        key = action_key(text)
        due, source = resolve_due(raw.get("due"), meeting)
        owner = str(raw.get("owner", "")).strip()
        if key not in grouped:
            grouped[key] = {
                "text": text,
                "owner": owner,
                "due": due,
                "due_source": source,
                "issues": [],
            }
            order.append(key)
            continue
        current = grouped[key]
        if owner and current["owner"] and owner != current["owner"]:
            if "owner-conflict" not in current["issues"]:
                current["issues"].append("owner-conflict")
        elif owner and not current["owner"]:
            current["owner"] = owner
        if source == "unparsed":
            if "unparsed-date" not in current["issues"]:
                current["issues"].append("unparsed-date")
            continue
        if due and current["due"] and due != current["due"]:
            if source == "relative" and current["due_source"] == "explicit":
                if "relative-date-ignored" not in current["issues"]:
                    current["issues"].append("relative-date-ignored")
            elif source == "explicit" and current["due_source"] == "relative":
                current["due"] = due
                current["due_source"] = "explicit"
                if "relative-date-ignored" not in current["issues"]:
                    current["issues"].append("relative-date-ignored")
            elif "date-conflict" not in current["issues"]:
                current["issues"].append("date-conflict")
                if due < current["due"]:
                    current["due"] = due
                    current["due_source"] = source
        elif due and not current["due"]:
            current["due"] = due
            current["due_source"] = source
    actions = []
    for key in order:
        item = grouped[key]
        if item["due_source"] == "unparsed":
            if "unparsed-date" not in item["issues"]:
                item["issues"].append("unparsed-date")
        if not item["owner"]:
            item["owner"] = "unassigned"
            item["issues"].append("missing-owner")
        item.pop("due_source", None)
        actions.append(item)
    actions.sort(key=lambda item: (item["due"] is None, item["due"] or "", item["text"].lower()))
    for index, item in enumerate(actions, start=1):
        item["id"] = f"A-{index}"
    normalized = {
        "title": title,
        "meeting_date": meeting.isoformat(),
        "decisions": decisions,
        "actions": [
            {
                "id": item["id"],
                "text": item["text"],
                "owner": item["owner"],
                "due": item["due"],
                "issues": item["issues"],
            }
            for item in actions
        ],
        "open_questions": questions,
    }
    return normalized


def render_markdown(document: dict) -> str:
    lines = [
        f"# {document['title']}",
        "",
        f"Meeting date: {document['meeting_date']}",
        "",
        "## Decisions",
        "",
    ]
    if document["decisions"]:
        lines.extend(f"- {item}" for item in document["decisions"])
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Actions", ""])
    if document["actions"]:
        for action in document["actions"]:
            due = action["due"] or "no date"
            extra = f" ({', '.join(action['issues'])})" if action["issues"] else ""
            lines.append(f"- {action['id']} {action['owner']} — {action['text']} — due {due}{extra}")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Open questions", ""])
    if document["open_questions"]:
        lines.extend(f"- {item}" for item in document["open_questions"])
    else:
        lines.append("- None recorded.")
    lines.append("")
    return "\n".join(lines)


def render_email(document: dict) -> str:
    lines = [
        f"Subject: Follow-up: {document['title']}",
        "",
        f"Notes from {document['meeting_date']}. Reply if an owner or a date is wrong.",
        "",
        "Decisions",
    ]
    lines.extend(f"- {item}" for item in document["decisions"] or ["None recorded."])
    lines.append("")
    lines.append("Actions")
    if document["actions"]:
        for action in document["actions"]:
            due = action["due"] or "no date"
            note = ""
            if "missing-owner" in action["issues"]:
                note = " (needs an owner)"
            lines.append(f"- {action['owner']} — {action['text']} — due {due}{note}")
    else:
        lines.append("- None recorded.")
    lines.append("")
    lines.append("Open questions")
    lines.extend(f"- {item}" for item in document["open_questions"] or ["None."])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize extracted meeting actions.")
    parser.add_argument("extracted", type=Path)
    parser.add_argument("--json", dest="json_out", type=Path)
    parser.add_argument("--markdown", dest="markdown_out", type=Path)
    parser.add_argument("--email", dest="email_out", type=Path)
    args = parser.parse_args(argv)
    try:
        source = json.loads(args.extracted.read_text(encoding="utf-8"))
        document = normalize(source)
    except FileNotFoundError:
        print(f"File not found: {args.extracted}", file=sys.stderr)
        return 2
    except (MeetingError, json.JSONDecodeError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    markdown = render_markdown(document)
    email = render_email(document)
    if args.json_out:
        args.json_out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.write_text(markdown, encoding="utf-8")
    if args.email_out:
        args.email_out.write_text(email, encoding="utf-8")
    issue_count = sum(len(action["issues"]) for action in document["actions"])
    print(f"{document['title']}: {len(document['actions'])} actions, {issue_count} issues")
    sys.stdout.write(email)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
