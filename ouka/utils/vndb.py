import aiohttp
from dataclasses import dataclass
from ..db import Database


@dataclass(slots=True)
class VNDBQuery:
    id: str
    title: str
    alt_title: str
    aliases: list[str]
    orig_lang: str
    released: str | None
    languages: list[str]
    platforms: list[str]
    image_url: str | None
    image_sexual: int
    image_violence: int
    length_minutes: int | None
    description: str | None
    rating: float | None
    vndb_link: str


async def post_vn(db: Database, query: str) -> list[VNDBQuery]:
    from .vndb_cache import pass_to_cache, in_cache

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.vndb.org/kana/vn",
            json={
                "filters": ["search", "=", query],
                "fields": "id, title, alttitle, aliases, olang, released, languages, platforms, image.url, image.sexual, image.violence, length_minutes, description, rating",
                "sort": "searchrank",
            },
        ) as response:
            res = await response.json()
            queries = [
                VNDBQuery(
                    id=result["id"],
                    title=result["title"],
                    alt_title=result["alttitle"],
                    aliases=result["aliases"],
                    orig_lang=result["olang"],
                    released=result["released"],
                    languages=result["languages"],
                    platforms=result["platforms"],
                    image_url=result["image"]["url"],
                    image_sexual=result["image"]["sexual"],
                    image_violence=result["image"]["violence"],
                    length_minutes=result["length_minutes"],
                    description=result["description"],
                    rating=result["rating"],
                    vndb_link=f"https://vndb.org/{result['id']}",
                )
                for result in res["results"]
            ]
            for q in queries:
                cached = await in_cache(db, q)
                if cached:
                    continue
                else:
                    await pass_to_cache(db, q)
            return queries
