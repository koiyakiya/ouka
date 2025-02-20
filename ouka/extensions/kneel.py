import logging

import arc
import hikari as hk
from ..sql import SELECT_KNEEL_ADD, INSERT_INTO_KNEEL_ADD, UPDATE_KNEEL_ADD
from ..sql import *
from ..db import Database

_log = logging.getLogger(__name__)

plugin = arc.GatewayPlugin("KneelModule")


@plugin.listen()
@plugin.inject_dependencies
async def kneel_reaction_added(
    event: hk.GuildReactionAddEvent,
    db: Database = arc.inject(),
    rest: hk.api.RESTClient = arc.inject(),
) -> None:
    if event.emoji_name.lower() == "ikneel":
        gid: hk.Snowflake = event.guild_id
        cid: hk.Snowflake  = event.channel_id
        mid: hk.Snowflake  = event.message_id
        msg: hk.Message = await rest.fetch_message(cid, mid)
        _log.debug(f"Fetching message... {msg=}")
        async with db.sel(SELECT_KNEEL_ADD, (gid, msg.author.id)) as cur:
            res = await cur.fetchone()
            _log.debug(f"{res=}")
        if res is None:
            await db.exec(INSERT_INTO_KNEEL_ADD, (gid, msg.author.id, msg.author.display_name, 1))
            _log.info(f"Executing INSERT_INTO_KNEEL_ADD: {gid=}, {msg.author.id=}, {msg.author.display_name=}, 1")
        else:
            await db.exec(UPDATE_KNEEL_ADD, (gid, msg.author.id))
            _log.info(f"Executing UPDATE_KNEEL_ADD: {gid=}, {msg.author.id=}, {msg.author.display_name=}")
            
    


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)
