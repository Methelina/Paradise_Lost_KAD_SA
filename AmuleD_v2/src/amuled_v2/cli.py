"""Command-line interface for AmuleD_v2.

Provides an argparse-based English CLI with optional ``--json`` output.
Commands:
  - ``status``              — show backend, db path, table counts, version.
  - ``config show``         — print current JSONC config.
  - ``config set <key> <v>``— set a dotted config key (type-inferred).
  - ``init``                — ensure runtime dirs and default config exist.
  - ``daemon start/stop``   — M2 stubs returning not_implemented.

Dependencies (duckdb, rich) are optional at runtime; ``--help`` works without
them installed.  Network/protocol modules are not imported.

src/amuled_v2/cli.py
Version:     0.1.0
Author:      Soror L.'.L.'.
Updated:     2026-09-22

Patch Notes v0.1.0 (Soror L.'.L'.):
  [+] argparse CLI with --json, status, config show/set, init, daemon.
  [+] Lazy imports so --help works without optional deps.
  [+] status and config work without network.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from amuled_v2 import __version__
from amuled_v2.config import config_set, config_show, load_config
from amuled_v2.daemon import start_daemon, stop_daemon
from amuled_v2.logging_setup import configure_logging
from amuled_v2.state import get_state


# ------------------------------------------------------------------
# Output helpers
# ------------------------------------------------------------------

def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))


def _print_text(header: str, lines: list[str]) -> None:
    print(header)
    for line in lines:
        print(f"  {line}")


# ------------------------------------------------------------------
# Command handlers
# ------------------------------------------------------------------

def _cmd_status(args: argparse.Namespace) -> int:
    cfg = load_config(save_if_missing=True)
    st = get_state()
    st.connect()
    status = st.get_status()
    result: dict = {
        "app": "amuled-v2",
        "version": __version__,
        "backend": status["backend"],
        "db_path": status["db_path"],
        "tables": status["tables"],
        "network": {
            "client_tcp_port": cfg["network"]["client_tcp_port"],
            "client_udp_port": cfg["network"]["client_udp_port"],
            "enable_ed2k": cfg["network"]["enable_ed2k"],
            "enable_kad": cfg["network"]["enable_kad"],
        },
    }
    if args.json:
        _print_json(result)
    else:
        _print_text("AmuleD_v2 Status", [
            f"version    : {result['version']}",
            f"backend    : {result['backend']}",
            f"db_path    : {result['db_path']}",
            f"tables     : {result['tables']}",
            f"tcp_port   : {result['network']['client_tcp_port']}",
            f"udp_port   : {result['network']['client_udp_port']}",
            f"ed2k       : {result['network']['enable_ed2k']}",
            f"kad        : {result['network']['enable_kad']}",
        ])
    return 0


def _cmd_config_show(args: argparse.Namespace) -> int:
    return config_show(json_output=args.json)


def _cmd_config_set(args: argparse.Namespace) -> int:
    return config_set(args.key, args.value, json_output=args.json)


def _cmd_init(args: argparse.Namespace) -> int:
    from amuled_v2.paths import ensure_runtime_dirs

    created = ensure_runtime_dirs()
    load_config(save_if_missing=True)
    st = get_state()
    st.connect()
    status = st.get_status()
    result: dict = {
        "status": "ok",
        "dirs_created": [str(p) for p in created] if created else [],
        "backend": status["backend"],
        "db_path": status["db_path"],
    }
    if args.json:
        _print_json(result)
    else:
        _print_text("Init", [
            f"status       : {result['status']}",
            f"dirs_created : {result['dirs_created']}",
            f"backend      : {result['backend']}",
            f"db_path      : {result['db_path']}",
        ])
    return 0


def _cmd_daemon_start(args: argparse.Namespace) -> int:
    code, info = start_daemon()
    result = info.to_dict()
    if args.json:
        _print_json(result)
    else:
        _print_text("Daemon", [
            f"status   : {result['status']}",
            f"message  : {result['message']}",
        ])
    return code


def _cmd_daemon_stop(args: argparse.Namespace) -> int:
    code, info = stop_daemon()
    result = info.to_dict()
    if args.json:
        _print_json(result)
    else:
        _print_text("Daemon", [
            f"status   : {result['status']}",
            f"message  : {result['message']}",
        ])
    return code


# ------------------------------------------------------------------
# Argument parser
# ------------------------------------------------------------------

def _make_parents() -> argparse.ArgumentParser:
    """Parent parser carrying --json for both top-level and subcommand use."""
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit machine-readable JSON output.",
    )
    return parent


def build_parser() -> argparse.ArgumentParser:
    parents = [_make_parents()]

    parser = argparse.ArgumentParser(
        prog="amuled",
        description="Pure Python ED2K/Kademlia client (AmuleD v2).",
        parents=parents,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"amuled-v2 {__version__}",
    )

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # --- status ---
    p_status = sub.add_parser("status", help="Show client status.", parents=parents)
    p_status.set_defaults(func=_cmd_status)

    # --- config ---
    p_config = sub.add_parser("config", help="Manage configuration.", parents=parents)
    cfg_sub = p_config.add_subparsers(dest="config_command", metavar="<action>")
    p_cfg_show = cfg_sub.add_parser("show", help="Show current config.", parents=parents)
    p_cfg_show.set_defaults(func=_cmd_config_show)
    p_cfg_set = cfg_sub.add_parser("set", help="Set a dotted config key.", parents=parents)
    p_cfg_set.add_argument("key", help="Dotted key, e.g. network.client_tcp_port")
    p_cfg_set.add_argument("value", help="Value (bool/int/float/str inferred).")
    p_cfg_set.set_defaults(func=_cmd_config_set)

    # --- init ---
    p_init = sub.add_parser("init", help="Initialize runtime dirs and config.", parents=parents)
    p_init.set_defaults(func=_cmd_init)

    # --- daemon ---
    p_daemon = sub.add_parser("daemon", help="Daemon lifecycle (M2 stub).", parents=parents)
    d_sub = p_daemon.add_subparsers(dest="daemon_command", metavar="<action>")
    p_d_start = d_sub.add_parser("start", help="Start daemon (stub).", parents=parents)
    p_d_start.set_defaults(func=_cmd_daemon_start)
    p_d_stop = d_sub.add_parser("stop", help="Stop daemon (stub).", parents=parents)
    p_d_stop.set_defaults(func=_cmd_daemon_stop)

    return parser


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "command", None):
        parser.print_help()
        return 0

    # Configure logging lazily (optional deps already guarded).
    cfg = load_config(save_if_missing=True)
    log_level = cfg.get("logging", {}).get("level", "INFO")
    configure_logging(log_level)

    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0
    return func(args)


if __name__ == "__main__":
    sys.exit(main())
