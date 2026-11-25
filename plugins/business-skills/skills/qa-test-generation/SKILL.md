---
name: qa-test-generation
description: Turns requirements and user stories into a risk-prioritized test set with test cases, Gherkin, a traceability matrix, and Playwright skeletons. Use when the user shares acceptance criteria, a user story, a PRD excerpt, or asks for test cases, BDD scenarios, regression coverage, or automation scaffolding. Payment, pricing, auth, privacy, and data-loss paths are raised ahead of copy changes.
license: MIT
compatibility: Requires Python 3.11 or newer. No network calls. Playwright skeletons are text only and are not executed by the script.
metadata:
  author: Mustafa
  version: "1.0.0"
---

# QA test generation

Produce a suite a reviewer can trace back to a story. The script decides priority, ids, and coverage. You decide whether the requirements JSON is a fair reading of what the user wrote.

## Do this first

Map the source into the JSON shape in [requirements shape](references/requirements-shape.md). Keep acceptance text close to the source. If a sentence is ambiguous, ask before you turn it into a criterion. Missing risk numbers are a question, not a default of 5.

Then run, from this skill directory:

```bash
python scripts/generate_tests.py requirements.json --out-dir ./out --stem checkout
```

That writes `checkout.cases.json`, `checkout.feature`, `checkout.spec.ts`, and `checkout.traceability.md`. Exit 2 means a story is malformed or an acceptance id has no test. Do not hand-write a replacement file to hide that.

The project example `examples/qa-test-generation/checkout.json` is the reference run: promo codes at P0, a shipping table that scores 12 and is still P0 because it is pricing, and a delivery-copy story that stays P3.

## Read the result before you talk about it

1. Say the counts by priority. A suite that is all P0 is a signal the impact scores were lazy. Say so.
2. Point at the highest band and name the area that put it there: raw score, or the critical-area floor. The floor rules are in [risk model](references/risk-model.md).
3. Confirm every acceptance id is in the matrix. The script already exits 2 when one is missing. Look anyway if you edited the JSON after the run.
4. Do not delete a boundary or a decision-table row because it looks repetitive. Two rows that share an outcome can still protect different conditions.

## What you may add

After the files, you may write a short section titled `Exploratory, not in the source`. Use it for charters the script does not infer: double-submit, pairwise gaps, permission changes that were never written as acceptance. Rules of thumb are in [techniques](references/techniques.md). Those charters do not get fake `AC-` ids and they do not go inside the generated feature file.

## Playwright

The spec is a skeleton. Every test is `test.fixme` so it cannot go green by accident. Conventions for filling one in are in [Playwright](references/playwright.md). Do not tell the user the skeletons passed.

## Review habits

- Quote the test id when you talk about a case.
- Keep the Given line tied to the persona and the want. Do not upgrade a shopper into an admin.
- Negative detection is literal. `unexpired` is not a failure. `rejected` and `unchanged` are. If that classification is wrong for a sentence, change the sentence with the user, then rerun. Do not patch the feature file by hand and leave the JSON behind.
- P3 work is still listed. It is scheduled last, not dropped.

## Out of scope

This skill does not execute Playwright, does not open a browser, and does not declare a release ready. It prepares the list. A green pipeline is a separate job.
