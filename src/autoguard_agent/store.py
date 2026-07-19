from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS logs(event_id TEXT, timestamp REAL, signal TEXT, value TEXT);
CREATE TABLE IF NOT EXISTS version_changes(version TEXT, change_id TEXT, component TEXT, field TEXT, old_value TEXT, new_value TEXT);
CREATE TABLE IF NOT EXISTS replays(event_id TEXT, version TEXT, timestamp REAL, field TEXT, value TEXT);
CREATE TABLE IF NOT EXISTS cases(case_id TEXT, title TEXT, root_cause TEXT, fix TEXT);
"""


class EvidenceStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)

    def insert(self, table: str, **values: Any) -> None:
        columns = ",".join(values)
        placeholders = ",".join("?" for _ in values)
        self.connection.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",  # noqa: S608 controlled table names
            [json.dumps(v) if isinstance(v, (dict, list)) else str(v) for v in values.values()],
        )
        self.connection.commit()

    def query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        if not sql.lstrip().upper().startswith("SELECT"):
            raise ValueError("read-only evidence queries only")
        return [dict(row) for row in self.connection.execute(sql, params).fetchall()]

    @classmethod
    def demo(cls) -> "EvidenceStore":
        store = cls()
        store.insert("logs", event_id="EVT-001", timestamp=12.34, signal="object_328.class", value="pedestrian")
        store.insert("logs", event_id="EVT-001", timestamp=12.58, signal="acceleration_command_mps2", value=-2.4)
        store.insert("version_changes", version="V2.7.0", change_id="CFG-108", component="perception", field="pedestrian_threshold", old_value=0.42, new_value=0.35)
        store.insert("replays", event_id="EVT-001", version="V2.6.8", timestamp=12.34, field="object_328.class", value="static_unknown")
        store.insert("replays", event_id="EVT-001", version="V2.7.0", timestamp=12.34, field="object_328.class", value="pedestrian")
        store.insert("cases", case_id="CASE-17", title="billboard false positive", root_cause="low pedestrian threshold", fix="temporal consistency gate")
        return store
