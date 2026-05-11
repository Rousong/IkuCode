# AGENTS.md

如果修改此目录里面的代码文件，那么请同步更新此 MD 文档。

<!-- USER-SUBDIRECTORY-RULES:START -->
<!-- 用户自定义的子目录规则写在这里；如果这里除了本注释外没有任何内容，则忽略本区块。 -->
<!-- USER-SUBDIRECTORY-RULES:END -->

## 代码简介

此目录存放 hook 播放用的 MP3 音频资源，用于会话开始、权限确认和任务结束等事件提示。

## 目录结构

```text
voice/ # 存放 hook 事件提示音频资源。
├── AGENTS.md # 子目录协作说明文档，记录此目录约束、资源简介和结构。
├── MissionComplete1.mp3 # 任务完成提示音频。
├── MissionComplete2.mp3 # 备用任务完成提示音频。
├── NeedConfirm1.mp3 # 权限确认提示音频。
├── NeedConfirm2.mp3 # 备用权限确认提示音频。
└── StartTask.mp3 # 会话开始提示音频。
```
