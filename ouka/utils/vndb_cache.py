from .vndb import VNDBQuery
from ..db import Database
from ..sql import VN_CACHE_INSERT, VN_ID_QUERY, VN_ID_EXISTS, VN_SEARCH_QUERY
from dataclasses import dataclass
import logging

_log = logging.getLogger(__name__)

@dataclass(slots=True)
class CachedVNDBQuery:
    id: str
    title: str
    description: str
    image_url: str | None
    image_sexual: int

async def pass_to_cache(db: Database, query: VNDBQuery) -> None:
    await db.exec(
        VN_CACHE_INSERT,
        (query.id, query.title, query.description, query.image_url, query.image_sexual)
    )
    
async def get_id_cached(db: Database, query: str) -> CachedVNDBQuery:
    async with db.sel(VN_ID_QUERY, (query,)) as cursor:
        res = await cursor.fetchall()
    if res:
        if not res[0][3]:
            return CachedVNDBQuery(id=res[0][0], title=res[0][1], description=res[0][2], image_url=None, image_sexual=res[0][4])
        return CachedVNDBQuery(id=res[0][0], title=res[0][1], description=res[0][2], image_url=res[0][3], image_sexual=res[0][4])
    return None

async def search_cached_queries(db: Database, query: str) -> list[CachedVNDBQuery]:
    async with db.sel(VN_SEARCH_QUERY, (query,)) as cursor:
        res = await cursor.fetchall()
    if res:
        return [CachedVNDBQuery(id=result[0], title=result[1], description=result[2], image_url=result[3], image_sexual=-1) for result in res]
    return []
    
async def in_cache(db: Database, query: VNDBQuery) -> bool:
    async with db.sel(VN_ID_EXISTS, (query.id,)) as cursor:
        id = await cursor.fetchone()
    if id:
        return True
    return False