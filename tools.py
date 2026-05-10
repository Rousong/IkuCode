#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: tools.py
Author: Codex
Date: 2026-05-10
Version: 1.0.0
Description: 定义本地工具及其元数据。
"""

import subprocess
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent


# ------------------------------------------------------------
# 校验项目内路径
# ------------------------------------------------------------
def ensure_in_root(path_text: str) -> Path:
    """
    将相对路径解析为项目内绝对路径，并阻止越界访问。

    Args:
        path_text: 用户传入的相对路径字符串。

    Returns:
        解析后的绝对路径对象。
    """
    path = (ROOT / path_text).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("path must stay inside the project root") from exc
    return path


# ------------------------------------------------------------
# 列出文件
# ------------------------------------------------------------
def list_files(path: str = ".") -> str:
    """
    列出项目目录内指定路径下的文件或子目录。

    Args:
        path: 相对于项目根目录的路径，默认当前目录。

    Returns:
        目录项列表文本；如果目标是文件，则返回该文件相对路径。
    """
    target = ensure_in_root(path)
    if not target.exists():
        raise FileNotFoundError(f"{path} does not exist")
    if target.is_file():
        return str(target.relative_to(ROOT))

    names = []
    for child in sorted(target.iterdir(), key=lambda item: item.name):
        suffix = "/" if child.is_dir() else ""
        names.append(f"{child.relative_to(ROOT)}{suffix}")
    return "\n".join(names) or "(empty directory)"


# ------------------------------------------------------------
# 读取文件
# ------------------------------------------------------------
def read_file(path: str) -> str:
    """
    读取项目目录内的 UTF-8 文本文件。

    Args:
        path: 相对于项目根目录的文件路径。

    Returns:
        文件文本内容。
    """
    target = ensure_in_root(path)
    return target.read_text(encoding="utf-8")


# ------------------------------------------------------------
# 写入文件
# ------------------------------------------------------------
def write_file(path: str, content: str) -> str:
    """
    将 UTF-8 文本写入项目目录内文件。

    Args:
        path: 相对于项目根目录的文件路径。
        content: 需要写入的文本内容。

    Returns:
        描述写入结果的文本。
    """
    target = ensure_in_root(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"wrote {target.relative_to(ROOT)}"


# ------------------------------------------------------------
# 执行命令
# ------------------------------------------------------------
def run_command(command: str) -> str:
    """
    在项目根目录执行 shell 命令，并返回输出。

    Args:
        command: 需要执行的 shell 命令字符串。

    Returns:
        命令退出码与输出内容；超时时返回错误信息。
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "tool error: command timed out after 30 seconds"

    output = (result.stdout + result.stderr).strip()
    if not output:
        output = "(no output)"
    return f"exit_code={result.returncode}\n{output}"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files under a path relative to the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file relative to the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write UTF-8 text to a file relative to the project root.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command in the project root and return stdout and stderr.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                },
                "required": ["command"],
            },
        },
    },
]

TOOL_FUNCS: dict[str, Callable[..., str]] = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}
