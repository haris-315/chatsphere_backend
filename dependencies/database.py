import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv


load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URI")
client = MongoClient("mongodb+srv://hkffking:8xB5GzYe0lc2tZl8@cluster0.3j2sw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0&ssl=true")
db = client.get_database("chatapp") 

def get_db() -> Database:
    """Dependency to provide the database instance."""
    return db

def close_db():
    """Close current database connection."""
    client.close()