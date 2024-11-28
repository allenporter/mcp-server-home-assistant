"""MCP server for Home Assistant."""

import asyncio
import logging
from typing import Any

from aiohttp import ClientSession

from hass_client.client import HomeAssistantClient
from hass_client.exceptions import BaseHassClientError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    Prompt,
    GetPromptResult,
)

_LOGGER = logging.getLogger(__name__)


async def create_server(
    url: str | None, token: str | None, aiohttp_session: ClientSession | None = None
) -> Server:
    """Create the MCP server."""
    server = Server("mcp-home-assistant")

    client = HomeAssistantClient(url, token, aiohttp_session)
    await client.connect()

    async def listener() -> None:
        """Start listening on the HA websockets."""
        try:
            # start listening will block until the connection is lost/closed
            await client.start_listening()
        except BaseHassClientError as err:
            _LOGGER.warning("Connection to HA lost due to error: %s", err)
        _LOGGER.info(
            "Connection to HA lost. Connection will be automatically retried later."
        )

    loop = asyncio.get_event_loop()
    loop.create_task(listener())

    @server.list_tools()  # type: ignore[no-untyped-call, misc]
    async def list_tools() -> list[Tool]:
        results = await client.send_command("mcp/tools/list")
        tools = [
            Tool(
                name=result["name"],
                description=result.get("description"),
                inputSchema=result.get("input_schema"),
            )
            for result in results["tools"]
        ]
        _LOGGER.debug("Returning %d tools", len(tools))
        return tools

    @server.call_tool()  # type: ignore[no-untyped-call, misc]
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        results = await client.send_command("mcp/tools/call")
        return [TextContent(**result) for result in results["content"]]

    @server.list_prompts()  # type: ignore[no-untyped-call, misc]
    async def list_prompts() -> list[Prompt]:
        prompts = await client.send_command("mcp/prompts/list")
        _LOGGER.debug("Returning %d resources", len(prompts))
        return [Prompt.model_validate(prompt) for prompt in prompts]

    @server.get_prompt()  # type: ignore[no-untyped-call, misc]
    async def get_prompt(name: str, arguments: dict[str, Any]) -> GetPromptResult:
        result = await client.send_command("mcp/prompts/get", name=name)
        _LOGGER.debug("Returning prompt result %s", name=name, arguments=arguments)
        return GetPromptResult.model_validate(result)

    return server


async def serve(
    url: str | None, token: str | None, aiohttp_session: ClientSession | None = None
) -> None:
    """Serve the MCP server."""
    server = await create_server(url, token, aiohttp_session)
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
