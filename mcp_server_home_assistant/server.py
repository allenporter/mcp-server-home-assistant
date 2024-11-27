"""MCP server for Home Assistant."""

import logging

from aiohttp import ClientSession

from hass_client.client import HomeAssistantClient
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

_LOGGER = logging.getLogger(__name__)


async def create_server(
    url: str | None, token: str | None, aiohttp_session: ClientSession | None = None
) -> Server:
    """Create the MCP server."""
    server = Server("mcp-home-assistant")

    client = HomeAssistantClient(url, token, aiohttp_session)
    await client.connect()

    @server.list_tools()  # type: ignore[no-untyped-call, misc]
    async def list_tools() -> list[Tool]:
        results = await client.send_command("mcp/list_tools")
        return [Tool(**result) for result in results]

    @server.call_tool()  # type: ignore[no-untyped-call, misc]
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        results = await client.send_command("mcp/call_tool")
        return [TextContent(**result) for result in results]

    return server


async def serve(
    url: str | None, token: str | None, aiohttp_session: ClientSession | None = None
) -> None:
    """Serve the MCP server."""
    server = await create_server(url, token, aiohttp_session)
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)