from openai import OpenAI
import asyncio
import websockets
import json, time
import traceback
import os
# 确保设置了 OPENAI_API_KEY 环境变量
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def plan_with_gpt(goal, screenshot_b64):

    prompt = f"""
你是一个桌面自动化大师。你可以通过键盘与鼠标来控制电脑。用户的目标是：「{goal}」。

现在请你规划一下如何达成这个目标。请根据当前屏幕截图和之前的尝试来决定下一步的动作。

你可以使用以下几种动作类型：
- 移动鼠标：{{"type": "move", "x": 0.1, "y": 0.2}}
- 点击鼠标：{{"type": "click", "x": 0.3, "y": 0.2}}
- 键盘输入：{{"type": "type", "text": "Hello World"}}
- 按下键：{{"type": "keypress", "key": "enter"}}

请根据情况选择合适的动作，并**仅输出 JSON 数组**，其中数字为以整个屏幕的长或宽为1的相对坐标。例如：

[
  {{ "type": "move", "x": 0.2, "y": 0.3 }},
  {{ "type": "click", "x": 0.5, "y": 0.6 }},
  {{ "type": "type", "text": "Hello World" }},
  {{ "type": "keypress", "key": "enter" }},
  {{ "success": true }}  # 如果目标已达成，否则为 false
]
"""

    def extract_json_list(raw_content: str):
        """
        从 raw_content 中提取最外层的 JSON 数组并返回解析后的 Python 列表。
        如果提取或解析失败，则返回 None。
        """
        try:
            start = raw_content.index('[')
            end = raw_content.rindex(']')
        except ValueError:
            # 没有找到合法的方括号
            traceback.print_exc()
            return None

        json_str = raw_content[start:end+1]
        print("Extracted JSON string:", repr(json_str))
        # 尝试解析 JSON 字符串
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            traceback.print_exc()
            # JSON 格式不合法
            return None

    while True:
        try:
            response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "你是一个自动桌面控制助手"},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{screenshot_b64}",
                            },
                        },
                    ],
                }
            ],
            max_completion_tokens=32768
        )
            content = response.choices[0].message.content
            
            actions = extract_json_list(content)
            # actions = json.loads(content)
            if isinstance(actions, list) and all(isinstance(item, dict) for item in actions):
                return actions
            else:
                print("⚠️ GPT 响应结构不正确，重试中…")
        except Exception as e:
            print("⚠️ 解析或调用 GPT 失败，重试中… 错误信息：", e)
            # print(content)
        time.sleep(1)


async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        goal = data["goal"]
        screenshot_b64 = data["screenshot"]
        history = data.get("history", [])
        success = False

        # 假设客户端来判断是否达成目标，这里仅返回规划
        actions = await plan_with_gpt(goal, screenshot_b64, history)
        for action in actions:
            if not isinstance(action, dict) or "type" not in action:
                if "success" in action:
                    success = action["success"]
                    break
        await websocket.send(json.dumps({
            "actions": actions, 
            "success": success
        }))

async def main():
    async with websockets.serve(handler, "localhost", 8765, max_size=50 * 1024 * 1024):
        print("🚀 WebSocket 服务器已启动，等待客户端连接...")
        await asyncio.Future()  # run forever

asyncio.run(main())
