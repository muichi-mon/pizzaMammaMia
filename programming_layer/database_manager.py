from dotenv import load_dotenv
import os
import mysql.connector

class DatabaseManager:
    def __init__(self):
        # TODO: Load config from .env
        pass
    
    def get_connection(self):
        # TODO: Return DB connection
        pass
    
    def execute_query(self, query, params=None):
        # TODO: Execute SELECT queries
        pass
    
    def execute_transaction(self, queries):
        # TODO: Execute multiple queries in transaction
        pass
    
    def close_connection(self):
        # TODO: Close DB connection
        pass