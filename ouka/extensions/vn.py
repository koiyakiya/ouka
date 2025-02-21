import logging

import arc
import re
import hikari as hk
from ..utils import vndb, vndb_cache
from ..db import Database

_log = logging.getLogger(__name__)

plugin = arc.GatewayPlugin("VNModule")

@plugin.inject_dependencies
async def vn_autocomplete(data: arc.AutocompleteData[arc.GatewayClient, str], db: Database = arc.inject()) -> list[str]:
    value = data.focused_value or ""
    if not value:
        return []

    # If input is "v123", strip the 'v'
    if value.startswith("v") and value[1:].isdigit():
        value = value[1:]

    results = []
    if value.isdigit():
        cached_result = await vndb_cache.get_id_cached(db, f"v{value}")
        if cached_result:
            return [f"{cached_result.title} ({cached_result.id}) (Cache)"]
        results = await vndb.post_vn(db, f"v{value}")
    else:
        cached_results = await vndb_cache.search_cached_queries(db, value)
        if cached_results:
            return [f"{r.title} ({r.id}) (Cache)" for r in cached_results]
        results = await vndb.post_vn(db, value)

    return [f"{r.title} ({r.id}) (API)" for r in results] if results else []

@plugin.include
@arc.slash_command("vn", "Search for a visual novel on VNDB")
@plugin.inject_dependencies
async def vn_command(
    ctx: arc.GatewayContext,
    query: arc.Option[str, arc.StrParams("The visual novel you want to search for.", autocomplete_with=vn_autocomplete)],
    db: Database = arc.inject(),
) -> None:
    query = query.split(" (")[0]
    # Defer the response to prevent the command from timing out
    await ctx.defer()
    
    res = await vndb_cache.search_cached_queries(db, query)
    if not res:
        res = await vndb.post_vn(db, query)
        if not res:
            await ctx.respond("No results found.")
            return
    title_prefix = "🔞 " if res[0].image_sexual > 0 else ""
    embed = hk.Embed(
        title=f"{title_prefix}{res[0].title} ({str(res[0].id)})",
        description=(re.sub(r'\[url=(.*?)\](.*?)\[/url\]', r'[\2](\1)', res[0].description)
                    .replace('[b]', '**').replace('[/b]', '**')
                    .replace('(/c', '(https://vndb.org/c')),
        color=0x00FF00,
    )
    if res[0].image_sexual <= 0.6:
        embed.set_image(res[0].image_url)
        
    await ctx.respond(embed=embed)

@arc.loader
def loader(client: arc.GatewayClient, db: Database = arc.inject()) -> None:
    client.add_plugin(plugin)