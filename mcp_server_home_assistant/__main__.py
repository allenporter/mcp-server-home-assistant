import os
import click
import logging
import sys
from .server import serve

HOME_ASSISTANT_WEB_SOCKET_URL = os.getenv("HOME_ASSISTANT_WEB_SOCKET_URL")
HOME_ASSISTANT_API_TOKEN = os.getenv("HOME_ASSISTANT_API_TOKEN")


@click.command()
@click.option("--url", required=False, help="Home Assistant websocket url")
@click.option("--token", required=False, help="Home Assistant token")
@click.option("-v", "--verbose", count=True)
def main(url: str, token: str, verbose: bool) -> None:
    """MCP Home Assistant Server."""
    import asyncio

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    if not url:
        url = HOME_ASSISTANT_WEB_SOCKET_URL
        if not url:
            raise click.ClickException("url or environment var HOME_ASSISTANT_WEB_SOCKET_URL is required")
    if not token:
        token = HOME_ASSISTANT_API_TOKEN
        if not token:
            raise click.ClickException("token or environment var HOME_ASSISTANT_API_TOKEN is required")

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve(url or HOME_ASSISTANT_WEB_SOCKET_URL, token or HOME_ASSISTANT_API_TOKEN))

if __name__ == "__main__":
    main()
