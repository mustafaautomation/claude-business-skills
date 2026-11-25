# claude-business-skills

**Portfolio demo, not client work.** The invoices, job post, meeting, and transcripts in `examples/` are fictional. Mustafa ([mustafaautomation](https://github.com/mustafaautomation)) built this as a public sample. The page for it is [skills.quvantic.com](https://skills.quvantic.com).

![Invoice extraction on a valid bill and a bill whose tax does not add up](docs/invoice-extraction.gif)

Six skills for the work freelancers and small teams actually bill. Each folder follows the [Agent Skills](https://agentskills.io/specification) layout: `SKILL.md` with `name` and `description`, plus `scripts/`, `references/`, and `assets/` where they earn their place. The same zip uploads to claude.ai, installs in Claude Code, and uploads through the Skills API. The scripts use the Python standard library so they still run where you cannot `pip install`.

The QA skill is the one to read first. It scores impact and likelihood, raises payment, pricing, auth, privacy, and data-loss above copy changes, and writes Gherkin plus Playwright skeletons that stay `test.fixme` until a person fills the locators.

![QA generator: 19 P0 tests, one P3, and a pricing story held at P0](docs/qa-test-generation.gif)

![Talking-head EDL after a filler cue and the dead air around it are removed](docs/talking-head-edit-plan.gif)

## Skills

| Skill | Use it for | What the script locks |
| --- | --- | --- |
| `proposal-writer` | An Upwork, Fiverr, or agency bid from a job post and a profile | Fit score, red flags, and a draft that can only quote proof from the profile |
| `invoice-extraction` | Invoice text, PDF, or a transcription of a photo | Line math, tax arithmetic, totals, JSON, and CSV |
| `qa-test-generation` | User stories and acceptance criteria | Priority, traceability, Gherkin, Playwright skeletons |
| `content-repurposing` | A transcript or article turned into a LinkedIn post, an X thread, a newsletter, and a short script | Length and structure for each channel |
| `meeting-notes-to-actions` | Notes or a transcript turned into owners, dates, and a follow-up | Dates, duplicate actions, missing owners |
| `talking-head-edit-plan` | An SRT, VTT, or timed transcript turned into a cut list | Filler cuts, dead air, a CMX 3600 EDL, jump-cut warnings |

Worked inputs and the files the scripts emit are in [`examples/`](examples/README.md).

## Install

Skills do not sync between products. Upload or install once per surface. Code execution has to be on wherever a script should run.

### claude.ai

1. Take a zip from [`dist/`](dist/) or build them with `python3 scripts/package_skills.py`. The landing page also links the same six files under `downloads/`.
2. Open Settings, then Capabilities, then Skills, and upload the zip.
3. Each zip has one top-level folder and a `SKILL.md` inside it.

### Claude Code

```bash
claude plugin marketplace add mustafaautomation/claude-business-skills
claude plugin install business-skills@quvantic-skills
```

Inside a session the same lines start with `/plugin`. From a local checkout of this folder, `claude plugin marketplace add .` points at the copy you have open. The manifest is [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). The plugin is [`plugins/business-skills`](plugins/business-skills/.claude-plugin/plugin.json).

You can also copy a single skill folder into `~/.claude/skills/` or `.claude/skills/`.

### API

Upload `dist/<skill>.zip` with `POST /v1/skills`. The archive root is the skill folder, and `SKILL.md` sits at the top of that folder. The response gives you a `skill_…` id.

Use it on a Messages request by listing the skill in `container.skills` with `"type": "custom"` and including the code execution tool. The container has no network access and cannot install packages at runtime. Pin `version` to the version id you just uploaded when you do not want a later upload to change production.

## FAQ

**Do skills sync between claude.ai, Claude Code, and the API?**
No. Upload or install on each surface.

**Why does the script not run?**
Code execution is off, or the file you passed is a photo. The invoice skill does not OCR. Transcribe the image, then validate the text.

**Is a failing invoice a tax ruling?**
No. The script checks that line math, the stated rate, and the total agree within a cent. Whether the rate is the right one for a place is an accountant's question.

**Does the video skill export a finished cut?**
No. It writes a cut list and a CMX 3600 EDL. If the transcript has no timestamps, it stops. It does not invent them.

**Will CI call a paid model?**
No. `evals/test_llm_judge.py` skips unless `ANTHROPIC_API_KEY` is set, and the workflow does not set it.

**Is this a client project?**
No. Portfolio demo, not client work.

## Run the demos and the tests

Python 3.11 or newer.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/demo_invoice.py
python3 scripts/demo_qa.py
python3 scripts/demo_edl.py
python3 -m pytest
```

`pytest` checks frontmatter and size limits, then runs the scripts against `examples/`. Without an API key you should see the live judge skipped and everything else passing. The workflow is [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

Rebuild a GIF from its tape if you have [vhs](https://github.com/charmbracelet/vhs), ffmpeg, and ttyd:

```bash
vhs docs/invoice-extraction.tape
vhs docs/qa-test-generation.tape
vhs docs/talking-head-edit-plan.tape
```

## Layout

```
plugins/business-skills/skills/   the six skill folders
examples/                         inputs and expected outputs
evals/                            pytest, including the skipped live judge
dist/                             one zip per skill
docs/*.gif                        terminal recordings
docs/OFFER.md                     Fiverr and Upwork copy
site/                             static page, including downloads/
```

## Deploy the landing page

`site/` is static HTML, CSS, the three GIFs, and `downloads/*.zip`. No build step. Paths are relative, so the folder can be uploaded as-is.

1. Upload the contents of `site/` (or the assembled `site-deploy` folder) as a static project.
2. Leave the framework as Other. No build command.
3. Attach `skills.quvantic.com`. The DNS record is usually a CNAME from `skills` to `cname.vercel-dns.com`. Vercel shows the exact target.
4. `site/vercel.json` turns on clean URLs, so `/offer` serves the gig page.

## Offer

Paste-ready Fiverr and Upwork copy, with Starter ($180), Standard ($420), and Studio ($780), is in [`docs/OFFER.md`](docs/OFFER.md).

## License

MIT. See [LICENSE](LICENSE). Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md). History is in [CHANGELOG.md](CHANGELOG.md).
