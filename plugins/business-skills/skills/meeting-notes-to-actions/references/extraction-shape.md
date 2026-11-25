# Extraction shape

The normalizer does not read a transcript. You read the transcript and write this JSON. Then the script resolves dates, merges duplicates, and refuses a silent missing owner.

```json
{
  "title": "Q2 launch standup",
  "meeting_date": "2026-04-07",
  "decisions": ["Ship the billing page behind a flag"],
  "actions": [
    {"text": "Write the Playwright smoke for checkout", "owner": "Mustafa", "due": "2026-04-11"}
  ],
  "open_questions": ["Do we invoice the pilot before the flag is on?"]
}
```

## How to extract

- A decision is something the room agreed. A suggestion is not a decision. If they did not agree, it is an open question or it is omitted.
- An action needs a verb. "Playwright" is not an action. "Write the Playwright smoke for checkout" is.
- Copy names as they were said. Do not assign the person who talked the most.
- If nobody was named, set `owner` to an empty string. The script will mark `unassigned` and add `missing-owner`. Do not pick someone to make the list look finished.
- Prefer an explicit `YYYY-MM-DD` when the notes contain one. Also pass relative words through when that is all they said: `today`, `tomorrow`, or a weekday name. The script resolves those against `meeting_date`. Weekdays land on that weekday, on the meeting date if it matches, otherwise the next one.
- If the same action is said twice with two dates, keep both rows and let the script merge them. An explicit date wins over "Friday". The merged row carries `relative-date-ignored` so the conflict stays visible.
- An unreadable date stays in `due` as the original words only if you are unsure it is a date at all. Prefer the words they used. The script flags `unparsed-date` rather than guessing.

## Output

Actions are sorted by due date, undated last, then by text. Ids are `A-1` upward after that sort. The email is a follow-up, not minutes. It repeats decisions, actions, and open questions, and it marks a missing owner in the action line.
