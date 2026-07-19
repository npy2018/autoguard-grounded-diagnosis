from autoguard_agent.agent import GroundedDiagnosisAgent
from autoguard_agent.demo import run
from autoguard_agent.store import EvidenceStore
from autoguard_agent.tools import ToolRegistry


def test_demo_claims_have_evidence_uris() -> None:
    result = run()
    hypothesis = result["hypotheses"][0]
    assert result["grounded"] is True
    assert len(hypothesis["support"]) >= 2
    assert all("://" in item["uri"] for item in hypothesis["support"])


def test_missing_evidence_forces_insufficient_status() -> None:
    report = GroundedDiagnosisAgent(ToolRegistry(EvidenceStore())).diagnose("missing", "missing")
    assert report.grounded is False
    assert report.hypotheses[0].status == "insufficient_evidence"
    assert len(report.tool_trace) <= 6
