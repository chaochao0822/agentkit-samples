# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging

from agentkit.apps import AgentkitAgentServerApp, AgentkitSimpleApp
from google.adk.agents import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.genai.types import Content, Part
from tools import get_url_of_frontend_code_in_tos, upload_frontend_code_to_tos
from veadk import Agent, Runner
from veadk.memory import ShortTermMemory
from veadk.tools.builtin_tools.run_code import run_code
from veadk.tracing.telemetry.exporters.apmplus_exporter import APMPlusExporter
from veadk.tracing.telemetry.opentelemetry_tracer import OpentelemetryTracer

logger = logging.getLogger(__name__)

app = AgentkitSimpleApp()
short_term_memory = ShortTermMemory(backend="local")

tracer = OpentelemetryTracer(exporters=[APMPlusExporter()])

code_agent = Agent(
    description="A coding agent that helps users write code",
    instruction='''
    你是一位经验丰富的软件开发工程师，能够将用户的需求转化为功能完善的代码。
    # 你的技能
    - 你的任务是根据用户的需求，编写符合要求的代码。 
    - 你擅长多种编程语言，包括但不限于 Python、Java、JavaScript、Go 等。
    - 你还具备良好的代码质量控制习惯，能够确保代码的质量和可维护性。
    # 其他要求
    - 你必须严格遵守用户的需求，不偏离用户的意图。
    - 你在编写代码时，必须考虑代码的可读性和可维护性，避免使用复杂的、晦涩的代码。
    - 如果用户没有指定编程语言，你默认使用 Python。
    ''',
    short_term_memory=short_term_memory
)

agent = Agent(
    description="An AI coding agent that helps users solve programming problems",
    instruction='''
    你是一位专业、精准且高效的 AI 编程助手，专注于帮助用户解决各类编程语言及场景下的编程问题。
    你的核心使命是提供正确、优化且可落地的编程解决方案，关键能力是可使用代码执行功能，验证你提供的代码或用户现有代码的运行正确性。
    
    为了更好的用户体验，如果是前端代码，你需要将代码上传到TOS，并返回该代码的访问URL。
    其他情况下，你只需要返回代码字符串即可。
    ''',
    tools=[run_code, upload_frontend_code_to_tos, get_url_of_frontend_code_in_tos],
    sub_agents=[code_agent],
    tracers=[tracer],
    short_term_memory=short_term_memory,
)

app_name = "ai_coding_agent"
runner = Runner(app_name=app_name, agent=agent, short_term_memory=short_term_memory)

agent_server_app = AgentkitAgentServerApp(agent=agent, short_term_memory=short_term_memory)
@app.entrypoint
async def run(payload: dict, headers: dict) -> str:
    prompt = payload["prompt"]
    user_id = headers["user_id"]
    session_id = headers["session_id"]

    logger.info(
        f"Running agent with prompt: {prompt}, user_id: {user_id}, session_id: {session_id}"
    )
    
    await runner.short_term_memory.create_session (
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    
    # 流式输出
    new_message = Content(role="user", parts=[Part(text=prompt)])
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
        ):
            # Format as SSE data
            sse_event = event.model_dump_json(exclude_none=True, by_alias=True)
            logger.debug("Generated event in agent run streaming: %s", sse_event)
            yield f"data: {sse_event}\n\n"
    except Exception as e:
        logger.exception("Error in event_generator: %s", e)
        # You might want to yield an error event here
        yield f'data: {{"error": "{str(e)}"}}\n\n'


@app.ping
def ping() -> str:
    return "pong!"


if __name__ == "__main__":
    agent_server_app.run(host="0.0.0.0", port=8000)
