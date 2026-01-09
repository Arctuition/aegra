#!/usr/bin/env python3
"""Build and publish the package using uv."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, env=env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="publish.py")
    parser.add_argument(
        "--index",
        help="uv index name (from [[tool.uv.index]]), e.g. testpypi",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip uv build (assumes dist/ already exists)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not remove existing dist/ before build",
    )
    parser.add_argument(
        "--no-sources",
        action="store_true",
        help="Build with --no-sources (recommended for publish parity)",
    )
    parser.add_argument(
        "--token",
        help="PyPI token (sets UV_PUBLISH_TOKEN for uv publish)",
    )
    parser.add_argument(
        "--username",
        help="Username for uv publish (sets UV_PUBLISH_USERNAME)",
    )
    parser.add_argument(
        "--password",
        help="Password for uv publish (sets UV_PUBLISH_PASSWORD)",
    )
    parser.add_argument(
        "--no-attestations",
        action="store_true",
        help="Disable attestation uploads",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)

    if not args.skip_build:
        dist_dir = project_root / "dist"
        if dist_dir.exists() and not args.no_clean:
            shutil.rmtree(dist_dir)
        build_cmd = ["uv", "build"]
        if args.no_sources:
            build_cmd.append("--no-sources")
        run(build_cmd)

    env = os.environ.copy()
    if args.token:
        env["UV_PUBLISH_TOKEN"] = args.token
    if args.username:
        env["UV_PUBLISH_USERNAME"] = args.username
    if args.password:
        env["UV_PUBLISH_PASSWORD"] = args.password

    publish_cmd = ["uv", "publish"]
    if args.index:
        publish_cmd += ["--index", args.index]
    if args.no_attestations:
        publish_cmd.append("--no-attestations")

    run(publish_cmd, env=env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
