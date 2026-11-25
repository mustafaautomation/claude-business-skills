# Contributing

Portfolio demo, not client work. Issues and small fixes are welcome. A change should keep a skill honest: the script checks the result, and the instructions do not invent facts the user did not supply.

## Setup

Python 3.11 or newer.

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest
```

CI runs that same pytest and rebuilds the zips. Do not add a step that calls a paid model API. `evals/test_llm_judge.py` already skips when `ANTHROPIC_API_KEY` is unset, and the workflow must keep leaving it unset.

## Adding or editing a skill

1. Put the folder in `plugins/business-skills/skills/<name>/`.
2. `name` in `SKILL.md` matches the folder. Lowercase, hyphens, no reserved words, description under 1024 characters, and the file under 500 lines.
3. Keep `SKILL.md` as the procedure. Put tables and templates in `references/` or `assets/`.
4. If a check can be deterministic, put it in `scripts/` and use only the Python standard library. The API container cannot install packages.
5. Add an input and the expected output under `examples/<name>/`.
6. Lock that output with a test in `evals/`.
7. Rebuild zips with `python3 scripts/package_skills.py`.

Do not claim a client, a metric, or a tool that is not in the fixture. Sample invoices, job posts, meetings, and transcripts stay fictional.

## Marketplace

The plugin id is `business-skills@quvantic-skills`. After you change a skill, the marketplace entry in `.claude-plugin/marketplace.json` still points at `./plugins/business-skills`.

## License

MIT. See [LICENSE](LICENSE).
