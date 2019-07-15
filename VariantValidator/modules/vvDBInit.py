import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool


class Mixin:
    """
    A mixin containing the database initialisation routines.
    """
    def __init__(self, db_config):
        self.conn = None
        # self.cursor will be none UNLESS you're wrapping a function in @handleCursor, which automatically opens and
        # closes connections for you.
        self.cursor = None
        self.dbConfig = db_config

        self.pool = mysql.connector.pooling.MySQLConnectionPool(pool_size=10, **self.dbConfig)
        self.conn = self.pool.get_connection()

    def __del__(self):
        if self.conn.is_connected():
            try:
                self.conn.close()
            except mysql.connector.errors.NotSupportedError:
                pass
            self.conn = None
        if self.pool:
            self.pool = None