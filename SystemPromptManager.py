from motor.motor_asyncio import AsyncIOMotorClient
import os
import uuid
import datetime

# MongoDB 连接
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(mongo_uri)
db = client["desktop_ai"]
prompts_collection = db["system_prompts"]

async def save_system_prompt(user_id: str, agent_id: str, prompt_text: str):
    prompt_entry = {
        "prompt_id": str(uuid.uuid4()),
        "user_id": user_id,
        "agent_id": agent_id,
        "prompt": prompt_text,
        "timestamp": datetime.datetime.utcnow()
    }
    result = await prompts_collection.insert_one(prompt_entry)
    return {"success": True, "prompt_id": prompt_entry["prompt_id"]}
