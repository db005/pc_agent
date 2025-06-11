from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["desktop_ai"]

users_collection = db["users"]
sessions_collection = db["sessions"]
