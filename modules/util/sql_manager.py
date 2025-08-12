from modules.util.exceptions import DatabaseError

import mysql.connector
from mysql.connector import pooling, Error as MySQLError
import json

async def setup(client, config):
    if not config.get("sql_enabled", False):
        SQLManager.set_enabled(False)

class SQLManager:
    _instance = None
    _enabled = True

    def __new__(cls):
        if not cls._enabled:
            return None
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        try:
            config = self._load_db_config()
            self.host = config["db_host"]
            self.user = config["db_user"]
            self.password = config["db_password"]
            self.database = config["db_name"]
            self.pool = None
            self._initialize_pool()
            self._initialized = True
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"[SQL] Failed to initialize - Config load error: {e}")
            type(self).set_enabled(False)
            type(self)._instance = None
            return
        except MySQLError as e:
            print(f"[SQL] Failed to initialize - DB connection error: {e}")
            type(self).set_enabled(False)
            type(self)._instance = None
            return
        
        print(f"[SQL] Intialized successfully.")

    def _initialize_pool(self, pool_name="UserDataPool", pool_size=5):
        self.pool = pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def _load_db_config(self):
        with open("private/sql_config.json", "r") as file:
            return json.load(file)

    def get_connection(self):
        if self.pool:
            try:
                return self.pool.get_connection()
            except MySQLError as e:
                print(f"[SQL] Connection error: {e}")
                raise DatabaseError(str(e))
        else:
            raise DatabaseError("SQLManager connection pool is not initialized.")

    def execute_query(self, query: str, params=None, insert_return_query=None, handle_except=True, connection=None):
        manage_connection = connection is None
        try:
            connection = connection or self.get_connection()
            if manage_connection:
                with connection:
                    return self._execute_query_logic(connection, query, params, insert_return_query)
            else:
                return self._execute_query_logic(connection, query, params, insert_return_query)
        except DatabaseError as e:
            if handle_except:
                print(f"[SQL] Query execution failed: {e}")
            else:
                raise

    def _execute_query_logic(self, connection, query, params, insert_return_query):
        cursor = connection.cursor(dictionary=True)
        result = None
        try:
            cursor.execute(query, params or ())
            command = query.strip().split()[0].lower()

            if command == "insert":
                connection.commit()
                if insert_return_query:
                    cursor.execute(insert_return_query)
                    result = cursor.fetchall()

            elif command == "select":
                result = cursor.fetchall()

            else:
                connection.commit()

            return result
        except MySQLError as e:
            raise DatabaseError(str(e))
        finally:
            cursor.close()

    def close_pool(self):
        if self.pool:
            try:
                self.pool.close()
            except MySQLError as e:
                print(f"[SQL] Error closing pool: {e}")

    @classmethod
    def get(cls):
        return cls._instance

    @classmethod
    def set_enabled(cls, enabled: bool):
        cls._enabled = enabled
