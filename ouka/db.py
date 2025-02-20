import aiosqlite
from pathlib import Path
from collections.abc import Iterable
from typing import Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import logging
import sqlite3

import aiosqlite.context
from .sql import CREATE_TABLE
from . import __DEBUG_DB_PATH__
import os
from .exceptions import DatabaseConnectionError, DatabaseExecutionError, DatabaseTransactionError
import asyncio

_log = logging.getLogger(__name__)

class Database:
    __slots__ = (
        "path",
        "conn",
    )

    def __init__(self, path: Path) -> None:
        """
        Initializes aiosqlite database connection.

        Args:
            path (Path): Path to the SQLite database file.

        Attributes:
            path (Path): Stored path to the database file.
            conn (Optional[aiosqlite.Connection]): Asynchronous SQLite connection object, initially None.
        """
        self.path = path
        # If the db directory doesnt exist create it
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> aiosqlite.Connection:
        """
        Establishes a connection to the SQLite database.

        This method attempts to connect to the database at the specified path. If the initial
        connection fails, it will retry up to 5 times with a 1-second delay between attempts.

        Returns:
            aiosqlite.Connection: An active database connection object.

        Raises:
            DatabaseConnectionError: If all connection attempts fail after retries.

        Note:
            The connection object is stored in self.conn and reused for subsequent calls.
        """
        if self.conn is None:
            try:
                self.conn = await aiosqlite.connect(self.path)
                _log.debug(f"Connected to database at {self.path}")
            except sqlite3.Error as e:
                _log.critical(f"Database connection failed: {str(e)}. Attempting to restart...")
                for i in range(5):
                    await asyncio.sleep(1)
                    try:
                        self.conn = await aiosqlite.connect(self.path)
                        _log.debug(f"Connected to database at {self.path} after retry #{i + 1}.")
                        return self.conn
                    except sqlite3.Error:
                        continue
                raise DatabaseConnectionError(f"Failed to connect to the database at {self.path}") from e
        return self.conn
        

    async def create(self) -> None:
        """
        Create the necessary tables in the database.

        This method should only be used within `__main__.py`.

        Raises:
            Exception: If there is an issue executing the CREATE_TABLE command.
        """
        try:  
            await self.exec(CREATE_TABLE)
        except sqlite3.Error as e:
            _log.critical("Failed to create tables.")
            raise DatabaseExecutionError("Failed to create tables.") from e

    async def exec(
        self, sql: str, parameters: Optional[Iterable[Any]] | None = None
    ) -> aiosqlite.Cursor:
        """
        Executes the given SQL statement with the provided parameters and commits the transaction.

        Args:
            sql (str): The SQL statement to execute.
            parameters (Optional[Iterable[Any]]): The parameters to bind to the SQL statement. Defaults to None.

        Returns:
            aiosqlite.Cursor: The cursor object resulting from the executed SQL statement.

        Raises:
            DatabaseExecutionError: If there is an error executing the SQL statement.
            DatabaseTransactionError: If there is an error committing the transaction.

        Notes:
            This function is similar to aiosqlite's `execute` function, but it commits the transaction before returning.
        """
        if parameters is None:
            parameters = []
        try: 
            cursor = await self.conn.execute(sql, parameters)
        except sqlite3.Error as e:
            _log.critical(f"Failed to execute SQL: {sql}")
            raise DatabaseExecutionError(f"Failed to execute SQL into {self.path}.") from e
        try:
            await self.conn.commit()
        except sqlite3.Error as e:
            _log.critical("Failed to commit transaction.")
            raise DatabaseTransactionError("Failed to commit transaction.") from e
        return cursor
                
    
    @asynccontextmanager
    async def sel(
        self, sql: str, parameters: Optional[Iterable[Any]] | None = None
    ) -> AsyncGenerator[aiosqlite.Cursor, None]:
        """
        Execute a SQL query and yield the cursor for asynchronous context management.

        Args:
            sql (str): The SQL query to execute.
            parameters (Optional[Iterable[Any]] | None): The parameters to bind to the SQL query. Defaults to None.

        Yields:
            AsyncGenerator[aiosqlite.Cursor, None]: An asynchronous generator yielding the cursor.

        Raises:
            Exception: If an exception occurs during the execution of the SQL query, it is logged and re-raised.
            
        Notes:
            Exactly the same as the `execute` aiosqlite function, but renamed for better readability.
        """
        if parameters is None:
            parameters = []
        cursor = await self.conn.execute(sql, parameters)
        try:
            yield cursor
        except Exception as e:
            _log.error("Exception occurred:", exc_info=e)
        finally:
            await cursor.close()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def _delete(self) -> None:
        """
        Delete the debug database file if it exists.

        WARNING: This method should only be used when the `wipe` variable in `__init__.py` is set to True.

        Raises:
            FileNotFoundError: If the debug database file does not exist.
        """
        if os.path.exists(__DEBUG_DB_PATH__):
            try:
                os.remove(__DEBUG_DB_PATH__)
            except FileNotFoundError as e:
                _log.critical(f"Failed to delete debug database at {__DEBUG_DB_PATH__}.")
                raise e
