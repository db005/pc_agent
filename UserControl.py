import uuid
import bcrypt
import motor.motor_asyncio

# 连接 MongoDB
mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
db = mongo_client.desktop_ai
users_collection = db.users

async def register(email, password):
    user = await users_collection.find_one({"email": email})
    if user:
        return {"success": False, "msg": "Email already registered."}
    
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    token_id = str(uuid.uuid4())

    await users_collection.insert_one({
        "email": email,
        "password_hash": password_hash,
        "token_id": token_id,
    })

    return {"success": True, "token_id": token_id}

async def login(email, password):
    user = await users_collection.find_one({"email": email})
    if not user:
        return {"success": False, "msg": "User not found."}
    
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return {"success": True, "token_id": user["token_id"]}
    else:
        return {"success": False, "msg": "Incorrect password."}
