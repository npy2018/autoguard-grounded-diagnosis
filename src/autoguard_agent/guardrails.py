from __future__ import annotations

from .schemas import Hypothesis


ALLOWED_SCHEMES = ("log://", "video://", "version://", "replay://", "case://")


def validate_hypothesis(hypothesis: Hypothesis) -> None:
    if hypothesis.status != "insufficient_evidence" and len(hypothesis.support) < 2:
        raise ValueError("a grounded hypothesis needs at least two evidence references")
    for evidence in hypothesis.support + hypothesis.counter_evidence:
        if not evidence.uri.startswith(ALLOWED_SCHEMES):
            raise ValueError(f"unresolvable evidence URI: {evidence.uri}")
