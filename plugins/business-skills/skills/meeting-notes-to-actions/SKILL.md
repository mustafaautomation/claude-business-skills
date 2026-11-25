---
name: meeting-notes-to-actions
description: Turns meeting notes or a transcript into decisions, owners, due dates, open questions, and a follow-up note. Use when the user pastes notes, a transcript, or a recap and asks for action items, owners, deadlines, or an email to send after the meeting. Missing owners stay missing instead of being guessed.
license: MIT
compatibility: Requires Python 3.11 or newer. No network calls. The script normalizes extracted JSON. It does not summarize a transcript by itself.
metadata:
  author: Mustafa
  version: "1.0.0"
---

# Meeting notes to actions

Separate what was decided, what someone has to do, and what is still a question. Then let the script check the list.

## Steps

1. Read the notes. Extract JSON in the shape from [extraction shape](references/extraction-shape.md). Do not promote a suggestion to a decision. Do not invent an owner.
2. Run the normalizer from this skill directory:

```bash
python scripts/normalize_actions.py extracted.json --json normalized.json --markdown summary.md --email follow-up.txt
```

3. Read the issues on each action before you show the email.
   - `missing-owner` means you ask who owns it. You do not fill the name in the email.
   - `relative-date-ignored` means an explicit date beat a weekday. Mention both dates in one sentence so the room can correct you.
   - `date-conflict` means two explicit dates disagreed. The earlier one was kept. Say that.
   - `unparsed-date` means the due text was not a date the script understands. Quote it.
4. Give the user the email and the markdown. The email is the thing they can send. The markdown is the record.

The project example `examples/meeting-notes-to-actions/` has a short transcript, the extraction, and the normalized list: the checkout smoke stays with Mustafa on 2026-04-11, and the recap stays unassigned.

## Out of scope

Do not send the email. Do not create calendar events. Do not assign work to someone who was only in the room.
