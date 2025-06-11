import json
import asyncio
import websockets
import time
from GPTPlanner import GPTPlanner
from UserControl import register, login, users_collection
from SystemPromptManager import save_system_prompt
planner = GPTPlanner()
from database import sessions_collection  # 假设你从 database.py 中导入
from bson.objectid import ObjectId

async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        action = data.get("action")

        if action == "register":
            email = data["email"]
            password = data["password"]
            result = await register(email, password)
            await websocket.send(json.dumps(result))
        
        elif action == "login":
            email = data["email"]
            password = data["password"]
            result = await login(email, password)
            await websocket.send(json.dumps(result))
        
        elif action == "plan":
            token_id = data.get("token_id")
            session_id = data.get("session_id")
            user = await users_collection.find_one({"token_id": token_id})
            if not user:
                await websocket.send(json.dumps({"success": False, "msg": "Invalid token_id"}))
                continue

            goal = data["goal"]
            screenshot_b64 = data["screenshot"]
            success = False

            # 获取历史对话（如果有）
            session = await sessions_collection.find_one({"_id": ObjectId(session_id)})
            history = session.get("history", []) if session else []

            # 获取规划动作
            actions = await planner.plan(goal, screenshot_b64, history)

            for action in actions:
                if isinstance(action, dict) and "success" in action:
                    success = action["success"]
                    break

            # 更新数据库中的对话记录
            new_entry = {
                "goal": goal,
                "screenshot_b64": screenshot_b64,
                "actions": actions,
                "success": success,
                "timestamp": time.time()
            }

            if session:
                await sessions_collection.update_one(
                    {"_id": ObjectId(session_id)},
                    {"$push": {"history": new_entry}}
                )
            else:
                session_doc = {
                    "_id": ObjectId(session_id),
                    "user_id": user["_id"],
                    "history": [new_entry],
                    "created_at": time.time()
                }
                await sessions_collection.insert_one(session_doc)

            await websocket.send(json.dumps({
                "actions": actions,
                "success": success
            }))
        
        elif action == "save_system_prompt":
            token_id = data.get("token_id")
            user = await users_collection.find_one({"token_id": token_id})
            if not user:
                await websocket.send(json.dumps({"success": False, "msg": "Invalid token_id"}))
                return

            agent_id = data.get("agent_id", "default")  # 如果你有多个 agent，可传入标识
            prompt_text = data.get("prompt")
            result = await save_system_prompt(user["_id"], agent_id, prompt_text)
            await websocket.send(json.dumps(result))                                        

        else:
            await websocket.send(json.dumps({"success": False, "msg": "Invalid action"}))

async def main():
    async with websockets.serve(handler, "localhost", 8765, max_size=50 * 1024 * 1024):
        print("🚀 WebSocket 服务器已启动，等待客户端连接...")
        await asyncio.Future()

asyncio.run(main())
# 运行 WebSocket 服务器，等待客户端连接并处理请求