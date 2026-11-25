"""Skill folders match the Agent Skills spec and stay small enough to upload."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import yaml

from conftest import SKILLS

EXPECTED = {
    "proposal-writer",
    "invoice-extraction",
    "qa-test-generation",
    "content-repurposing",
    "meeting-notes-to-actions",
    "talking-head-edit-plan",
}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED = ("anthropic", "claude")
MAX_LINES = 500
MAX_BYTES = 30 * 1024 * 1024


def _skills():
    found = sorted(path for path in SKILLS.iterdir() if (path / "SKILL.md").is_file())
    assert {path.name for path in found} == EXPECTED
    return found


def _frontmatter(text: str) -> dict:
    assert text.startswith("---\n")
    end = text.find("\n---\n", 4)
    assert end != -1
    data = yaml.safe_load(text[4:end])
    assert isinstance(data, dict)
    return data


def test_skill_set_is_complete():
    assert len(list(_skills())) == 6


def test_frontmatter_and_size():
    for skill in _skills():
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        meta = _frontmatter(text)
        body = text.split("\n---\n", 1)[1].strip()
        assert body, skill.name
        assert meta["name"] == skill.name
        assert NAME_RE.fullmatch(meta["name"])
        assert 1 <= len(meta["name"]) <= 64
        assert not meta["name"].startswith("-") and not meta["name"].endswith("-")
        assert "--" not in meta["name"]
        lowered = meta["name"]
        for word in RESERVED:
            assert word not in lowered
        description = meta["description"]
        assert isinstance(description, str)
        assert 1 <= len(description) <= 1024
        assert "<" not in description and ">" not in description
        assert not description.startswith(("I ", "You ", "I'll "))
        assert "Use when" in description
        assert len(text.splitlines()) <= MAX_LINES
        if "compatibility" in meta:
            assert 1 <= len(meta["compatibility"]) <= 500
        if "metadata" in meta:
            assert isinstance(meta["metadata"], dict)
            for value in meta["metadata"].values():
                assert isinstance(value, str)
        size = sum(path.stat().st_size for path in skill.rglob("*") if path.is_file())
        assert size < MAX_BYTES
        assert (skill / "scripts").is_dir()
        assert (skill / "references").is_dir()


def test_skill_scripts_do_not_import_network_modules():
    banned = {"urllib", "requests", "httpx", "socket", "ftplib", "smtplib"}
    for skill in _skills():
        for script in (skill / "scripts").rglob("*.py"):
            tree = ast.parse(script.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".")[0]]
                else:
                    continue
                assert not (set(names) & banned), f"{script} imports {names}"


def test_marketplace_points_at_the_plugin():
    root = SKILLS.parents[2]
    market = yaml.safe_load((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert market["name"] == "quvantic-skills"
    assert market["owner"]["name"]
    plugin = market["plugins"][0]
    assert plugin["name"] == "business-skills"
    assert plugin["source"] == "./plugins/business-skills"
    manifest_path = root / "plugins" / "business-skills" / ".claude-plugin" / "plugin.json"
    import json

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["name"] == "business-skills"
    assert "claude" not in manifest["name"]
    assert (root / "plugins" / "business-skills" / "skills").is_dir()
