from pymongo import MongoClient
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# client = MongoClient("mongodb+srv://dasunthathsara974_db_user:IHhMkJKDhnaqDnA6@cluster0.vbanwih.mongodb.net/?appName=Cluster0")

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://dasunthathsara974_db_user:IHhMkJKDhnaqDnA6@cluster0.vbanwih.mongodb.net/?appName=Cluster0"
)
client = AsyncIOMotorClient(MONGO_URI)

db = client.comind_db
plans_collection = db["plan"]
