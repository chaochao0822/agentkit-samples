# 绘本故事视频生成 Agent

## 项目概述

本项目提供一个基于火山引擎 AgentKit 的“成语绘本故事视频生成”Agent。它会根据用户输入的成语故事情节：

- 生成四张卡通风格的分镜插画
- 以相邻分镜为首尾帧生成三段过渡视频
- 通过本地 MCP 工具将三段视频顺序拼接为完整成片
- 上传成片到火山引擎 TOS，并返回可访问的签名 URL

核心组件：
- Agent 服务：`agent.py`，基于 `AgentkitSimpleApp`
- 工具集：图片生成、视频生成、文件下载、视频拼接（MCP）、TOS 上传
- 短期记忆：用于维持对话会话上下文

## 目录结构

```
video-gen/
├── agent.py         # Agent 应用入口，注册 MCP 工具并运行
├── agent.yaml       # Agent 配置：模型、系统指令与工具列表
├── tool/            # 自定义工具
│   ├── file_download.py  # 批量下载文件到本地
│   └── tos_upload.py     # 上传文件到 TOS 并生成签名 URL
├── requirements.txt # Python 依赖列表
└── .dockerignore    # Docker 构建忽略文件
```

## 快速开始

### 1. 安装依赖

```bash
cd 02-use-cases/video-gen
uv pip install -r requirements.txt
```

额外要求：
- 安装 Node.js 与 npm（用于运行本地 MCP 视频拼接工具）
- 确保本机可使用 `npx`（Node.js 18+ 推荐）

### 2. 准备视频剪辑 MCP 工具

本项目已在 `agent.py` 中集成 MCP 工具，运行时将通过 `npx @pickstar-2002/video-clip-mcp@latest` 启动，无需手动安装。

### 3. 配置环境变量

本地必需的环境变量（用于 TOS 上传）：

```bash
export VOLCENGINE_ACCESS_KEY=AK
export VOLCENGINE_SECRET_KEY=SK
# 可选：指定下载目录（不设置则默认使用项目根目录）
export DOWNLOAD_DIR=/path/to/downloads
```

TOS 存储桶说明：
- 默认使用 `tool/tos_upload.py` 中的 `bucket_name="agentkit-platform-{{your account_id}}"`
- 如需自定义，可在调用工具时传入 `bucket_name`，或直接修改 `tool/tos_upload.py` 的默认参数为你的 Bucket 名称

### 4. 启动与部署

以本地方式运行（调试）：

```bash
python agent.py
# 服务默认监听 0.0.0.0:8000
```

部署到火山引擎 AgentKit（runtime）：

```bash
agentkit config \
--agent_name video_gen \
--entry_point 'agent.py' \
--runtime_envs DATABASE_TOS_BUCKET=agentkit-platform-{{your account_id}} \ # example: agentkit-platform-12345678901234567890
--launch_type cloud && \
#--iam-role <your iam role>\
agentkit launch
```

## 使用与测试

通过 AgentKit 调用示例：
- Prompt：后移射日，嫦娥奔月，吴刚伐木真人版
- Prompt: 愚公移山与精卫填海绘本故事
- Prompt: 射雕英雄传的真人版视频故事
- Prompt: 凡人修仙传韩立结婴
- Prompt: 凡人修仙传虚天殿大战，3D动漫风格


```bash
agentkit invoke '{"prompt": "请根据寓言《狐假虎威》生成绘本故事视频"}'
```

期望行为：
- 自动生成 4 张分镜插画，并基于相邻分镜生成 3 段过渡视频
- 启动本地 MCP 工具拼接为完整视频
- 通过 TOS 上传生成签名 URL，并将该 URL 作为最终响应返回

## 常见问题

- `npx` 不可用或 Node 环境缺失：请安装 Node.js（推荐 18+）与 npm，确保命令行可执行 `npx`。
- TOS 上传失败：确认已设置 `VOLCENGINE_ACCESS_KEY` 与 `VOLCENGINE_SECRET_KEY`，并保证账户拥有目标 Bucket 的访问权限。
- 使用环境变量来指定Bucket DATABASE_TOS_BUCKET="agentkit-platform-{{account_id}}"

## 参考

- `agent.yaml` 的工作流程定义了从分镜生成到视频拼接与上传的完整链路