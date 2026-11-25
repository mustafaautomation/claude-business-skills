# Techniques the generator applies

Use these names in review notes so a later reader can see why a test exists.

## Acceptance

One scenario per written criterion. The Then step for a positive criterion is the story outcome. The Then step for a negative criterion is a refusal that leaves protected totals unchanged. Sharpen that sentence in the exploratory note if the product has a specific message. Do not delete the generated scenario while you do it.

## Boundary values

Strings use length. Numbers use the declared minimum and maximum, plus one hundredth outside the range. Values outside the range are negative tests. The point of the hundredth is to show the comparison is exclusive of the invalid side, not to invent a currency rounding rule. Money rounding belongs to the story text if it matters.

## Decision table

Each `rules` entry is one column: the `when` object is the condition, `then` is the expected result. Set `"type": "negative"` on a rule when the outcome is a rejection. Otherwise the test is positive. Do not collapse two rows because they share an outcome. US shipping at 74.99 and CA shipping at 75.00 can both say "standard shipping" and still be different tests.

## State transition

Each transition is a test. `from`, `event`, and `to` are copied. A rejected transition says the event is refused and the state stays at `to`. The model is not a full statechart: there is no guard language and no nested states. If the story needs those, say so in the exploratory note and keep the generated transitions.

## What to add by hand

Add an exploratory charter when:

- three or more independent fields exist and nobody wrote a decision table
- the story mentions a permission change, a retry, or a double submit and the acceptance lines do not
- the risk area is payment or auth and the acceptance lines only describe the happy path

Write the charter as a short mission, not as a fake acceptance id. Example: "Charter: apply, remove, and re-apply the same code. Look for a total that drifts by one cent."

## Playwright skeletons

See [playwright conventions](playwright.md). The generated file is a list of intentions. It is not a suite you run in CI.
