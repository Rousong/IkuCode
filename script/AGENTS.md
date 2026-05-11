# AGENTS.md

如果修改此目录里面的代码文件，那么请同步更新此 MD 文档。

<!-- USER-SUBDIRECTORY-RULES:START -->
<!-- 用户自定义的子目录规则写在这里；如果这里除了本注释外没有任何内容，则忽略本区块。 -->
<!-- USER-SUBDIRECTORY-RULES:END -->

## 代码简介

此目录存放项目 hook 使用的本地脚本，目前包含用于在 macOS 和 Windows 下播放 `voice` 目录 MP3 音频的脚本。

## 目录结构

```text
script/ # 存放 hook 调用的本地辅助脚本。
├── AGENTS.md # 子目录协作说明文档，记录此目录约束、代码简介和结构。
├── play_voice_macos.sh # macOS 音频播放脚本，使用 afplay 播放 voice 目录中的 MP3。
└── play_voice_windows.ps1 # Windows 音频播放脚本，使用系统 MCI 接口播放 voice 目录中的 MP3。
```
