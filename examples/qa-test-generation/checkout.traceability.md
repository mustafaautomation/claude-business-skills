# Traceability — Checkout

Generated from the requirements file. Do not delete a row because it feels redundant; mark it out of scope in a review note instead.

| Test | Story | Priority | Technique | Type | Traces | Automated skeleton | Title |
| --- | --- | --- | --- | --- | --- | --- | --- |
| US-14-TC-001 | US-14 | P0 | acceptance | positive | AC-1 | yes | A valid unexpired code reduces the order total by the code amount |
| US-14-TC-002 | US-14 | P0 | acceptance | negative | AC-2 | yes | An expired code is rejected and the total stays unchanged |
| US-14-TC-003 | US-14 | P0 | acceptance | negative | AC-3 | yes | A second code is rejected while one code is already applied |
| US-14-TC-004 | US-14 | P0 | boundary | positive | — | yes | promo_code length 4 is accepted |
| US-14-TC-005 | US-14 | P0 | boundary | negative | — | yes | promo_code length 3 is rejected |
| US-14-TC-006 | US-14 | P0 | boundary | positive | — | yes | promo_code length 12 is accepted |
| US-14-TC-007 | US-14 | P0 | boundary | negative | — | yes | promo_code length 13 is rejected |
| US-14-TC-008 | US-14 | P0 | boundary | negative | — | yes | promo_code is empty and is rejected |
| US-14-TC-009 | US-14 | P0 | state-transition | positive | — | yes | promo: empty --apply_valid--> applied |
| US-14-TC-010 | US-14 | P0 | state-transition | negative | — | yes | promo: applied --apply_second--> applied |
| US-14-TC-011 | US-14 | P0 | state-transition | positive | — | yes | promo: applied --remove--> empty |
| US-30-TC-001 | US-30 | P0 | acceptance | positive | AC-4 | yes | Carts at or above 75.00 in the US show free shipping |
| US-30-TC-002 | US-30 | P0 | boundary | positive | — | yes | cart_total at minimum 0 is accepted |
| US-30-TC-003 | US-30 | P0 | boundary | negative | — | yes | cart_total below minimum (-0.01) is rejected |
| US-30-TC-004 | US-30 | P0 | boundary | positive | — | yes | cart_total at maximum 10000 is accepted |
| US-30-TC-005 | US-30 | P0 | boundary | negative | — | yes | cart_total above maximum (10000.01) is rejected |
| US-30-TC-006 | US-30 | P0 | decision-table | positive | — | yes | rule country=US cart_total=74.99 -> standard shipping |
| US-30-TC-007 | US-30 | P0 | decision-table | positive | — | yes | rule country=US cart_total=75.00 -> free shipping |
| US-30-TC-008 | US-30 | P0 | decision-table | positive | — | yes | rule country=CA cart_total=75.00 -> standard shipping |
| US-3-TC-001 | US-3 | P3 | acceptance | positive | AC-5 | later | A dated estimate is visible before the pay button |
