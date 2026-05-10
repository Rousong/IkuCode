# Claude Code Like

一个尽量简单的终端对话程序，使用 DeepSeek API，支持：

- 多轮对话
- 基本 tool use
- `uv` 管理依赖和运行

## 1. 准备 `.env`

在项目根目录创建或修改本地 `.env` 文件：

```env
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

## 2. 安装并运行

```bash
uv sync
uv run ccdeep
```

也可以直接：

```bash
uv run python claude_code_like.py
```

程序启动时会自动读取项目根目录下的 `.env`。

## 3. 内置命令

- `/exit` 退出
- `/clear` 清空当前会话历史
- `/history` 查看当前消息条数

## 4. 内置工具

- `list_files(path=".")`
- `read_file(path)`
- `write_file(path, content)`
- `run_command(command)`

所有路径都限制在当前项目目录内，`run_command` 默认超时 30 秒。
