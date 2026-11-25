from __future__ import annotations

import json

from conftest import EXAMPLES, load_script

content = load_script("content-repurposing", "check_pack.py")
meeting = load_script("meeting-notes-to-actions", "normalize_actions.py")
fit = load_script("proposal-writer", "score_job_fit.py")
lint = load_script("proposal-writer", "lint_proposal.py")


def test_content_pack_passes_and_a_long_post_fails():
    pack = json.loads((EXAMPLES / "content-repurposing" / "pack.json").read_text(encoding="utf-8"))
    result = content.check_pack(pack)
    assert result["ok"] is True
    assert content.main([str(EXAMPLES / "content-repurposing" / "pack.json")]) == 0
    pack["x_thread"][0]["text"] = "x" * 281
    failed = content.check_pack(pack)
    assert failed["ok"] is False
    assert any(item["name"] == "x_thread.1.length" and not item["ok"] for item in failed["checks"])


def test_meeting_actions_merge_and_keep_the_missing_owner():
    source = json.loads((EXAMPLES / "meeting-notes-to-actions" / "extracted.json").read_text(encoding="utf-8"))
    document = meeting.normalize(source)
    expected = json.loads((EXAMPLES / "meeting-notes-to-actions" / "expected.json").read_text(encoding="utf-8"))
    assert document == expected
    email = meeting.render_email(document)
    markdown = meeting.render_markdown(document)
    assert email == (EXAMPLES / "meeting-notes-to-actions" / "expected-email.txt").read_text(encoding="utf-8")
    assert markdown == (EXAMPLES / "meeting-notes-to-actions" / "expected.md").read_text(encoding="utf-8")
    assert "needs an owner" in email
    assert document["actions"][0]["owner"] == "unassigned"
    assert document["actions"][1]["due"] == "2026-04-11"
    assert "relative-date-ignored" in document["actions"][1]["issues"]


def test_proposal_fit_and_lint():
    job = (EXAMPLES / "proposal-writer" / "job-post.txt").read_text(encoding="utf-8")
    profile = json.loads((EXAMPLES / "proposal-writer" / "profile.json").read_text(encoding="utf-8"))
    result = fit.score_fit(job, profile)
    expected = json.loads((EXAMPLES / "proposal-writer" / "expected-fit.json").read_text(encoding="utf-8"))
    assert result == expected
    assert result["fit_score"] == 30
    assert result["band"] == "decline"
    assert result["red_flags"] == ["unpaid-sample", "urgent"]
    assert result["budget"] == {"kind": "hourly", "low": 30, "high": 45, "currency": "USD"}
    draft = (EXAMPLES / "proposal-writer" / "expected-proposal.md").read_text(encoding="utf-8")
    assert lint.lint_proposal(draft, profile) == []
    assert "paid pilot" in draft.lower() or "paid" in draft.lower()
    broken = draft.replace(profile["proof"][0], "I edited 400 videos for Fortune 100 brands.")
    problems = lint.lint_proposal(broken, profile)
    assert any(item["path"] == "Proof" for item in problems)
