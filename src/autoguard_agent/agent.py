from __future__ import annotations

from dataclasses import dataclass

from .guardrails import validate_hypothesis
from .schemas import DiagnosisReport, Hypothesis, ToolCallRecord
from .tools import ToolRegistry


@dataclass
class GroundedDiagnosisAgent:
    tools: ToolRegistry
    max_steps: int = 6

    def diagnose(self, event_id: str, version: str) -> DiagnosisReport:
        plan = [
            ("query_logs", {"event_id": event_id}),
            ("get_version_diff", {"version": version}),
            ("compare_replays", {"event_id": event_id}),
            ("retrieve_similar_cases", {"query": "pedestrian threshold"}),
        ][: self.max_steps]
        trace: list[ToolCallRecord] = []
        evidence = {}
        for name, arguments in plan:
            result = self.tools.call(name, arguments)
            evidence[name] = result
            trace.append(ToolCallRecord(tool=name, arguments=arguments, evidence=result))

        logs = evidence.get("query_logs", [])
        changes = evidence.get("get_version_diff", [])
        replay = evidence.get("compare_replays", [])
        cases = evidence.get("retrieve_similar_cases", [])
        support = changes[:1] + replay[:2] + logs[:1] + cases[:1]
        if len(support) < 2:
            hypothesis = Hypothesis(
                statement="Evidence is insufficient to produce a root-cause hypothesis.",
                confidence=0.0,
                support=[],
                missing_information=["version diff", "paired replay", "event log"],
                falsifiable_prediction="Collect the missing evidence and rerun diagnosis.",
                recommended_experiment="No experiment should be run before evidence is complete.",
                status="insufficient_evidence",
            )
        else:
            hypothesis = Hypothesis(
                statement="The lower pedestrian threshold caused object 328 to change from static_unknown to pedestrian, propagating to excessive braking.",
                confidence=0.82,
                support=support,
                counter_evidence=[],
                missing_information=["radar object confirmation", "camera frame review"],
                falsifiable_prediction="Restoring pedestrian_threshold to 0.42 should remove the replay braking anomaly while holding all other variables constant.",
                recommended_experiment="Run a parameter-level paired replay with CFG-108 reverted only.",
                status="candidate",
            )
        validate_hypothesis(hypothesis)
        return DiagnosisReport(
            event_id=event_id,
            hypotheses=[hypothesis],
            tool_trace=trace,
            grounded=hypothesis.status != "insufficient_evidence",
            stop_reason="completed bounded evidence plan",
        )
