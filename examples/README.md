# Examples

Sample inputs and the outputs the scripts actually produce. The invoices, job post, meeting, and transcripts are fictional.

Portfolio demo, not client work.

| Skill | Input | Expected output |
| --- | --- | --- |
| `proposal-writer` | `job-post.txt`, `profile.json` | `expected-fit.json`, `expected-proposal.md` |
| `invoice-extraction` | `northwind.txt`, `northwind.pdf`, `northwind-bad-tax.txt` | `expected.json`, `expected.csv` |
| `qa-test-generation` | `checkout.json` | `checkout.cases.json`, `checkout.feature`, `checkout.spec.ts`, `checkout.traceability.md` |
| `content-repurposing` | `transcript.md`, `pack.json` | `pack.json` passes `check_pack.py` |
| `meeting-notes-to-actions` | `transcript.md`, `extracted.json` | `expected.json`, `expected.md`, `expected-email.txt` |
| `talking-head-edit-plan` | `short.srt`, `walkthrough.srt` | `short.edl`, `short.json`, `walkthrough.edl`, `walkthrough.json` |

The meeting transcript is the messy source. The script reads `extracted.json`, which is the structured extraction a model is supposed to write before normalization. It does not summarize prose by itself.

Regenerate the QA files with:

```bash
python plugins/business-skills/skills/qa-test-generation/scripts/generate_tests.py \
  examples/qa-test-generation/checkout.json \
  --out-dir examples/qa-test-generation \
  --stem checkout
```
