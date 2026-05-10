#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: claude_code_like.py
Author: Codex
Date: 2026-05-10
Version: 1.0.0
Description: 主模块，仅保留系统提示词和程序入口。
"""

from methods import run_cli


SYSTEM_PROMPT = """You are a concise coding assistant running in a terminal.
Use tools when they help.
Prefer reading files before editing them.
Keep answers short and practical.
Current working directory is the project root.
"""


# ------------------------------------------------------------
# 主程序入口
# ------------------------------------------------------------
def main() -> None:
    """
    启动命令行对话程序。

    Args:
        None

    Returns:
        None
    """
    run_cli(system_prompt=SYSTEM_PROMPT)


if __name__ == "__main__":
    main()
