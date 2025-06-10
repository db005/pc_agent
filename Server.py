import json
import asyncio
import websockets
from GPTPlanner import GPTPlanner
from UserControl import register, login, users_collection

planner = GPTPlanner()

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
            user = await users_collection.find_one({"token_id": token_id})
            if not user:
                await websocket.send(json.dumps({"success": False, "msg": "Invalid token_id"}))
                continue

            goal = data["goal"]
            screenshot_b64 = data["screenshot"]
            success = False

            actions = await planner.plan(goal, screenshot_b64)
            for action in actions:
                if not isinstance(action, dict) or "type" not in action:
                    if "success" in action:
                        success = action["success"]
                        break

            await websocket.send(json.dumps({
                "actions": actions,
                "success": success
            }))

        else:
            await websocket.send(json.dumps({"success": False, "msg": "Invalid action"}))

async def main():
    async with websockets.serve(handler, "localhost", 8765, max_size=50 * 1024 * 1024):
        print("🚀 WebSocket 服务器已启动，等待客户端连接...")
        await asyncio.Future()

asyncio.run(main())
# 运行 WebSocket 服务器，等待客户端连接并处理请求