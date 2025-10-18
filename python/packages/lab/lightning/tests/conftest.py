# Copyright (c) Microsoft. All rights reserved.

"""Pytest configuration that disables outbound telemetry during tests."""

from __future__ import annotations

import pytest
from pytest import MonkeyPatch
from requests import Response, Session


def _is_localhost(url: str) -> bool:
    return url.startswith(("http://127.0.0.1", "http://localhost", "https://127.0.0.1", "https://localhost"))


@pytest.fixture(scope="session", autouse=True)
def disable_agentops_telemetry() -> None:
    """Prevent AgentOps telemetry from making outbound HTTP calls during tests."""
    mp = MonkeyPatch()
    mp.setenv("AGENTOPS_FAIL_SAFE", "true")
    mp.setenv("AGENTOPS_PREFETCH_JWT_TOKEN", "false")
    mp.setenv("AGENTOPS_LOG_LEVEL", "CRITICAL")

    original_post = Session.post

    def _safe_post(self, url, *args, **kwargs):
        if isinstance(url, str) and _is_localhost(url):
            resp = Response()
            resp.status_code = 200
            resp._content = b""
            return resp
        return original_post(self, url, *args, **kwargs)

    mp.setattr(Session, "post", _safe_post, raising=False)
    try:
        yield
    finally:
        mp.undo()
