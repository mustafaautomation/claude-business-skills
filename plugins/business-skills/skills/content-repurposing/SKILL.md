---
name: content-repurposing
description: Repurposes a long-form article or transcript into a LinkedIn post, an X thread, a newsletter, and a short video script, then checks length and structure. Use when the user pastes a transcript, blog, talk, or interview and asks for social posts, a newsletter, or a short-form script.
license: MIT
compatibility: Requires Python 3.11 or newer. No network calls. The checker validates JSON. It does not publish anywhere.
metadata:
  author: Mustafa
  version: "1.0.0"
---

# Content repurposing

One argument, four shapes. Do not paste the transcript four times with the intros chopped off.

## Steps

1. Read the source once and write the single claim a stranger could repeat. If you cannot, tell the user the source is still notes.
2. Draft a JSON pack. Field limits and the anti-paste rules are in [channel rules](references/channel-rules.md). Every sentence has to be supported by the source. Do not add a metric, a client, or a punchline that was not there.
3. Run the checker from this skill directory:

```bash
python scripts/check_pack.py pack.json
```

4. If the report says FAIL, change the pack and run it again. Show the failing check names if the user wants to see why a line was cut.
5. When it passes, present the four pieces as readable text as well as the JSON. The JSON is the contract. The readable text is what they will paste.

A source transcript and a pack that already passes are in `examples/content-repurposing/`.

## Voice

Match the source. A dry teardown stays dry. Do not add exclamation points, a fake personal story, or a "let that sink in" line. Hashtags are few and literal.

## Out of scope

Do not post, schedule, or thread-reply on an account. Do not generate images. The short video section is a script with on-screen text, not an edit.
