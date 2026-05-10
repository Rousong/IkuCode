#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: methods.py
Author: Codex
Date: 2026-05-10
Version: 1.0.0
Description: 封装环境加载、模型调用与命令行对话流程。
"""

import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from tools import TOOL_FUNCS, TOOLS


ROOT = Path(__file__).resolve().parent


# ------------------------------------------------------------
# 加载本地环境变量
# ------------------------------------------------------------
def load_local_env(env_path: str = ".env") -> None:
    """
    从项目根目录的 .env 文件加载环境变量。

    Args:
        env_path: 相对于项目根目录的 .env 文件路径。

    Returns:
        None
    """
    target = ROOT / env_path
    if not target.exists():
        return

    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


# ------------------------------------------------------------
# 创建客户端
# ------------------------------------------------------------
def build_client() -> OpenAI:
    """
    创建 DeepSeek OpenAI 兼容客户端。

    Args:
        None

    Returns:
        已初始化的 OpenAI 客户端实例。
    """
    load_local_env()
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY is required in .env")

    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )


# ------------------------------------------------------------
# 调用模型
# ------------------------------------------------------------
def call_model(client: OpenAI, messages: list[dict[str, Any]]) -> Any:
    """
    发送当前对话历史到 DeepSeek 模型。

    Args:
        client: 已初始化的 OpenAI 客户端。
        messages: 完整对话历史消息。

    Returns:
        模型返回的原始响应对象。
    """
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")
    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )


# ------------------------------------------------------------
# 处理工具调用
# ------------------------------------------------------------
def handle_tool_calls(message: Any) -> list[dict[str, Any]]:
    """
    执行模型发起的工具调用，并转换为 tool 消息。

    Args:
        message: 单次模型返回的消息对象。

    Returns:
        回填给模型的 tool 消息列表。
    """
    outputs: list[dict[str, Any]] = []
    for tool_call in message.tool_calls or []:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments or "{}")
        func = TOOL_FUNCS[name]
        try:
            result = func(**args)
        except Exception as exc:
            result = f"tool error: {exc}"

        print(f"[tool] {name}({args})")
        outputs.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )
    return outputs


# ------------------------------------------------------------
# 完成单轮对话
# ------------------------------------------------------------
def chat_once(client: OpenAI, messages: list[dict[str, Any]]) -> str:
    """
    执行一次用户输入对应的完整模型交互，包含可能的工具调用。

    Args:
        client: 已初始化的 OpenAI 客户端。
        messages: 当前会话的完整消息列表。

    Returns:
        本轮最终返回给用户的文本答案。
    """
    while True:
        response = call_model(client, messages)
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if message.tool_calls:
            messages.extend(handle_tool_calls(message))
            continue

        return message.content or ""


# ------------------------------------------------------------
# 运行命令行界面
# ------------------------------------------------------------
def run_cli(system_prompt: str) -> None:
    """
    运行交互式命令行对话循环。

    Args:
        system_prompt: 会话初始使用的系统提示词。

    Returns:
        None
    """
    client = build_client()
    messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    print("Claude Code Like")
    print("Commands: /clear /history /exit")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not user_input:
            continue
        if user_input == "/exit":
            print("bye")
            break
        if user_input == "/clear":
            messages = [{"role": "system", "content": system_prompt}]
            print("history cleared")
            continue
        if user_input == "/history":
            print(f"messages={len(messages)}")
            continue

        messages.append({"role": "user", "content": user_input})
        answer = chat_once(client, messages)
        print(answer)
