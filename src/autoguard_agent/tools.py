from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .schemas import Evidence
from .store import EvidenceStore


Tool = Callable[..., list[Evidence]]


@dataclass
class ToolRegistry:
    store: EvidenceStore

    def query_logs(self, event_id: str) -> list[Evidence]:
        rows = self.store.query("SELECT * FROM logs WHERE event_id=? ORDER BY timestamp", (event_id,))
        return [Evidence(uri=f"log://{event_id}?t={row['timestamp']}&signal={row['signal']}", source_type="log", summary=f"{row['signal']}={row['value']} at {row['timestamp']}s", value=row["value"]) for row in rows]

    def get_version_diff(self, version: str) -> list[Evidence]:
        rows = self.store.query("SELECT * FROM version_changes WHERE version=?", (version,))
        return [Evidence(uri=f"version://{version}/change/{row['change_id']}", source_type="version", summary=f"{row['component']}.{row['field']}: {row['old_value']} -> {row['new_value']}", value=row) for row in rows]

    def compare_replays(self, event_id: str) -> list[Evidence]:
        rows = self.store.query("SELECT * FROM replays WHERE event_id=? ORDER BY timestamp, version", (event_id,))
        return [Evidence(uri=f"replay://{event_id}/{row['version']}?t={row['timestamp']}&field={row['field']}", source_type="replay", summary=f"{row['version']} {row['field']}={row['value']} at {row['timestamp']}s", value=row["value"]) for row in rows]

    def retrieve_similar_cases(self, query: str) -> list[Evidence]:
        token = f"%{query.lower()}%"
        rows = self.store.query("SELECT * FROM cases WHERE lower(title) LIKE ? OR lower(root_cause) LIKE ?", (token, token))
        return [Evidence(uri=f"case://{row['case_id']}", source_type="case", summary=f"{row['title']}: {row['root_cause']} / fix={row['fix']}", value=row) for row in rows]

    def call(self, name: str, arguments: dict[str, Any]) -> list[Evidence]:
        allowed: dict[str, Tool] = {
            "query_logs": self.query_logs,
            "get_version_diff": self.get_version_diff,
            "compare_replays": self.compare_replays,
            "retrieve_similar_cases": self.retrieve_similar_cases,
        }
        if name not in allowed:
            raise ValueError(f"unknown tool: {name}")
        return allowed[name](**arguments)
