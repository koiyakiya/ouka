import hikari, arc
from . import (
    __TOKEN__,
    debug_mode,
    __DEBUG_DB_PATH__,
    __PROD_DB_PATH__,
    __EXTENSIONS_PATH__,
    wipe,
)
from pathlib import Path
from .log import init_logger
from .db import Database
import logging
import os
from .utils import vndb

if debug_mode:
    init_logger(logging.DEBUG)
else:
    init_logger()

_log = logging.getLogger(__name__)

bot = hikari.GatewayBot(
    __TOKEN__,
    # Allow hikari to cache a guild's roles, members,
    # messages, etc for use later, without having to repeatedly call the rest API.
    cache_settings=hikari.impl.CacheSettings(
        components=hikari.impl.CacheComponents.ALL
    ),
    # As this bot is not intended to go mainstream, all intents
    # here is fine for now.
    intents=hikari.Intents.ALL,
)

# Funnel the `bot` GatewayBot into arc
client = arc.GatewayClient(bot)

# Load all extensions in the specified folder
client.load_extensions_from(__EXTENSIONS_PATH__)


@client.add_startup_hook
async def startup_hook(client: arc.GatewayClient) -> None:
    if debug_mode:
        db = Database(Path(__DEBUG_DB_PATH__))
    else:
        db = Database(Path(__PROD_DB_PATH__))

    await db.connect()
    
    await db.create()
    
    # Execute all VN cache triggers
    await db._execute_triggers()

    # Use arc for dependency injection. Now we can use the db practically anywhere without
    # having to make multiple instances of it.
    client.set_type_dependency(Database, db)
    # Allow access to the REST API without having to call any bot
    client.set_type_dependency(hikari.api.RESTClient, bot.rest)


@client.add_shutdown_hook
@client.inject_dependencies
async def shutdown_hook(client: arc.GatewayClient, db: Database = arc.inject()) -> None:
    await db.close()
    _log.info("Database successfully closed.")

    if wipe and debug_mode:
        await db._delete()
        _log.critical("Debug database successfully wiped.")


if __name__ == "__main__":
    # Speeds things up on Linux servers
    if os.name != "nt":
        import asyncio, uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    bot.run()
