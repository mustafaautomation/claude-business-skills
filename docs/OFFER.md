# I will build a custom skill for your workflow

Portfolio demo, not client work. The copy below is what Mustafa posts on Fiverr and Upwork. It is not a live checkout, and the sample skills in this repo are not a client delivery.

Mustafa builds the skill, the script that checks the output, and a couple of examples from your real files. You own the folder.

## Upwork

**Title:** I will build a custom skill for your workflow

**Opening**

I build skills that follow a written procedure and then check their own work. A proposal that invents experience, an invoice total that does not add up, or a test suite with no link back to the story is a failed skill, even if the prose sounds confident.

You get a folder you can upload: `SKILL.md` with the name and description filled in, the steps, any template or schema, and a small Python script where a check should be deterministic. I test that script. I do not turn on a paid API in your CI.

Good fits: a repeatable writing or extraction job, a QA workflow, a meeting recap, a cut list from a transcript. A poor fit: anything that needs me to log into your accounts, move money, or decide a legal or tax question.

**Three packages**

| | Starter | Standard | Studio |
| --- | --- | --- | --- |
| Price | $180 | $420 | $780 |
| Skills | 1 | 1 | up to 3 related skills |
| `SKILL.md`, templates, tone or format rules | yes | yes | yes |
| Worked example from your sample | 1 | 2, including a failure | 2 per skill |
| Validation script and schema or checklist | | yes | yes |
| pytest that locks the script | | yes | yes |
| Zip for upload, plus a Claude Code plugin manifest | zip | zip | zip and plugin manifest |
| Revision on the skill text | | | one pass |
| Delivery | 3 days | 5 days | 10 days |

The hourly posts I see for this work sit around $20-48/hr. These are fixed prices for a finished folder, not an open-ended retainer.

**What I need in the first message**

- One real input, with anything confidential removed.
- An example of the output you wish you had, even if it is rough.
- Words, claims, or tools the skill is not allowed to use.
- Where it has to run: claude.ai upload, Claude Code, the API, or all three.

**Screening**

I decline unpaid sample projects, equity-only offers, and briefs that ask me to log into a client account. If the fit is weak I will say so before you hire the Studio package.

## Fiverr gig

**Title:** I will build a custom skill for your workflow

**Gallery line:** A skill folder with a real check behind it. Proposals, invoices, QA, content, meetings, cut lists, or your own repeatable job.

**Description**

Paste the job you do every week. I turn it into a skill: instructions the model can follow, a script that rejects a bad result, and examples taken from a file you send. You can upload the zip, or install the folder in Claude Code.

This gig is how I sell the same kind of pack as the public demo at skills.quvantic.com. The demo is portfolio work. Your gig is written for your files.

### Packages

**Starter — $180 — 3-day delivery**

- One skill
- `SKILL.md` with name, description, and the workflow
- Templates or tone rules where the writing has a shape
- One worked example
- A zip you can upload

**Standard — $420 — 5-day delivery**

- Everything in Starter
- A Python validation script and a schema or checklist
- A happy-path example and a failure example
- A pytest that locks the script so a later edit cannot silently break it
- The upload zip

**Studio — $780 — 10-day delivery**

- Up to three related skills
- Everything in Standard for each of them
- A plugin manifest so `/plugin install` can load the set
- One revision pass on the skill text after you try it

Revisions beyond the Studio pass, extra skills, and a hosted API integration are a new order.

### Buyer requirements

1. A sample input with secrets removed.
2. The output you want, or a short description of the fields and the tone.
3. Anything the skill must refuse to invent.

I start the clock when those three are in the order, not when the order is placed.

## FAQ

**Who owns the files?**
You do. The skill folder is yours to upload, edit, and keep in your repo.

**Do you post, send email, or log into my tools?**
No. The skill drafts. You send.

**Will this call a paid model API from CI?**
Not unless you ask for that and you provide the key. The scripts in the public demo do not call an API. The optional live judge stays skipped when no key is set.

**Does the invoice skill tell me if the tax is legal?**
No. It checks that the line math, the rate arithmetic, and the total agree. Whether the rate is the right one for a place is your accountant's job.

**Does the video skill export a finished video?**
No. It writes an edit decision list and a CMX EDL from a timestamped transcript. Someone still cuts the picture.

**What if my source has no timestamps?**
The cut-list skill stops and asks for them. It does not invent timecodes.

**Can you match our voice?**
Yes, if you send a sample of writing you actually like, and a list of phrases you will not publish. I will not invent proof points that are not in the profile you give me.

**What does code execution mean?**
Skills that run a script need code execution turned on in the product where you use them. The instructions still read without it. The checks do not.

**Is the public repo a client project?**
No. Portfolio demo, not client work. The invoices, the job post, the meeting, and the transcripts are fictional.
