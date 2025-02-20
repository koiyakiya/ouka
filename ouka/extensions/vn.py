import logging

import arc
import re
import hikari as hk
from ..utils import vndb

_log = logging.getLogger(__name__)

plugin = arc.GatewayPlugin("VNModule")

@plugin.include
@arc.slash_command("vn", "Search for a visual novel on VNDB", autodefer=arc.AutodeferMode.EPHEMERAL)
async def vn_command(
    ctx: arc.GatewayContext,
    query: arc.Option[str, arc.StrParams("The visual novel you want to search for.")]
) -> None:
    res = await vndb.post_vn(query)
    if not res: 
        await ctx.respond("No results found.")
        return
    title_prefix = "🔞 " if res[0].image_sexual > 0 else ""
    embed = hk.Embed(
        title=f"{title_prefix}{res[0].title} ({str(res[0].id)})",
        description=(re.sub(r'\[url=(.*?)\](.*?)\[/url\]', r'[\2](\1)', res[0].description)
                    .replace('[b]', '**').replace('[/b]', '**')
                    .replace('(/c', '(https://vndb.org/c')),
        url=res[0].vndb_link,
        color=0x00FF00,
    )
    if res[0].image_sexual <= 0.6 and res[0].image_violence <= 0.6:
        embed.set_image(res[0].image_url)
    if res[0].rating is None:
        embed.add_field("Rating", "N/A")
    else:
        embed.add_field("Rating", f"{round(res[0].rating / 10)}/10")
    # Use minutes if the length / 60 is less than 1 hour otherwise use hours
    if res[0].length_minutes is None:
        embed.add_field("Length", "N/A")
    else:
        if round(res[0].length_minutes / 60) <= 1:
            embed.add_field("Length", "~" + str(res[0].length_minutes) + " minutes")
        else:
            embed.add_field("Length", "~" + str(round(res[0].length_minutes / 60)) + " hours")
    
    # also known as
    if res[0].alt_title is not None:
        embed.add_field("Also known as", res[0].alt_title)
    await ctx.respond(embed=embed)

@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)