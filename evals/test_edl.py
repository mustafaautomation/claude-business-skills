from __future__ import annotations

import json

from conftest import EXAMPLES, load_script

edl = load_script("talking-head-edit-plan", "build_edl.py")
EXAMPLE = EXAMPLES / "talking-head-edit-plan"


def test_frame_rounding_and_short_edit():
    assert edl.ms_to_frames(3120, 30) == 94
    assert edl.frames_to_tc(94, 30) == "00:00:03:04"
    assert edl.frames_to_tc(214, 30) == "00:00:07:04"
    cues, _fps = edl.load_cues(EXAMPLE / "short.srt")
    plan = edl.build_plan(cues)
    assert plan["edl"] == (EXAMPLE / "short.edl").read_text(encoding="utf-8")
    assert plan == json.loads((EXAMPLE / "short.json").read_text(encoding="utf-8"))
    assert plan["program_duration_ms"] == 7120
    assert [item["reason"] for item in plan["removed"]] == ["filler", "dead-air"]
    assert plan["removed"][0]["text"] == "Um"
    assert plan["keeps"][0]["end_ms"] == 3120
    assert plan["keeps"][1]["start_ms"] == 5000


def test_walkthrough_chapter_cover_and_filler_phrase():
    cues, _fps = edl.load_cues(EXAMPLE / "walkthrough.srt")
    plan = edl.build_plan(cues)
    assert plan == json.loads((EXAMPLE / "walkthrough.json").read_text(encoding="utf-8"))
    assert plan["chapters"] == [{"program_ms": 0, "title": "Open on the promise"}]
    assert plan["broll"]
    assert plan["broll"][0]["program_start_ms"] == 6620
    reasons = [item["reason"] for item in plan["removed"]]
    assert reasons.count("filler") == 2
    assert edl.is_filler("Um, you know")
    assert not edl.is_filler("I think you know the cut")
    assert not edl.is_filler("I like this cut")


def test_overlapping_cues_are_rejected():
    try:
        edl.build_plan(
            [
                {"start_ms": 0, "end_ms": 1000, "text": "Hello"},
                {"start_ms": 500, "end_ms": 1500, "text": "Overlap"},
            ]
        )
    except edl.TranscriptError as exc:
        assert "overlap" in str(exc).lower()
    else:
        raise AssertionError("overlap should fail")
