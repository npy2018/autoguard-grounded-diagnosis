from __future__ import annotations

import json
from pathlib import Path

from .agent import GroundedDiagnosisAgent
from .store import EvidenceStore
from .tools import ToolRegistry


def run(output: Path | None = None) -> dict[str, object]:
    agent = GroundedDiagnosisAgent(ToolRegistry(EvidenceStore.demo()))
    result = agent.diagnose("EVT-001", "V2.7.0").model_dump(mode="json")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
