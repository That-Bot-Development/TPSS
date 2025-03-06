import mysql.connector
from mysql.connector import pooling

import json

class SQLManager:
    _instance = None

    # Define as singleton
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        config = self.load_db_config()
        self.host = config['db_host']
        self.user = config['db_user']
        self.password = config['db_password']
        self.database = config['db_name']

        self.initialize_pool()

    def initialize_pool(self, pool_name="UserDataPool", pool_size=5):
        # Initialize the connection pool
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def load_db_config(self):
        # Load the configuration for this system
        with open("private/sql_config.json", "r") as file:
            config = json.load(file)
        return config

    def get_connection(self):
        # Get a connection from the pool
        if not self.pool:
            raise Exception("Connection pool is not initialized.")
        return self.pool.get_connection()

    def execute_query(self, query: str, params=None, handle_except=True,connection=None):
        # Create a new connection if not provided
        if not connection:
            connection = self.get_connection()

        cursor = connection.cursor(dictionary=True)
        result = None  # Default result
        
        try:
            cursor.execute(query, params or ())

            # If it's an INSERT query, fetch the last inserted ID
            if query.strip().lower().startswith("insert"):
                connection.commit()  # Commit changes for insert/update/delete
                last_inserted_id_query = "SELECT * FROM Punishments WHERE CaseNo = LAST_INSERT_ID()"
                cursor.execute(last_inserted_id_query)
                result = cursor.fetchall()

            # For SELECT queries, fetch the results
            elif query.strip().lower().startswith("select"):
                result = cursor.fetchall()

            # For other queries (UPDATE, DELETE), commit the changes
            else:
                connection.commit()

            return result

        except mysql.connector.Error as e:
            if handle_except:
                print(f"Database query error: {e}")
            else:
                raise
        finally:
            cursor.close()

            # Close the connection (if not externally provided)
            if not connection:
                connection.close()


    def close_pool(self):
        # Close the connection pool
        if self.pool:
            self.pool.close()

    @classmethod
    def get(cls):
        return cls._instance
