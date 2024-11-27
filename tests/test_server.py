"""Tests for mcp_server_home_assistant."""

from typing import Any
from collections.abc import AsyncGenerator

import pytest
import aiohttp

from mcp_server_home_assistant.server import create_server

# TODO: Home Assistant client is not really testable at the moment because of a
# logging statement that conflicts with aiohttp test client absolute url requirements
HASS_CLIENT_HACK = "://"
TEST_HOST_PATH = f"/api/websocket{HASS_CLIENT_HACK}"
TEST_TOKEN = "aiohttp-token"

AUTH_REQUIRED_MESSAGE = {"type": "auth_required", "ha_version": "some-version"}
AUTH_OK = {"type": "auth_ok", "ha_version": "2021.5.3"}


async def websocket_handler(
    request: aiohttp.web.Request,
) -> aiohttp.web.WebSocketResponse:
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    await ws.send_json(AUTH_REQUIRED_MESSAGE)
    await ws.receive_json()
    await ws.send_json(AUTH_OK)
    return ws


@pytest.fixture(name="test_client")
async def aiohttp_client_fixture(
    aiohttp_client: Any,
) -> AsyncGenerator[aiohttp.ClientSession, None]:
    """Fixture for an aiohttp client."""
    app = aiohttp.web.Application()
    app.router.add_get(TEST_HOST_PATH, websocket_handler)
    client = await aiohttp_client(app)
    yield client


async def test_create_server(test_client: aiohttp.ClientSession) -> None:
    """Test creating the mcp server."""
    await create_server(TEST_HOST_PATH, TEST_TOKEN, test_client)
