from typing import Any, Dict, Optional

import json
import aiohttp
from pydantic import BaseModel
from stagehand.llm.client import LLMClient  # 继承项目现有的 LLMClient 基类
from stagehand.metrics import start_inference_timer, get_inference_time_ms


class HybridDict(dict):
    def __init__(self, data: dict):
        super().__init__(data)
        # 递归处理嵌套字典（如 usage、choices 里的内容）
        for k, v in data.items():
            if isinstance(v, dict):
                self[k] = HybridDict(v)
            elif isinstance(v, list):
                # 处理列表中的字典（如 choices 数组）
                self[k] = [HybridDict(item) if isinstance(item, dict) else item for item in v]

    # 支持属性访问（如 self.usage → self['usage']）
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'HybridDict' object has no attribute '{name}'")

    # 支持属性赋值（可选）
    def __setattr__(self, name, value):
        self[name] = value


class QwenClient(LLMClient):
    def __init__(self, stagehand_logger, api_key: str, model_name: str = "qwen-turbo", **kwargs):
        # 调用父类构造函数，符合现有 LLMClient 的初始化方式
        super().__init__(
            stagehand_logger=stagehand_logger,
            api_key=api_key,
            default_model=model_name, **kwargs
        )
        self.api_key = api_key
        self.api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    async def create_response(
            self,
            *,
            messages: list[dict[str, str]],
            model: Optional[str] = None,
            function_name: Optional[str] = None,
            **kwargs: Any,
    ) -> dict[str, Any]:
        # 1. 基础参数校验
        model = model or self.default_model
        if not model:
            raise ValueError("未指定模型名称")

        # 2. 构建请求头（修复：自定义 headers，而非引用 litellm 模块）
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 3. 处理 response_format + 自动追加 JSON 格式提示
        response_format = kwargs.get("response_format")
        # 深拷贝 messages，避免修改原始数据（关键！）
        processed_messages = [msg.copy() for msg in messages]

        # 仅当指定 response_format 时，追加 JSON 格式要求
        if response_format:
            json_format_prompt = """
                你是浏览器自动化的元素识别助手，需基于 Accessibility Tree（语义化节点树）返回符合要求的可操作元素，规则如下：

                ### 输入说明
                1. Accessibility Tree 包含节点格式：[节点ID] 角色: 标签（如 [4] textbox: 请输入账号）；
                2. 目标操作是用户的自然语言指令（如「在请输入账号输入框中输入内容」）。

                ### 返回规则
                1. 仅返回合法 JSON 字符串，无任何多余文字/解释/代码块；
                2. 顶层为字典，仅包含 "elements" 键（值为数组）；
                3. 数组内每个元素必须包含以下字段：
                   - element_id：Accessibility Tree 中的原始数字 ID（如 [4] 中的 4，整数类型，用于定位元素）；
                   - description：元素的描述（结合角色和标签，如「textbox: 请输入账号」）；
                   - method：Playwright 支持的操作方法（如 textbox/textarea 用 "fill"，button/link 用 "click"）；
                   - arguments：必须是list数组结构，操作的参数列表list,即使只有一个元素也应该用数组嵌套，没有元素时填入一个空字符串''。

                ### 返回格式示例
                {
                  "elements": [
                    {
                      "element_id": 4,
                      "description": "textbox: 请输入账号",
                      "method": "fill",
                      "arguments": ["15211228071"]
                    }
                  ]
                }

                ### 强制要求
                1. 仅返回上述格式的 JSON，无其他内容；
                2. element_id 必须是 Accessibility Tree 中的原始数字，不允许自定义；
                3. 若未找到匹配元素，返回 {"elements": []}；
                4. 若用户指令是动作（如输入/点击），优先返回最匹配的单个元素；若为观察（如"找到所有按钮"），返回所有符合条件的元素。
            """
            has_system_msg = False

            # 遍历 messages，在已有 system 消息后追加提示
            for msg in processed_messages:
                if msg["role"] == "system":
                    msg["content"] += json_format_prompt
                    has_system_msg = True
                    break

            # 若无 system 消息，新增一条（保证 JSON 提示存在）
            if not has_system_msg:
                processed_messages.insert(0, {
                    "role": "system",
                    "content": f"你是一个专业的助手{json_format_prompt}"
                })

        # 4. 初始化请求体（使用处理后的 messages）
        payload = {
            "model": model,
            "messages": processed_messages,  # 用追加提示后的 messages
            "temperature": kwargs.get("temperature", 0.1),
            "max_tokens": kwargs.get("max_tokens", 1024),
            "top_p": kwargs.get("top_p", 0.9),
        }

        # 5. 处理 response_format 格式转换（原有逻辑不变）
        if response_format:
            # 场景1：传入的是 Pydantic 模型（比如 ObserveInferenceSchema）
            if isinstance(response_format, type) and issubclass(response_format, BaseModel):
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_format.__name__,
                        "strict": True,
                        "schema": response_format.model_json_schema(),
                    }
                }
            # 场景2：传入的是 json_schema 格式（但 strict 为 false）
            elif isinstance(response_format, dict) and response_format.get("type") == "json_schema":
                response_format["json_schema"]["strict"] = True
                payload["response_format"] = response_format
            # 场景3：传入的是 json_object（通用兼容）
            elif isinstance(response_format, dict) and response_format.get("type") == "json_object":
                payload["response_format"] = response_format
            # 其他情况：兜底为 json_object
            else:
                payload["response_format"] = {"type": "json_object"}

        # 6. 发送请求
        start_time = start_inference_timer()
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_base, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise ValueError(f"通义千问 API 错误: {await response.text()}")
                response_data = await response.json()

        # 7. 解析 JSON 响应（原有逻辑不变）
        if response_format:
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if content:
                try:
                    parsed_content = json.loads(content)
                    # ========== 核心适配逻辑 ==========
                    # 遍历 elements 数组，强制转换 arguments 为列表
                    if isinstance(parsed_content, dict) and "elements" in parsed_content:
                        elements = parsed_content["elements"]
                        if isinstance(elements, list):
                            for elem in elements:
                                # 1. 如果 arguments 字段不存在 → 初始化为空列表
                                if "arguments" not in elem:
                                    elem["arguments"] = []
                                else:
                                    # 2. 如果 arguments 是 None → 替换为空列表
                                    if elem["arguments"] is None:
                                        elem["arguments"] = []
                                    # 3. 如果 arguments 是非列表类型（字符串/数字/布尔等）→ 包装为列表
                                    elif not isinstance(elem["arguments"], list):
                                        # 额外处理：如果值是 None，包装为包含空字符串的列表（按需可选）
                                        elem["arguments"] = [elem["arguments"] if elem["arguments"] is not None else ""]
                    # ========== 适配结束 ==========
                    response_data["choices"][0]["message"]["content"] = parsed_content
                except json.JSONDecodeError as e:
                    raise ValueError(f"千问模型返回非 JSON 内容：{content} | 错误：{str(e)}")

        # 8. 调用指标回调（关键修改：包装响应为对象）
        inference_time_ms = get_inference_time_ms(start_time)
        if self.metrics_callback and function_name:
            response_obj = HybridDict(response_data)
            self.metrics_callback(response_obj, inference_time_ms, function_name)

        return HybridDict(response_data)