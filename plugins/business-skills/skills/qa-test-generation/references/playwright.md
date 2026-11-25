# Playwright conventions

The generator writes TypeScript skeletons. They are `test.fixme` on purpose. A fixme test is visible and does not paint a false green.

## Shape

- Import `test` and `expect` from `@playwright/test`.
- One `test.describe` for the feature.
- The title starts with the priority, then the test id, then a short name, then `@p0` and `@US-14` style tags.
- Comments carry technique, type, traces, and risk score.
- Navigation uses the feature slug, such as `/checkout`.
- The placeholder assertion is `getByTestId("result")`. Replace it. Do not leave it and remove `test.fixme`.

## When you fill a skeleton in

- Prefer `getByRole`, `getByLabel`, and `getByTestId` over CSS that depends on layout.
- Do not add `page.waitForTimeout`.
- Keep the test id in the title so the traceability table still matches.
- One skeleton becomes one test. Do not merge a boundary test into the happy path to "save time".
- Data that moves money uses a known fixture amount written in the test, not whatever the environment happens to have in the cart.

## Priority order

The file is sorted P0, then P1, then P2, then P3, and within a band by story id and test id. When you implement, start at the top. A P3 copy test does not jump the queue because it is easy.

## Not in this file

Exploratory charters stay in the review note. A `.fixme` test that nobody intends to automate should stay a charter instead of a permanent skip. Say which, in the note.
