from __future__ import annotations

import json

from conftest import EXAMPLES, load_script

qa = load_script("qa-test-generation", "generate_tests.py")
EXAMPLE = EXAMPLES / "qa-test-generation"


def test_checkout_suite_matches_the_committed_files():
    document = json.loads((EXAMPLE / "checkout.json").read_text(encoding="utf-8"))
    result = qa.generate(document)
    committed = json.loads((EXAMPLE / "checkout.cases.json").read_text(encoding="utf-8"))
    assert {"feature": result["feature"], "uncovered_acceptance": result["uncovered_acceptance"], "cases": result["cases"]} == committed
    assert result["gherkin"] == (EXAMPLE / "checkout.feature").read_text(encoding="utf-8")
    assert result["playwright"] == (EXAMPLE / "checkout.spec.ts").read_text(encoding="utf-8")
    assert result["matrix"] == (EXAMPLE / "checkout.traceability.md").read_text(encoding="utf-8")


def test_risk_bands_and_negative_word_boundaries():
    cases = json.loads((EXAMPLE / "checkout.cases.json").read_text(encoding="utf-8"))["cases"]
    by_id = {case["id"]: case for case in cases}
    assert len(cases) == 20
    happy = by_id["US-14-TC-001"]
    assert happy["type"] == "positive"
    assert happy["priority"] == "P0"
    assert happy["risk_score"] == 20
    assert "unexpired" in happy["title"]
    assert by_id["US-14-TC-002"]["type"] == "negative"
    shipping = by_id["US-30-TC-001"]
    assert shipping["risk_score"] == 12
    assert shipping["priority"] == "P0"
    assert by_id["US-3-TC-001"]["priority"] == "P3"
    assert by_id["US-3-TC-001"]["automation_candidate"] is False
    assert by_id["US-14-TC-009"]["technique"] == "state-transition"
    assert "rejected" in by_id["US-14-TC-010"]["expected"].lower()
    traces = {trace for case in cases for trace in case["traces"]}
    assert traces == {"AC-1", "AC-2", "AC-3", "AC-4", "AC-5"}


def test_gherkin_and_playwright_skeletons_are_ordered():
    feature = (EXAMPLE / "checkout.feature").read_text(encoding="utf-8")
    spec = (EXAMPLE / "checkout.spec.ts").read_text(encoding="utf-8")
    assert feature.startswith("Feature: Checkout\n")
    assert feature.count("Scenario:") == 20
    assert "@p0 @US-14 @acceptance @positive" in feature
    assert 'import { test, expect } from "@playwright/test";' in spec
    assert spec.count("test.fixme(") == 20
    assert spec.index("US-14-TC-001") < spec.index("US-30-TC-001") < spec.index("US-3-TC-001")
    assert 'await page.goto("/checkout");' in spec


def test_malformed_requirements_exit_two():
    assert qa.main(["examples/qa-test-generation/checkout.json", "--out-dir", "examples/qa-test-generation", "--stem", "checkout"]) == 0
    try:
        qa.generate({"feature": "Checkout", "stories": []})
    except qa.RequirementsError as exc:
        assert "feature" in str(exc) or "story" in str(exc).lower()
    else:
        raise AssertionError("empty stories should fail")
