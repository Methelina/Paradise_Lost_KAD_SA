"""State / persistence layer for AmuleD_v2.

Uses DuckDB when available for runtime state, indexes, and kv metadata.
Falls back to a tiny JSON store (``db\\state.json``) when DuckDB is not
installed, marking the backend as ``json-fallback``.

Tables created on connect:
  - ``schema_migrations``  — idempotent schema version tracking.
  - ``kv_meta``            — arbitrary key/value metadata.

src/amuled_v2/state.py
Version:     0.1.0
Author:      Soror L.'.L.'.
Updated:     2026-09-22

Patch Notes v0.1.0 (Soror L.'.L'.):
  [+] Lazy DuckDB connection with JSON fallback.
  [+] Schema init: schema_migrations, kv_meta tables.
  [+] get_status() returns backend, path, and table counts.
  [+] close() method for clean teardown.
"""

from __future__ import annotations

import json
from typing import Any

from amuled_v2.paths import DB_FILE, STATE_JSON, ensure_runtime_dirs

# ------------------------------------------------------------------
# Backend selection
# ------------------------------------------------------------------

try:
    import duckdb  # type: ignore[import-untyped]
    _HAS_DUCKDB = True
except ImportError:  # pragma: no cover - exercised when duckdb absent
    _HAS_DUCKDB = False

_CURRENT_SCHEMA_VERSION = 1

_JSON_STORE: dict[str, Any] | None = None


# ------------------------------------------------------------------
# DuckDB helpers
# ------------------------------------------------------------------

def _init_duckdb(con: Any) -> None:
    """Create core tables if they do not already exist."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS kv_meta (
            key   VARCHAR PRIMARY KEY,
            value VARCHAR
        )
    """)
    # Record schema version if not present.
    row = con.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
    if row is None or row[0] is None or row[0] < _CURRENT_SCHEMA_VERSION:
        con.execute(
            "INSERT INTO schema_migrations (version) VALUES (?)",
            (_CURRENT_SCHEMA_VERSION,),
        )


def _json_get_store() -> dict[str, Any]:
    global _JSON_STORE
    if _JSON_STORE is None:
        ensure_runtime_dirs()
        if STATE_JSON.exists():
            with open(STATE_JSON, "r", encoding="utf-8") as fh:
                _JSON_STORE = json.load(fh)
        else:
            _JSON_STORE = {"schema_migrations": [], "kv_meta": {}}
    return _JSON_STORE


def _json_save_store() -> None:
    ensure_runtime_dirs()
    with open(STATE_JSON, "w", encoding="utf-8") as fh:
        json.dump(_JSON_STORE, fh, indent=2)


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

class StateBackend:
    """Thin wrapper around DuckDB or JSON fallback."""

    def __init__(self) -> None:
        self.backend: str = "duckdb" if _HAS_DUCKDB else "json-fallback"
        self.db_path: str = str(DB_FILE)
        self._con: Any | None = None

    def connect(self) -> None:
        if self._con is not None:
            return
        ensure_runtime_dirs()
        if _HAS_DUCKDB:
            self._con = duckdb.connect(str(DB_FILE))
            _init_duckdb(self._con)
        else:
            self._con = _json_get_store()

    def get_status(self) -> dict[str, Any]:
        """Return backend, db path, and table/row counts."""
        if self._con is None:
            self.connect()
        status: dict[str, Any] = {
            "backend": self.backend,
            "db_path": self.db_path,
            "tables": {},
        }
        if self.backend == "duckdb":
            tables = self._con.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'main'"
            ).fetchall()
            for (tname,) in tables:
                count = self._con.execute(f"SELECT COUNT(*) FROM {tname}").fetchone()[0]
                status["tables"][tname] = count
        else:
            status["tables"]["schema_migrations"] = len(
                self._con.get("schema_migrations", [])
            )
            status["tables"]["kv_meta"] = len(self._con.get("kv_meta", {}))
        return status

    def close(self) -> None:
        if self._con is not None:
            if self.backend == "duckdb" and self._con is not None:
                self._con.close()
            self._con = None


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_state: StateBackend | None = None


def get_state() -> StateBackend:
    """Return the shared :class:`StateBackend` instance (lazy)."""
    global _state
    if _state is None:
        _state = StateBackend()
    return _state
