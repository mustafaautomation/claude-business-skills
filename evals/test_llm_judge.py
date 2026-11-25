"""Optional live judge. CI has no key, so this test is skipped there."""

from __future__ import annotations

import json
import os
import urllib.request

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set; live judge skipped",
)


def test_live_judge_accepts_a_scoped_proposal_outline():
    model = os.environ.get("ANTHROPIC_EVAL_MODEL", "claude-haiku-4-5")
    draft = (
        "Hook: paid pilot on one transcript, no free sample.\n"
        "Understanding: the post wants an EDL.\n"
        "Approach: one short file first.\n"
        "Proof: only the two profile lines.\n"
        "Timeline: first deliverable is the EDL.\n"
        "Questions: frame rate, and whether a short pilot is acceptable.\n"
    )
    body = {
        "model": model,
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Reply with JSON {\"pass\": true or false, \"reason\": \"...\"}. "
                    "pass is true only if the draft refuses unpaid work and names a first deliverable.\n\n"
                    + draft
                ),
            }
        ],
    }
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    text = "".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text")
    start = text.find("{")
    end = text.rfind("}")
    verdict = json.loads(text[start : end + 1])
    assert verdict["pass"] is True
