"""Proxy module that re-exports the packaged authentication configuration.

Edit *src/agent_server/auth.py* to customize authentication for packaged builds.
"""

from agent_server.auth import *  # noqa: F401,F403

__all__ = ["auth", "AUTH_TYPE"]
