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
        results = await client.send_command("mcp/tools/list")
        tools = [Tool(**result) for result in results["tools"]]
        _LOGGER.debug("Returning %d tools", len(tools))
        return tools

    @server.call_tool()  # type: ignore[no-untyped-call, misc]
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        results = await client.send_command("mcp/tools/call")
        return [TextContent(**result) for result in results["content"]]

    @server.list_resources()  # type: ignore[no-untyped-call, misc]
    async def list_resources() -> list[dict]:
        _LOGGER.debug("Listing resources")
        results = await client.send_command("mcp/resources/list")
        resources = results["resources"]
        _LOGGER.debug("Returning %d resources", len(resources))
        return resources

    @server.read_resource()  # type: ignore[no-untyped-call, misc]
    async def read_resource(uri: str) -> dict:
        results = await client.send_command("mcp/resources/read", uri=uri)
        contents = results["contents"]
        _LOGGER.debug("Returning %d contents", len(contents))
        return contents

    return server


async def serve(
    url: str | None, token: str | None, aiohttp_session: ClientSession | None = None
) -> None:
    """Serve the MCP server."""
    server = await create_server(url, token, aiohttp_session)
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
