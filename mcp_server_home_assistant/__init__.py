"""
.. include:: ../README.md
"""

import click
import logging
import sys
from .server import serve


@click.command()
@click.option("--url", required=True, help="Home Assistant websocket url")
@click.option("--token", required=True, help="Home Assistant token")
@click.option("-v", "--verbose", count=True)
def main(url: str, token: str, verbose: bool) -> None:
    """MCP Home Assistant Server."""
    import asyncio

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve(url, token))


if __name__ == "__main__":
    main()
