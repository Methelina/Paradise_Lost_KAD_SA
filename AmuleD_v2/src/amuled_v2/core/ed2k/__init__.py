"""ED2K client-protocol package.

src/amuled_v2/core/ed2k/__init__.py
Version:     0.1.0
Author:      Soror L.'.L.'.
Updated:     2026-09-22

Patch Notes v0.1.0 (Soror L.'.L'.):
  [+] Package marker for ED2K server-list and future protocol modules.
  [+] Re-exports server persistence API for CLI and import layers.
"""

from .server_met import (
    SERVER_MET_VERSION,
    ServerMetError,
    ServerRecord,
    StaticServer,
    load_server_met,
    load_static_servers,
    merge_server_lists,
    parse_server_met,
)

__all__ = [
    "SERVER_MET_VERSION",
    "ServerMetError",
    "ServerRecord",
    "StaticServer",
    "load_server_met",
    "load_static_servers",
    "merge_server_lists",
    "parse_server_met",
]
