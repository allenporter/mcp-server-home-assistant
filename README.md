# mcp-server-home-assistant

A Model Context Protocol Server for Home Assistant. See [Model Context Protocol](https://modelcontextprotocol.io/)
for context.

The custom component required by this integration is moving to Home Assistant Core in https://github.com/home-assistant/core/pull/134122

## Usage in Claude Desktop

1. Install the [home-assistant-model-context-protocol](https://github.com/allenporter/home-assistant-model-context-protocol) custom component in your Home Assistant instance
1. Create a [Long Lived Access Token](https://www.home-assistant.io/docs/authentication/#your-account-profile)
1. Clone this git repo to a path like `/Users/allen/Development/mcp-server-home-assistant`
1. Edit your `claude_desktop_config.json` with something like this and include your home assistant url and api token:

    ```json
    {
        "mcpServers": {
            "Home-assistant": {
                "command": "uv",
                "args": [
                    "--directory",
                    "/Users/allen/Development/mcp-server-home-assistant",
                    "run",
                    "mcp-server-home-assistant",
                    "-v",
                    "-v"
                ],
                "env": {
                    "HOME_ASSISTANT_WEB_SOCKET_URL": "http://localhost:8123/api/websocket",
                    "HOME_ASSISTANT_API_TOKEN": "byJhbVci0iJIUzI1ii1sInR5cCI6IkpXVCJ9.....
                }
            }
        }
    }
    ```
1. You can view the logs e.g. `~Library/Logs/Claude/mcp-server-Home-assistant.log` to understand what is happening
