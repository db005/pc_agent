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

    async def plan(self, goal, screenshot_b64, history=None):
    # 转换历史记录为 OpenAI 格式的 messages
        history_messages = []
        if history:
            for h in history[-5:]:  # 最多保留 5 轮对话
                goal_text = f"用户的目标是：「{h['goal']}」。"
                result_text = f"助手给出的动作是：{json.dumps(h['actions'], ensure_ascii=False)}，是否成功：{h['success']}"
                history_messages.append({"role": "user", "content": goal_text})
                history_messages.append({"role": "assistant", "content": result_text})

        # 当前轮对话的 prompt
        user_prompt = f"""
    用户的目标是：「{goal}」。

    现在请你根据上面的对话历史和当前屏幕截图规划下一步的动作。你可以使用以下几种动作类型：
    - 移动鼠标：{{"type": "move", "x": 0.1, "y": 0.2}}
    - 点击鼠标：{{"type": "click", "x": 0.3, "y": 0.2}}
    - 键盘输入：{{"type": "type", "text": "Hello World"}}
    - 按下键：{{"type": "keypress", "key": "enter"}}

    请只输出 JSON 数组，例如：
    [
    {{ "type": "move", "x": 0.2, "y": 0.3 }},
    {{ "type": "click", "x": 0.5, "y": 0.6 }},
    {{ "type": "type", "text": "Hello World" }},
    {{ "type": "keypress", "key": "enter" }},
    {{ "success": true }}
    ]
    """

        while True:
            try:
                messages = [{"role": "system", "content": "你是一个自动桌面控制助手"}]
                messages.extend(history_messages)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{screenshot_b64}",
                            },
                        }
                    ]
                })

                response = client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=messages,
                    max_tokens=1024
                )

                # Token usage 统计
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
                print("⚠️ GPT 调用失败，重试中… 错误信息：", e)
            time.sleep(1)
