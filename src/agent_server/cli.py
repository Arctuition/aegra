"""Command-line interface for Aegra server management."""

from __future__ import annotations

import argparse
import os
import sys

import structlog
import uvicorn
from dotenv import load_dotenv

from .utils.setup_logging import get_logging_config, setup_logging

DEFAULT_DB_URL = "postgresql+asyncpg://user:password@localhost:5432/aegra"


def _apply_default_env() -> None:
    """Set sane defaults for local usage without overriding user config."""
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = DEFAULT_DB_URL
    if not os.getenv("AUTH_TYPE"):
        os.environ["AUTH_TYPE"] = "noop"


def _resolve_host_port(args: argparse.Namespace) -> tuple[str, int]:
    host = args.host or os.getenv("HOST", "0.0.0.0")
    port = args.port or int(os.getenv("PORT", "8000"))
    return host, port


def cmd_up(args: argparse.Namespace) -> int:
    """Start the Aegra server."""
    if args.config:
        os.environ["AEGRA_CONFIG"] = args.config

    load_dotenv()
    _apply_default_env()
    setup_logging()

    logger = structlog.get_logger(__name__)
    host, port = _resolve_host_port(args)

    logger.info("Starting Aegra", host=host, port=port)

    uvicorn.run(
        "agent_server.main:app",
        host=host,
        port=port,
        reload=args.reload,
        access_log=False,
        log_config=get_logging_config(),
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="arcsiteagent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    up_parser = subparsers.add_parser("up", help="Start the Aegra server")
    up_parser.add_argument(
        "--host",
        help="Host interface to bind (default: HOST env or 0.0.0.0)",
    )
    up_parser.add_argument(
        "--port",
        type=int,
        help="Port to bind (default: PORT env or 8000)",
    )
    up_parser.add_argument(
        "--config",
        help="Path to aegra.json or langgraph.json (sets AEGRA_CONFIG)",
    )
    up_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes",
    )
    up_parser.set_defaults(func=cmd_up)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
