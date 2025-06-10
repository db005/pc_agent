import json
import time
import traceback
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 确保你已设置 `OPENAI_API_KEY`

class GPTPlanner:
    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    def extract_json_list(self, raw_content: str):
        try:
            start = raw_content.index('[')
            end = raw_content.rindex(']')
        except ValueError:
            traceback.print_exc()
            return None

        json_str = raw_content[start:end+1]
        print("📦 Extracted JSON string:", repr(json_str))
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            traceback.print_exc()
            return None

    async def plan(self, goal, screenshot_b64):
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
        while True:
            try:
                response = client.chat.completions.create(
                    model="gpt-4-vision-preview",  # 或 gpt-4-0125-preview 等
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
                    max_tokens=1024
                )

                # 统计 token
                usage = response.usage
                if usage:
                    self.total_prompt_tokens += usage.prompt_tokens
                    self.total_completion_tokens += usage.completion_tokens
                    print(f"📊 Prompt tokens: {usage.prompt_tokens}, Completion tokens: {usage.completion_tokens}")
                    print(f"📈 Total so far: prompt={self.total_prompt_tokens}, completion={self.total_completion_tokens}")

                content = response.choices[0].message.content
                actions = self.extract_json_list(content)

                if isinstance(actions, list) and all(isinstance(item, dict) for item in actions):
                    return actions
                else:
                    print("⚠️ GPT 响应结构不正确，重试中…")
            except Exception as e:
                print("⚠️ 解析或调用 GPT 失败，重试中… 错误信息：", e)

            time.sleep(1)
