import asyncio
import websockets
import base64
from io import BytesIO
import json
import pyautogui
import time
from PIL import ImageGrab

# 截图并编码为 base64
def capture_screen_base64():
    screenshot = ImageGrab.grab()
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    b64_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return b64_str

# 执行动作
def execute_actions(actions):
    screen_width, screen_height = pyautogui.size()
    for action in actions:
        if not isinstance(action, dict) or "type" not in action:
            print(f"⚠️ 无效动作被跳过: {action}")
            continue
        if action["type"] == "move":
            x = int(action["x"] * screen_width)
            y = int(action["y"] * screen_height)
            pyautogui.moveTo(x, y)
        elif action["type"] == "click":
            x = int(action["x"] * screen_width)
            y = int(action["y"] * screen_height)
            pyautogui.click(x, y)
        elif action["type"] == "type":
            pyautogui.write(action["text"])
        elif action["type"] == "keypress":
            pyautogui.press(action["key"])
        time.sleep(1)

# 注册用户
async def register_user(ws, email, password):
    payload = {
        "action": "register",
        "email": email,
        "password": password
    }
    await ws.send(json.dumps(payload))
    response = await ws.recv()
    return json.loads(response)

# 登录用户
async def login_user(ws, email, password):
    payload = {
        "action": "login",
        "email": email,
        "password": password
    }
    await ws.send(json.dumps(payload))
    response = await ws.recv()
    return json.loads(response)

# 主逻辑
async def send_goal_and_act(goal, email, password):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri, ping_interval=300, ping_timeout=300) as ws:
        # 登录或注册
        login_result = await login_user(ws, email, password)
        if not login_result.get("success"):
            print("🔐 登录失败，尝试注册...")
            register_result = await register_user(ws, email, password)
            if not register_result.get("success"):
                print("❌ 注册也失败了:", register_result.get("msg"))
                return
            token_id = register_result["token_id"]
            print("✅ 注册成功，token_id:", token_id)
        else:
            token_id = login_result["token_id"]
            print("✅ 登录成功，token_id:", token_id)

        # 发送任务目标并执行动作
        success = False
        history = []

        while not success:
            screenshot_b64 = capture_screen_base64()
            payload = {
                "action": "plan",
                "token_id": token_id,
                "goal": goal,
                "screenshot": screenshot_b64
            }
            await ws.send(json.dumps(payload))
            print("🎯 发送目标，等待服务端规划...")

            response = await ws.recv()
            data = json.loads(response)
            actions = data.get("actions", [])
            success = data.get("success", False)

            if success:
                print("✅ 目标达成！")
                return

            print("🛠️ 接收到动作，开始执行...")
            execute_actions(actions)

            history.append({
                "goal": goal,
                "actions": actions,
                "success": success
            })

            if not success:
                print("❌ 尚未达成目标，继续尝试...\n")
                time.sleep(1)
            else:
                print("✅ 目标达成！")

async def write_slave_prompt(email, password, agent_id, title, prompt_text):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri, ping_interval=300, ping_timeout=300) as ws:
        # 登录
        await ws.send(json.dumps({
            "action": "login",
            "email": email,
            "password": password
        }))
        response = await ws.recv()
        login_data = json.loads(response)

        if not login_data.get("success"):
            print("❌ 登录失败，无法保存提示词")
            return

        token_id = login_data["token_id"]

        # 保存提示词
        await ws.send(json.dumps({
            "action": "save_system_prompt",
            "token_id": token_id,
            "agent_id": agent_id,
            "title": title,
            "prompt": prompt_text
        }))
        result = await ws.recv()
        result_data = json.loads(result)

        if result_data.get("success"):
            print(f"✅ 系统提示词已保存 (prompt_id={result_data['prompt_id']})")
        else:
            print("❌ 保存提示词失败:", result_data.get("msg"))

async def search_prompts(email, password, query, agent_id=None):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri, ping_interval=300, ping_timeout=300) as ws:
        # 登录
        await ws.send(json.dumps({
            "action": "login",
            "email": email,
            "password": password
        }))
        response = await ws.recv()
        login_data = json.loads(response)

        if not login_data.get("success"):
            print("❌ 登录失败，无法搜索提示词")
            return

        token_id = login_data["token_id"]

        # 搜索提示词
        await ws.send(json.dumps({
            "action": "search_system_prompts",
            "token_id": token_id,
            "query": query,
            "agent_id": agent_id  # 可传 None 搜索所有 agent
        }))

        result = await ws.recv()
        result_data = json.loads(result)

        if result_data.get("success"):
            print("✅ 搜索结果：")
            for item in result_data["results"]:
                print(f"Agent: {item['agent_id']} | 标题: {item['title']}")
                print(f"Prompt: {item['prompt'][:100]}...\n")
        else:
            print("❌ 搜索失败:", result_data.get("msg"))


# 示例运行
if __name__ == "__main__":
    time.sleep(3)
    # 示例：写入从 agent 的提示词
    asyncio.run(write_slave_prompt(
        email="297347023@qq.com",
        password="Bluedata259",
        agent_id="slave_agent_1",
        title="网页搜索助手",
        prompt_text="你是一个网页搜索助手，善于通过视觉图像和文字目标规划鼠标点击与打字。"
    ))
    asyncio.run(search_prompts(
        email="297347023@qq.com",
        password="Bluedata259",
        query="网页 搜索助手"
    ))
    asyncio.run(send_goal_and_act(
        '''打开浏览器，访问 https://www.bing.com/，搜索 "OpenAI 最新消息"，并点击第一个结果。''',
        email="297347023@qq.com",
        password="Bluedata259"
    ))
