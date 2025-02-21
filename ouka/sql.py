CREATE_BASE_TABLE = """
    CREATE TABLE IF NOT EXISTS vn_cache (
        primary_key INTEGER PRIMARY KEY AUTOINCREMENT,
        id TEXT UNIQUE,
        title TEXT,
        description TEXT,
        cover_image_url TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_cover_nsfw INTEGER DEFAULT 0
    )
"""

CREATE_FTS5_TABLE = """
    CREATE VIRTUAL TABLE IF NOT EXISTS vn_cache_fts USING fts5(
        id UNINDEXED,
        title,
        description,
        cover_image_url UNINDEXED,
        content = 'vn_cache',
        tokenize = 'porter'
    )
"""

VN_TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS vn_cache_insert
    AFTER INSERT ON vn_cache
    BEGIN
        INSERT INTO vn_cache_fts (id, title, cover_image_url)
        VALUES (new.id, new.title, new.cover_image_url);
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS vn_cache_delete
    AFTER DELETE ON vn_cache
    BEGIN
        DELETE FROM vn_cache_fts WHERE id = old.id;
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS vn_cache_update
    AFTER UPDATE ON vn_cache
    BEGIN
        UPDATE vn_cache_fts
        SET title = new.title,
            cover_image_url = new.cover_image_url
        WHERE id = new.id;
    END;
    """
]

VN_SEARCH_QUERY = """
    SELECT id, title, description, cover_image_url
    FROM vn_cache_fts
    WHERE title LIKE '%' || ? || '%'
    LIMIT 10;
"""

VN_ID_QUERY = """
    SELECT id, title, description, cover_image_url, is_cover_nsfw
    FROM vn_cache
    WHERE id = ?;
"""

VN_COVER_QUERY = """
    SELECT cover_image_url
    FROM vn_cache
    WHERE id = ? AND is_cover_nsfw < 0.6;
"""

VN_ID_EXISTS = """
    SELECT id FROM vn_cache WHERE id = ?;
"""

VN_CACHE_INSERT = """
    INSERT INTO vn_cache (id, title, description, cover_image_url, is_cover_nsfw)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET 
    title = excluded.title, 
    cover_image_url = excluded.cover_image_url, 
    timestamp = CURRENT_TIMESTAMP;
"""
