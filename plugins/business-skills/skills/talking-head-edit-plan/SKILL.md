---
name: talking-head-edit-plan
description: Builds a talking-head edit plan from a timestamped transcript, including a cut list, a CMX 3600 EDL, filler and dead-air removals, chapter markers, and jump-cut warnings. Use when the user provides an SRT, VTT, or timestamped transcript and wants an edit decision list, a paper edit, or a cut plan for a talking-head video.
license: MIT
compatibility: Requires Python 3.11 or newer. No network calls. The script writes an EDL and JSON. It does not render picture or audio.
metadata:
  author: Mustafa
  version: "1.0.0"
---

# Talking-head edit plan

Turn a timestamped transcript into a cut a person can execute. The numbers come from the script. Your job is to get the transcript into SRT, VTT, or JSON cues, then explain the plan without changing a timecode by hand.

## Steps

1. If the user pastes an untimed transcript, stop and ask for timestamps. Do not invent them.
2. If they paste a loose timed transcript, normalize it to SRT. Keep their words. Do not silently delete a sentence you think is boring. The script decides filler. You do not.
3. Run it from this skill directory:

```bash
python scripts/build_edl.py take.srt --fps 30 --json plan.json --edl take.edl
```

Defaults are 30 fps, an 800 ms pause threshold, and 120 ms of retained breath. Pass `--fps 24` or `--fps 25` when they tell you the master rate. Do not pick 29.97. This EDL is non-drop and wants an integer rate.

4. Read keeps, removed lines, chapters, b-roll windows, and warnings. Rules are in [edit rules](references/edit-rules.md).
5. Give the user the EDL, the cut list, and a short note: what was dropped, where a cover shot was suggested, and any `short-cut` warning. Quote milliseconds or timecode. Do not round them into "about three seconds" when the file has the frame.

## How to talk about the plan

Lead with program duration versus source duration so they can see what the tighten did. Then list filler lines that were removed, in order. Then any dead air. If a chapter cue was present, name it at its program time.

Do not promise the edit will "feel natural". Say what was removed and what was kept.

## Examples

`examples/talking-head-edit-plan/short.srt` drops a single "Um" and tightens the gap that follows. The EDL has two events. `walkthrough.srt` adds a chapter cue, a long stretch that earns a cover window, and a second filler.

## Out of scope

Do not export a finished video, pick music, or rewrite the speaker's sentences to be punchier. If they want a different pause length, change the flag and rerun. A hand-edited timecode will not match the JSON, and the JSON is the record.
