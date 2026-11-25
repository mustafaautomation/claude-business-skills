---
name: proposal-writer
description: Scores a job post against a freelancer or agency profile and drafts a proposal that uses only proof from that profile. Use when the user pastes an Upwork job, a Fiverr brief, or an agency request and wants a bid, cover letter, pitch, or a fit decision. Flags unpaid tests, equity-only offers, and hype language before a draft is sent.
license: MIT
compatibility: Requires Python 3.11 or newer. No network calls. Scoring and linting use the standard library.
metadata:
  author: Mustafa
  version: "1.0.0"
---

# Proposal writer

Decide the fit, then write. A fluent draft that invents experience is a failed draft.

## Inputs

You need the job post and a profile JSON with `name`, `skills`, and `proof`. Proof is a list of sentences the user is willing to have copied into a bid. If proof is missing, ask for it. Do not mine a memory or a website to fill the gap.

## Steps

1. Run the scorer from this skill directory:

```bash
python scripts/score_job_fit.py --job job.txt --profile profile.json --json fit.json
```

2. Read `band`, `red_flags`, `missing_must_haves`, `budget`, and `recommended_move`. The move is binding. Scoring rules are in [scoring](references/scoring.md).
3. Pick a template from `assets/templates/`: `upwork.md` for a marketplace post, `agency.md` for a longer RFP, `fiverr.md` for a custom offer. When the source is unclear, use the Upwork template.
4. Draft with the headings Hook, Understanding, Approach, Proof, Timeline, Questions. Tone is in [tone rules](references/tone-rules.md).
5. Proof bullets are exact strings from `proof_points_allowed`. If none of them match the job, say the closest one is still the only proof you can show, or tell the user the profile has no relevant proof. Do not write a new bullet.
6. Lint the draft:

```bash
python scripts/lint_proposal.py --proposal draft.md --profile profile.json
```

7. Fix every line the linter prints. Do not send a draft that exits 1.

## How to talk about a weak fit

If the band is `decline` or a red flag is present, the hook carries the boundary. An unpaid sample is refused in the first lines, not in a polite postscript. The project example under `examples/proposal-writer/` is that case: Python and Playwright match, the score is 30 because of an unpaid sample and an urgent flag, and the draft asks for a paid pilot.

Missing must-have tools are named. Do not imply you will learn them overnight unless the user said that and you put it in the approach as a risk.

## Out of scope

Do not submit the proposal to a marketplace. Do not invent a rate below the profile rate to win the job. Do not promise a start date the user did not give you.
