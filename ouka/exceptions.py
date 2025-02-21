class DatabaseError(Exception):
    pass


class DatabaseConnectionError(DatabaseError):
    pass


class DatabaseExecutionError(DatabaseError):
    pass


class DatabaseTransactionError(DatabaseError):
    pass
