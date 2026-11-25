# Changelog

## 1.0.0 — 2026-11-25

First public sample of the business skill pack. Portfolio demo, not client work.

- Six skills: proposals, invoices, QA test generation, content repurposing, meeting notes, and a talking-head edit plan.
- Each skill ships `SKILL.md`, references, and a standard-library script that checks the result.
- Worked examples and expected outputs under `examples/`.
- Pytest covers skill shape, money math, risk bands, the EDL, content length, meeting dates, proposal lint, and the zip layout. The live model judge stays skipped without an API key.
- One upload zip per skill in `dist/`.
- Claude Code marketplace manifest for `business-skills@quvantic-skills`.
- Static landing page in `site/`, with terminal recordings for invoices, QA, and the cut list.
- Fiverr and Upwork copy in `docs/OFFER.md`.
