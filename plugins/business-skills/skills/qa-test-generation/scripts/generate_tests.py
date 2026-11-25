#!/usr/bin/env python3
"""Turn a requirements JSON file into prioritized tests, Gherkin, and Playwright skeletons.

The script does not invent acceptance criteria. It expands the criteria, fields,
states, and decision-table rules that are already in the file, then ranks them
by impact, likelihood, and a short list of critical areas.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CRITICAL_AREAS = {"payment", "pricing", "auth", "privacy", "data-loss"}
RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
NEGATIVE_CUES = (
    r"\brejected\b",
    r"\bexpired\b",
    r"\binvalid\b",
    r"\berror\b",
    r"\bunchanged\b",
    r"\bcannot\b",
    r"\bmust not\b",
    r"\bfails\b",
    r"\bdenied\b",
    r"\bnot applied\b",
)


class RequirementsError(Exception):
    """The requirements file is missing something the generator needs."""


def priority_band(score: int) -> str:
    if score >= 16:
        return "P0"
    if score >= 10:
        return "P1"
    if score >= 5:
        return "P2"
    return "P3"


def raise_priority(current: str, floor: str) -> str:
    if RANK[current] > RANK[floor]:
        return floor
    return current


def story_priority(story: dict) -> tuple[int, str]:
    risks = story["risks"]
    impact = int(risks["impact"])
    likelihood = int(risks["likelihood"])
    if not 1 <= impact <= 5 or not 1 <= likelihood <= 5:
        raise RequirementsError(f"{story['id']}: impact and likelihood must be integers from 1 to 5")
    score = impact * likelihood
    band = priority_band(score)
    areas = {str(area).lower() for area in risks.get("areas", [])}
    if areas & CRITICAL_AREAS:
        floor = "P0" if impact >= 4 else "P1"
        band = raise_priority(band, floor)
    return score, band


def is_negative_text(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(cue, lowered) for cue in NEGATIVE_CUES)


def _require(story: dict, key: str) -> object:
    if key not in story:
        raise RequirementsError(f"{story.get('id', '?')}: missing {key}")
    return story[key]


def _case(
    story: dict,
    number: int,
    title: str,
    technique: str,
    kind: str,
    traces: list[str],
    when: str,
    expected: str,
    score: int,
    band: str,
) -> dict:
    return {
        "id": f"{story['id']}-TC-{number:03d}",
        "story_id": story["id"],
        "title": title,
        "priority": band,
        "risk_score": score,
        "technique": technique,
        "type": kind,
        "traces": traces,
        "preconditions": f"A {story['persona']} can {story['want']}",
        "steps": [when],
        "expected": expected,
        "automation_candidate": band in {"P0", "P1"},
    }


def _num(value: object) -> str:
    text = format(value, "f") if not isinstance(value, str) else value
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        return "0"
    return text


def expand_story(story: dict) -> list[dict]:
    for key in ("id", "title", "persona", "want", "outcome", "acceptance", "risks"):
        _require(story, key)
    score, band = story_priority(story)
    cases: list[dict] = []

    def add(title: str, technique: str, kind: str, traces: list[str], when: str, expected: str) -> None:
        cases.append(_case(story, len(cases) + 1, title, technique, kind, traces, when, expected, score, band))

    acceptance = story["acceptance"]
    if not isinstance(acceptance, list) or not acceptance:
        raise RequirementsError(f"{story['id']}: acceptance must be a non-empty list")
    for criterion in acceptance:
        text = str(criterion.get("text", "")).strip()
        criterion_id = str(criterion.get("id", "")).strip()
        if not text or not criterion_id:
            raise RequirementsError(f"{story['id']}: each acceptance item needs an id and text")
        negative = is_negative_text(text)
        add(
            title=text.rstrip("."),
            technique="acceptance",
            kind="negative" if negative else "positive",
            traces=[criterion_id],
            when=f"The acceptance criterion holds: {text}",
            expected=(
                "The system refuses the action and leaves protected totals unchanged."
                if negative
                else story["outcome"]
            ),
        )
    for field in story.get("fields") or []:
        name = str(field["name"])
        kind = str(field.get("type", "string"))
        if kind == "string":
            minimum = int(field.get("min_length", 0) or 0)
            maximum = field.get("max_length")
            if minimum:
                add(
                    f"{name} length {minimum} is accepted",
                    "boundary",
                    "positive",
                    [],
                    f"{name} is {'a' * minimum} (length {minimum})",
                    "The value is accepted.",
                )
                add(
                    f"{name} length {minimum - 1} is rejected",
                    "boundary",
                    "negative",
                    [],
                    f"{name} is {'a' * (minimum - 1)} (length {minimum - 1})",
                    "The value is rejected with a validation message.",
                )
            if maximum is not None:
                maximum = int(maximum)
                add(
                    f"{name} length {maximum} is accepted",
                    "boundary",
                    "positive",
                    [],
                    f"{name} is {'a' * maximum} (length {maximum})",
                    "The value is accepted.",
                )
                add(
                    f"{name} length {maximum + 1} is rejected",
                    "boundary",
                    "negative",
                    [],
                    f"{name} is {'a' * (maximum + 1)} (length {maximum + 1})",
                    "The value is rejected with a validation message.",
                )
            if field.get("required"):
                add(
                    f"{name} is empty and is rejected",
                    "boundary",
                    "negative",
                    [],
                    f"{name} is empty",
                    "The value is rejected with a validation message.",
                )
        elif kind == "number":
            minimum = field.get("minimum")
            maximum = field.get("maximum")
            if minimum is None or maximum is None:
                raise RequirementsError(f"{story['id']}.{name}: number fields need minimum and maximum")
            low = _decimal(minimum)
            high = _decimal(maximum)
            step = _decimal("0.01")
            points = (
                (f"{name} at minimum { _num(low) } is accepted", "positive", low, "accepted"),
                (f"{name} below minimum ({ _num(low - step) }) is rejected", "negative", low - step, "rejected"),
                (f"{name} at maximum { _num(high) } is accepted", "positive", high, "accepted"),
                (f"{name} above maximum ({ _num(high + step) }) is rejected", "negative", high + step, "rejected"),
            )
            for title, case_type, value, label in points:
                add(
                    title,
                    "boundary",
                    case_type,
                    [],
                    f"{name} is {_num(value)}",
                    "The value is accepted." if label == "accepted" else "The value is rejected with a validation message.",
                )
        else:
            raise RequirementsError(f"{story['id']}.{name}: unsupported field type {kind}")
    for rule in story.get("rules") or []:
        conditions = rule.get("when") or {}
        if not isinstance(conditions, dict) or not conditions:
            raise RequirementsError(f"{story['id']}: each rule needs a when object")
        outcome = str(rule.get("then", "")).strip()
        if not outcome:
            raise RequirementsError(f"{story['id']}: each rule needs a then")
        rendered = " ".join(f"{key}={value}" for key, value in conditions.items())
        case_type = "negative" if rule.get("type") == "negative" else "positive"
        add(
            f"rule {rendered} -> {outcome}",
            "decision-table",
            case_type,
            [],
            f"Conditions are {rendered}",
            outcome,
        )
    states = story.get("states") or []
    for machine in states:
        machine_name = str(machine.get("name", "state"))
        for transition in machine.get("transitions") or []:
            origin = transition["from"]
            event = transition["event"]
            target = transition["to"]
            rejected = str(transition.get("note", "")).lower() == "rejected"
            add(
                f"{machine_name}: {origin} --{event}--> {target}",
                "state-transition",
                "negative" if rejected else "positive",
                [],
                f"The {machine_name} state is {origin} and {event} happens",
                (
                    f"The event is rejected and the state stays {target}."
                    if rejected
                    else f"The state is {target}."
                ),
            )
    return cases


def _decimal(value: object):
    from decimal import Decimal

    return Decimal(str(value))


def uncovered_acceptance(stories: list[dict], cases: list[dict]) -> list[str]:
    covered = {trace for case in cases for trace in case["traces"]}
    missing = []
    for story in stories:
        for criterion in story["acceptance"]:
            if criterion["id"] not in covered:
                missing.append(criterion["id"])
    return missing


def generate(document: dict) -> dict:
    if not isinstance(document, dict):
        raise RequirementsError("Requirements JSON must be an object.")
    feature = str(document.get("feature", "")).strip()
    stories = document.get("stories")
    if not feature or not isinstance(stories, list) or not stories:
        raise RequirementsError("The file needs a feature name and at least one story.")
    cases: list[dict] = []
    for story in stories:
        cases.extend(expand_story(story))
    missing = uncovered_acceptance(stories, cases)
    ordered = sorted(cases, key=lambda case: (RANK[case["priority"]], case["story_id"], case["id"]))
    return {
        "feature": feature,
        "cases": cases,
        "ordered_cases": ordered,
        "uncovered_acceptance": missing,
        "gherkin": render_gherkin(feature, cases),
        "playwright": render_playwright(feature, ordered),
        "matrix": render_matrix(feature, cases),
    }


def render_gherkin(feature: str, cases: list[dict]) -> str:
    lines = [
        f"Feature: {feature}",
        "  Risk-based scenarios generated from the requirements file.",
        "  Exploratory charters are written separately and are not in this file.",
        "",
    ]
    for case in cases:
        tags = " ".join(
            [
                f"@{case['priority'].lower()}",
                f"@{case['story_id']}",
                f"@{case['technique']}",
                f"@{case['type']}",
            ]
        )
        lines.append(f"  {tags}")
        lines.append(f"  Scenario: {case['id']} {case['title']}")
        lines.append(f"    Given {case['preconditions']}")
        lines.append(f"    When {case['steps'][0]}")
        lines.append(f"    Then {case['expected']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _route(feature: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", feature.lower()).strip("-")
    return "/" + (slug or "app")


def render_playwright(feature: str, cases: list[dict]) -> str:
    route = _route(feature)
    lines = [
        'import { test, expect } from "@playwright/test";',
        "",
        "// Generated skeletons. test.fixme keeps them out of a green run until locators are filled in.",
        f"// Feature: {feature}",
        "",
        f"test.describe({json.dumps(feature)}, () => {{",
    ]
    for case in cases:
        title = f"[{case['priority']}] {case['id']} {case['title']} @{case['priority'].lower()} @{case['story_id']}"
        title = title.replace('"', "'")
        traces = ", ".join(case["traces"]) or "none"
        lines.append(f"  test.fixme({json.dumps(title)}, async ({{ page }}) => {{")
        lines.append(f"    // technique: {case['technique']}")
        lines.append(f"    // type: {case['type']}")
        lines.append(f"    // traces: {traces}")
        lines.append(f"    // risk: {case['risk_score']}")
        lines.append(f"    await page.goto({json.dumps(route)});")
        lines.append(f"    // When: {case['steps'][0]}")
        lines.append(f"    // Then: {case['expected']}")
        lines.append('    await expect(page.getByTestId("result")).toBeVisible();')
        lines.append("  });")
        lines.append("")
    lines.append("});")
    lines.append("")
    return "\n".join(lines)


def render_matrix(feature: str, cases: list[dict]) -> str:
    lines = [
        f"# Traceability — {feature}",
        "",
        "Generated from the requirements file. Do not delete a row because it feels redundant; mark it out of scope in a review note instead.",
        "",
        "| Test | Story | Priority | Technique | Type | Traces | Automated skeleton | Title |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in cases:
        traces = ", ".join(case["traces"]) or "—"
        auto = "yes" if case["automation_candidate"] else "later"
        title = case["title"].replace("|", "/")
        lines.append(
            f"| {case['id']} | {case['story_id']} | {case['priority']} | {case['technique']} | {case['type']} | {traces} | {auto} | {title} |"
        )
    lines.append("")
    return "\n".join(lines)


def load_document(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_outputs(result: dict, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "feature": result["feature"],
        "uncovered_acceptance": result["uncovered_acceptance"],
        "cases": result["cases"],
    }
    (out_dir / f"{stem}.cases.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (out_dir / f"{stem}.feature").write_text(result["gherkin"], encoding="utf-8")
    (out_dir / f"{stem}.spec.ts").write_text(result["playwright"], encoding="utf-8")
    (out_dir / f"{stem}.traceability.md").write_text(result["matrix"], encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate prioritized tests from requirements JSON.")
    parser.add_argument("requirements", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--stem", default="tests")
    args = parser.parse_args(argv)
    try:
        result = generate(load_document(args.requirements))
    except FileNotFoundError:
        print(f"File not found: {args.requirements}", file=sys.stderr)
        return 2
    except (RequirementsError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    write_outputs(result, args.out_dir, args.stem)
    counts = {band: sum(1 for case in result["cases"] if case["priority"] == band) for band in RANK}
    print(
        f"{result['feature']}: {len(result['cases'])} tests "
        f"(P0 {counts['P0']}, P1 {counts['P1']}, P2 {counts['P2']}, P3 {counts['P3']})"
    )
    if result["uncovered_acceptance"]:
        print("Uncovered acceptance: " + ", ".join(result["uncovered_acceptance"]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
