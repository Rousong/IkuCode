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
import shutil
from getpass import getuser
from pathlib import Path
from typing import Any

from openai import OpenAI

from tools import TOOL_FUNCS, TOOLS


ROOT = Path(__file__).resolve().parent
APP_TITLE = "IKU-Code"
APP_VERSION = "v0.1.0"
COMMAND_HELP = "Commands: /help /clear /history /exit"


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
# 获取模型名
# ------------------------------------------------------------
def get_model_name() -> str:
    """
    获取当前配置的模型名称。

    Args:
        None

    Returns:
        当前使用的模型名称。
    """
    return os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")


# ------------------------------------------------------------
# 获取展示路径
# ------------------------------------------------------------
def get_display_path() -> str:
    """
    获取适合在终端展示的项目路径。

    Args:
        None

    Returns:
        使用波浪线缩写后的项目路径字符串。
    """
    root_text = str(ROOT)
    home_text = str(Path.home())
    if root_text.startswith(home_text):
        return root_text.replace(home_text, "~", 1)
    return root_text


# ------------------------------------------------------------
# 截断文本
# ------------------------------------------------------------
def clip_text(text: str, width: int) -> str:
    """
    根据给定宽度截断文本。

    Args:
        text: 原始文本。
        width: 允许显示的最大宽度。

    Returns:
        截断后的文本；宽度不足时返回省略形式。
    """
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return f"{text[:width - 1]}…"


# ------------------------------------------------------------
# 构建内容行
# ------------------------------------------------------------
def format_line(text: str, width: int, align: str = "left") -> str:
    """
    按指定宽度和对齐方式格式化单行文本。

    Args:
        text: 需要展示的文本。
        width: 内容区域宽度。
        align: 对齐方式，支持 left 或 center。

    Returns:
        固定宽度的文本行。
    """
    clipped = clip_text(text, width)
    if align == "center":
        return clipped.center(width)
    return clipped.ljust(width)


# ------------------------------------------------------------
# 渲染欢迎横幅
# ------------------------------------------------------------
def render_banner() -> str:
    """
    生成类似 Claude Code 风格的启动欢迎横幅。

    Args:
        None

    Returns:
        渲染完成的多行横幅字符串。
    """
    terminal_width = shutil.get_terminal_size(fallback=(120, 40)).columns
    inner_width = max(78, min(terminal_width - 2, 118))
    separator = "│"
    gutter = "  "
    column_width = (inner_width - len(gutter) - 2) // 2
    left_width = column_width
    right_width = inner_width - len(gutter) - 2 - left_width

    username = getuser()
    model_name = get_model_name()
    left_lines = [
        "",
        f"Welcome back {username}!",
        "",
        "▐▛███▜▌",
        "▝▜█████▛▘",
        "  ▘▘ ▝▝",
        "",
        f"{model_name} · Tool Use Enabled",
        f"· {username}'s Local Workspace",
        get_display_path(),
    ]
    right_lines = [
        "Tips for getting started",
        "Run /help to see available commands",
        "Run /clear to reset the current chat history",
        "",
        "What's new",
        "Simple Claude-like terminal welcome screen",
        "DeepSeek multi-turn chat with tool use",
        "Local .env configuration support",
        "",
        "Type your prompt below to begin",
    ]

    line_count = max(len(left_lines), len(right_lines))
    while len(left_lines) < line_count:
        left_lines.append("")
    while len(right_lines) < line_count:
        right_lines.append("")

    title = f" {APP_TITLE} {APP_VERSION} "
    top = f"╭{title}{'─' * max(0, inner_width - len(title))}╮"
    bottom = f"╰{'─' * inner_width}╯"

    body_lines = []
    for left_text, right_text in zip(left_lines, right_lines):
        left_align = "center"
        if left_text.startswith(model_name) or left_text.startswith("· ") or left_text.startswith("~") or left_text.startswith("/"):
            left_align = "left"

        body = (
            f"{separator}"
            f"{format_line(left_text, left_width, align=left_align)}"
            f"{gutter}"
            f"{format_line(right_text, right_width)}"
            f"{separator}"
        )
        body_lines.append(body)

    return "\n".join([top, *body_lines, bottom])


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
    return client.chat.completions.create(
        model=get_model_name(),
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
    load_local_env()
    client = build_client()
    messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    print(render_banner())
    print(COMMAND_HELP)

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
        if user_input == "/help":
            print(COMMAND_HELP)
            continue
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
