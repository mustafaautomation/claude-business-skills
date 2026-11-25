#!/usr/bin/env python3
"""Build a talking-head cut list and a CMX 3600 EDL from a timestamped transcript.

Out points are exclusive. Frames are milliseconds times fps, with halves
rounded away from zero by adding half a frame before integer division.
Filler-only cues are dropped. Silence longer than the pause threshold is
tightened to the retained pause. The script does not render picture.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FILLER_WORDS = {"um", "uh", "er", "ah", "hmm", "uhh", "umm"}
FILLER_PHRASES = (("you", "know"), ("i", "mean"), ("kind", "of"), ("sort", "of"))
TIME_RE = re.compile(
    r"(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})[,.](?P<ms>\d{3})"
)
CHAPTER_RE = re.compile(r"^\[chapter\]\s+(.+)$", re.I)


class TranscriptError(Exception):
    """The transcript cannot be turned into an edit."""


def ms_to_frames(milliseconds: int, fps: int) -> int:
    if milliseconds < 0:
        raise TranscriptError("Negative timecode")
    return (milliseconds * fps + 500) // 1000


def frames_to_tc(frames: int, fps: int) -> str:
    if frames < 0:
        raise TranscriptError("Negative frame count")
    frames_part = frames % fps
    total_seconds = frames // fps
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames_part:02d}"


def stamp_to_ms(stamp: str) -> int:
    match = TIME_RE.fullmatch(stamp.strip())
    if not match:
        raise TranscriptError(f"Bad timestamp: {stamp}")
    parts = match.groupdict()
    return (
        int(parts["h"]) * 3_600_000
        + int(parts["m"]) * 60_000
        + int(parts["s"]) * 1000
        + int(parts["ms"])
    )


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def is_filler(text: str) -> bool:
    tokens = _tokens(text)
    if not tokens:
        return True
    changed = True
    while tokens and changed:
        changed = False
        kept = [token for token in tokens if token not in FILLER_WORDS]
        if kept != tokens:
            tokens = kept
            changed = True
        for phrase in FILLER_PHRASES:
            size = len(phrase)
            index = 0
            next_tokens: list[str] = []
            removed = False
            while index < len(tokens):
                if tuple(tokens[index : index + size]) == phrase:
                    removed = True
                    index += size
                    continue
                next_tokens.append(tokens[index])
                index += 1
            if removed:
                tokens = next_tokens
                changed = True
                break
    return not tokens


def parse_srt(text: str) -> list[dict]:
    blocks = re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip())
    cues = []
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        if re.fullmatch(r"\d+", lines[0]):
            lines = lines[1:]
        if not lines or "-->" not in lines[0]:
            continue
        start_raw, end_raw = [part.strip().split()[0] for part in lines[0].split("-->")]
        body = " ".join(lines[1:]).strip()
        start = stamp_to_ms(start_raw)
        end = stamp_to_ms(end_raw)
        if end <= start:
            raise TranscriptError(f"Cue ends before it starts: {body!r}")
        cues.append({"start_ms": start, "end_ms": end, "text": body})
    if not cues:
        raise TranscriptError("No cues found.")
    return cues


def parse_vtt(text: str) -> list[dict]:
    stripped = re.sub(r"^WEBVTT[^\n]*\n", "", text.strip(), count=1)
    return parse_srt(stripped)


def load_cues(path: Path) -> tuple[list[dict], int | None]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(text)
        cues = payload["cues"] if isinstance(payload, dict) else payload
        fps = payload.get("fps") if isinstance(payload, dict) else None
        normalized = []
        for cue in cues:
            normalized.append(
                {
                    "start_ms": int(cue["start_ms"]),
                    "end_ms": int(cue["end_ms"]),
                    "text": str(cue["text"]),
                }
            )
        return normalized, int(fps) if fps else None
    if suffix == ".vtt":
        return parse_vtt(text), None
    return parse_srt(text), None


def _check_order(cues: list[dict]) -> None:
    previous = -1
    for cue in cues:
        if cue["start_ms"] < previous:
            raise TranscriptError("Cues are not in time order.")
        if cue["end_ms"] <= cue["start_ms"]:
            raise TranscriptError("Cue ends before it starts.")
        previous = cue["start_ms"]
    for earlier, later in zip(cues, cues[1:]):
        if later["start_ms"] < earlier["end_ms"]:
            raise TranscriptError(
                f"Cues overlap: {earlier['text']!r} and {later['text']!r}"
            )


def build_plan(
    cues: list[dict],
    fps: int = 30,
    max_pause_ms: int = 800,
    retained_pause_ms: int = 120,
    title: str = "talking-head-cut",
) -> dict:
    if fps <= 0 or int(fps) != fps:
        raise TranscriptError("fps must be a positive integer. This EDL is non-drop.")
    fps = int(fps)
    ordered = sorted(cues, key=lambda cue: cue["start_ms"])
    _check_order(ordered)
    removed = []
    kept_cues = []
    for cue in ordered:
        if is_filler(cue["text"]):
            removed.append(
                {
                    "start_ms": cue["start_ms"],
                    "end_ms": cue["end_ms"],
                    "reason": "filler",
                    "text": cue["text"],
                }
            )
        else:
            kept_cues.append(cue)
    keeps: list[dict] = []
    if kept_cues:
        current = {
            "start_ms": kept_cues[0]["start_ms"],
            "end_ms": kept_cues[0]["end_ms"],
            "texts": [kept_cues[0]["text"]],
            "cues": [kept_cues[0]],
        }
        for nxt in kept_cues[1:]:
            gap = nxt["start_ms"] - current["end_ms"]
            if gap <= max_pause_ms:
                current["end_ms"] = nxt["end_ms"]
                current["texts"].append(nxt["text"])
                current["cues"].append(nxt)
                continue
            tightened = min(current["end_ms"] + retained_pause_ms, nxt["start_ms"])
            current["end_ms"] = tightened
            keeps.append(current)
            if tightened < nxt["start_ms"]:
                removed.append(
                    {
                        "start_ms": tightened,
                        "end_ms": nxt["start_ms"],
                        "reason": "dead-air",
                        "text": "",
                    }
                )
            current = {
                "start_ms": nxt["start_ms"],
                "end_ms": nxt["end_ms"],
                "texts": [nxt["text"]],
                "cues": [nxt],
            }
        keeps.append(current)
    program = 0
    planned = []
    chapters = []
    for keep in keeps:
        duration = keep["end_ms"] - keep["start_ms"]
        record = {
            "start_ms": keep["start_ms"],
            "end_ms": keep["end_ms"],
            "program_start_ms": program,
            "program_end_ms": program + duration,
            "text": " ".join(keep["texts"]),
        }
        for cue in keep["cues"]:
            match = CHAPTER_RE.match(cue["text"].strip())
            if match:
                chapters.append(
                    {
                        "program_ms": program + (cue["start_ms"] - keep["start_ms"]),
                        "title": match.group(1).strip(),
                    }
                )
        planned.append(record)
        program += duration
    warnings = []
    for keep in planned:
        if keep["end_ms"] - keep["start_ms"] < 400:
            warnings.append(
                {
                    "code": "short-cut",
                    "message": (
                        f"Keep {keep['start_ms']}-{keep['end_ms']} is under 400ms. "
                        "A cut this short will read as a jump cut on a talking head."
                    ),
                }
            )
    broll = []
    for keep in planned:
        duration = keep["end_ms"] - keep["start_ms"]
        if duration >= 8000:
            broll.append(
                {
                    "program_start_ms": keep["program_start_ms"] + 2000,
                    "program_end_ms": keep["program_end_ms"] - 1000,
                    "note": "Cover this stretch with a diagram or screen capture so the cutaways hide jump cuts.",
                }
            )
    edl = render_edl(planned, fps, title)
    source_end = max((cue["end_ms"] for cue in ordered), default=0)
    return {
        "title": title,
        "fps": fps,
        "max_pause_ms": max_pause_ms,
        "retained_pause_ms": retained_pause_ms,
        "source_duration_ms": source_end,
        "program_duration_ms": program,
        "removed": removed,
        "keeps": [
            {
                "start_ms": keep["start_ms"],
                "end_ms": keep["end_ms"],
                "program_start_ms": keep["program_start_ms"],
                "program_end_ms": keep["program_end_ms"],
                "text": keep["text"],
            }
            for keep in planned
        ],
        "chapters": chapters,
        "broll": broll,
        "warnings": warnings,
        "edl": edl,
    }


def render_edl(keeps: list[dict], fps: int, title: str) -> str:
    lines = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""]
    for index, keep in enumerate(keeps, start=1):
        src_in = frames_to_tc(ms_to_frames(keep["start_ms"], fps), fps)
        src_out = frames_to_tc(ms_to_frames(keep["end_ms"], fps), fps)
        rec_in = frames_to_tc(ms_to_frames(keep["program_start_ms"], fps), fps)
        rec_out = frames_to_tc(ms_to_frames(keep["program_end_ms"], fps), fps)
        lines.append(f"{index:03d}  {'AX':<8} V     C        {src_in} {src_out} {rec_in} {rec_out}")
        lines.append("* FROM CLIP NAME: SOURCE")
    lines.append("")
    return "\n".join(lines)


def format_report(plan: dict) -> str:
    lines = [
        f"{plan['title']}  {plan['fps']} fps",
        f"source {plan['source_duration_ms']} ms  ->  program {plan['program_duration_ms']} ms",
        f"keeps {len(plan['keeps'])}  removed {len(plan['removed'])}  chapters {len(plan['chapters'])}",
        "",
    ]
    for keep in plan["keeps"]:
        lines.append(
            f"  {keep['start_ms']:>7}-{keep['end_ms']:<7}  program {keep['program_start_ms']:>7}-{keep['program_end_ms']:<7}  {keep['text'][:72]}"
        )
    if plan["warnings"]:
        lines.append("")
        for warning in plan["warnings"]:
            lines.append(f"  {warning['code']}: {warning['message']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a talking-head EDL from a transcript.")
    parser.add_argument("transcript", type=Path, help="SRT, VTT, or JSON cues")
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--max-pause-ms", type=int, default=800)
    parser.add_argument("--retained-pause-ms", type=int, default=120)
    parser.add_argument("--title", default="talking-head-cut")
    parser.add_argument("--json", dest="json_out", type=Path)
    parser.add_argument("--edl", dest="edl_out", type=Path)
    args = parser.parse_args(argv)
    try:
        cues, file_fps = load_cues(args.transcript)
        plan = build_plan(
            cues,
            fps=args.fps or file_fps or 30,
            max_pause_ms=args.max_pause_ms,
            retained_pause_ms=args.retained_pause_ms,
            title=args.title,
        )
    except FileNotFoundError:
        print(f"File not found: {args.transcript}", file=sys.stderr)
        return 2
    except (TranscriptError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.json_out:
        args.json_out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    if args.edl_out:
        args.edl_out.write_text(plan["edl"], encoding="utf-8")
    sys.stdout.write(format_report(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
