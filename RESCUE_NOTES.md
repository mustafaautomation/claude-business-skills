# Rescued from Cursor

Source: claude-business-skills | Cursor https://cursor.com/agents/bc-9e7b68d9-6895-5a40-9082-3528f1eae1cc
Scope: All Commits
Captured: 2026-11-25T11:35:39.449Z
Files written: 89

Not in this copy: files Cursor's template created and the agent never changed (e.g. tsconfig, shadcn ui components, lockfiles, public assets) when scope is 'Last Agent Turn'; binaries.

- binary not recoverable from diff view: dist/content-repurposing.zip
- binary not recoverable from diff view: dist/invoice-extraction.zip
- binary not recoverable from diff view: dist/meeting-notes-to-actions.zip
- binary not recoverable from diff view: dist/proposal-writer.zip
- binary not recoverable from diff view: dist/qa-test-generation.zip
- binary not recoverable from diff view: dist/talking-head-edit-plan.zip
- binary not recoverable from diff view: docs/invoice-extraction.gif
- binary not recoverable from diff view: docs/qa-test-generation.gif
- binary not recoverable from diff view: docs/talking-head-edit-plan.gif
- binary not recoverable from diff view: examples/invoice-extraction/northwind.pdf
- binary not recoverable from diff view: site/downloads/content-repurposing.zip
- binary not recoverable from diff view: site/downloads/invoice-extraction.zip
- binary not recoverable from diff view: site/downloads/meeting-notes-to-actions.zip
- binary not recoverable from diff view: site/downloads/proposal-writer.zip
- binary not recoverable from diff view: site/downloads/qa-test-generation.zip
- binary not recoverable from diff view: site/downloads/talking-head-edit-plan.zip
- binary not recoverable from diff view: site/invoice-extraction.gif
- binary not recoverable from diff view: site/qa-test-generation.gif
- binary not recoverable from diff view: site/talking-head-edit-plan.gif

## Repair log (2026-11-25, Claude)

- Regenerated all six skill zips with the repo's own packager (fixed timestamps, reproducible): `python3 scripts/package_skills.py` -> `dist/*.zip`, and `--dist site/downloads` -> `site/downloads/*.zip` (byte-identical copies).
- `evals/test_invoice.py`: `test_pdf_round_trip_matches_the_text_invoice` now skips when `examples/invoice-extraction/northwind.pdf` is absent, instead of failing with FileNotFoundError. The PDF was not recreated (it would be a fabricated sample). Restore the original file and the test runs again.
- `.gitignore`: added `.env*` (keeps `.env.example`).
- Verified (Python 3.11 venv, requirements.txt): `python -m pytest` -> 19 passed, 2 skipped (missing PDF; live LLM judge without ANTHROPIC_API_KEY). Original agent reported 20 passed, 1 skipped; the difference is the PDF test. `scripts/demo_invoice.py`, `demo_qa.py`, `demo_edl.py` all run.
- Still missing (binaries): `examples/invoice-extraction/northwind.pdf`; the three demo GIFs (`docs/*.gif` and `site/*.gif`), which README and `site/index.html` (including og:image) still reference.
  The GIFs can be re-recorded with `vhs docs/<name>.tape` from the repo root (tapes use relative paths only), then copied to `site/`. Not done here because the tapes ask for the "DejaVu Sans Mono" font, which is not installed on this Mac, and vhs would silently fall back to a proportional font.

## Sample PDF restored (2026-11-25, Claude)

- `examples/invoice-extraction/northwind.pdf` is now generated from `northwind.txt` by the new `scripts/make_sample_pdf.py` (also `make sample-pdf`), which calls the skill's own `render_text_pdf()` (stdlib only, uncompressed, byte-for-byte deterministic; `--check` flags a stale file). Same fictional Northwind invoice as the text fixture.
- `evals/test_invoice.py`: the PDF round-trip test is no longer skipped; added a test that the committed PDF equals a fresh render of `northwind.txt`.
- Verified: `python -m pytest` -> 21 passed, 1 skipped (live LLM judge, no ANTHROPIC_API_KEY). Skill zips unchanged (examples are not packaged).
