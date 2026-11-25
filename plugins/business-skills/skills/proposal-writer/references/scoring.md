# Fit score

Start at 40.

- Add 10 for each profile skill that appears in the post, up to 40. Skills of three letters or fewer match as whole words. Longer skills match as a phrase, case insensitive.
- Subtract 15 for each known tool that sits in a "must have" or "must be" sentence and is not on the profile.
- Subtract 20 for an unpaid or free sample, test, trial, or edit.
- Subtract 25 for equity-only.
- Subtract 5 for rockstar, ninja, or guru.
- Subtract 10 for urgent, asap, or yesterday.

Clamp the result to 0-100.

| Score | Band |
| --- | --- |
| 75-100 | recommend |
| 55-74 | conditional |
| 0-54 | decline |

Known tools the must-have scan recognizes: python, playwright, selenium, cypress, pytest, postman, jira, sql, typescript, appium, k6, premiere, davinci, ffmpeg.

Budget parsing reads `$30-45/hr`, `$45/hr`, and `$500 fixed`. If none of those appear, budget is null. Do not invent a number from "competitive" or "DOE".

The script's recommended move is the move the draft has to follow. An unpaid sample always produces "Ask for a paid pilot. Do not start with an unpaid sample." even when the numeric score would have been higher.
