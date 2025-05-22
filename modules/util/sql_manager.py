import mysql.connector

import json

#TODO: Have a way to disable SQL functionality TODO: Exception handling & disabling of functionality if connection cannot be established with given credentials
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

        self.pool = None
        try:
            self.initialize_pool()
        except Exception as e:
            #TODO: Individual error handling
            print(f"-- Couldn't connect to SQL database! --\n{e}")
            pass

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
        if self.pool:
            return self.pool.get_connection()
        else:
            # TODO: Change to custom exception type, catch for commands, and other uses 
            raise Exception("No connection pool available!")

    def execute_query(self, query: str, params=None, insert_return_query=None, handle_except=True, connection=None):
        # Determine if we should manage the connection
        manage_connection = connection is None

        # Create a new connection if not provided
        connection = connection or self.get_connection()

        if manage_connection:
            with connection:  # Use 'with' only when we create the connection
                return self._execute_query_logic(connection, query, params, insert_return_query, handle_except)
        else:
            return self._execute_query_logic(connection, query, params, insert_return_query, handle_except)

    def _execute_query_logic(self, connection, query, params, insert_return_query, handle_except):
        cursor = connection.cursor(dictionary=True)
        result = None  # Default result

        try:
            cursor.execute(query, params or ())

            if query.strip().lower().startswith("insert"):
                connection.commit()
                if insert_return_query:
                    cursor.execute(insert_return_query)
                    result = cursor.fetchall()

            elif query.strip().lower().startswith("select"):
                result = cursor.fetchall()

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

    def close_pool(self):
        # Close the connection pool
        if self.pool:
            self.pool.close()

    @classmethod
    def get(cls):
        return cls._instance
