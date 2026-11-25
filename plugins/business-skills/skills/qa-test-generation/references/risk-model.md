# Risk model

The generator is the authority for priority. Do not renumber a test because it "feels" less important. Record a disagreement in a review note.

## Score

`risk_score = impact * likelihood`

Impact and likelihood are integers from 1 to 5.

| Score | Band |
| --- | --- |
| 16-25 | P0 |
| 10-15 | P1 |
| 5-9 | P2 |
| 1-4 | P3 |

## Critical areas

If any area is `payment`, `pricing`, `auth`, `privacy`, or `data-loss`:

- impact 4 or 5 raises the band to at least P0
- impact 1, 2, or 3 raises the band to at least P1

A floor only raises priority. A content change with impact 2 stays P3.

`risk_score` stays the raw product. A pricing story with impact 4 and likelihood 3 keeps score 12 and is still P0 because of the floor. The traceability file shows both numbers so a reviewer can see the bump.

## What gets a test

For each story, in this order:

1. One test per acceptance criterion. Wording is not guessed past the criterion text.
2. String boundaries for `min_length`, one below, `max_length`, one above, and empty when the field is required.
3. Number boundaries at `minimum`, one hundredth below, `maximum`, and one hundredth above.
4. One test per decision-table rule, in file order.
5. One test per state transition. `note: rejected` marks the negative case, where the state stays at `to`.

A criterion is negative only when it contains a whole word or phrase from this list: rejected, expired, invalid, error, unchanged, cannot, must not, fails, denied, not applied. `unexpired` is not `expired`.

## Automation

P0 and P1 cases set `automation_candidate` to true. The Playwright file still marks every test `test.fixme` until a person adds locators. A skeleton must not pretend to pass.

## Coverage

Every acceptance `id` has to appear in `traces`. The script exits 2 if one does not. Boundary, rule, and state tests trace nothing, because they were expanded from fields rather than from a criterion.

## What the script will not add

Pairwise combinations, session-based charters, and production-data privacy checks are not inferred. Put those in a separate note titled `Exploratory, not in the source`. Do not insert them into the `.feature` file or the `.spec.ts` file.
