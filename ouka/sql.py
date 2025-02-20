CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS kneelboard
    (guild_id INTEGER, member_id INTEGER, member_name VARCHAR(32), kneels INTEGER, rank INTEGER UNIQUE, PRIMARY KEY (guild_id, member_id));
"""

INSERT_INTO_KNEEL_ADD = """
    INSERT OR IGNORE INTO kneelboard
    (guild_id, member_id, member_name, kneels)
    VALUES (?, ?, ?, ?)
"""

SELECT_KNEEL_ADD = """
    SELECT kneels
    FROM kneelboard
    WHERE guild_id = ?
    AND member_id = ?
"""

SELECT_GUILD_KNEELS = """
    SELECT member_id, kneels
    FROM kneelboard
    WHERE guild_id = ?
"""

UPDATE_KNEEL_ADD = """
    UPDATE kneelboard
    SET kneels = kneels + 1
    WHERE guild_id = ?
    AND member_id = ?
"""
