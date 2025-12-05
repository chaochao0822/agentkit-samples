# 客服智能体（Customer Support Agent）

## 项目概述

本项目基于火山引擎 AgentKit 构建“客户咨询与售后服务”智能体，支持导购咨询与售后处理两类场景。系统整合知识库与CRM工具，结合短期/长期记忆与身份校验，面向真实客服流程提供高效、准确、隐私安全的服务能力。

核心组件：
- Agent 服务：`agent.py`，基于 `AgentkitAgentServerApp` 运行 HTTP 服务
- 工具集：客户信息、购买记录、保修查询、维修单增删改查（`tools/crm_mock.py`）
- 知识库：首次运行自动将 `pre_build/knowledge/` 导入 Viking 向量库
- 记忆：短期记忆（本地），长期记忆（Viking 或可选 Mem0）

核心价值：
- 统一客服入口：自动判别“导购/售后”意图并路由至对应子智能体
- 快速问题定位：结合知识库与工具检索，规范化输出，提升一次解决率
- 可扩展与低耦合：工具与知识独立，可替换为真实 CRM 或更多业务接口

## 目录结构

```
customer_support/
├── agent.py                 # Agent 应用入口，注册工具与子智能体，运行服务
├── tools/
│   └── crm_mock.py         # CRM 模拟工具：客户、购买、保修、维修单增删改查
├── pre_build/
│   └── knowledge/          # 知识库文件（首次运行导入 Viking）
│       ├── policies.md             # 退换货与保修策略
│       ├── shopping_guide.md       # 商品导购知识
│       └── troubleshooting_for_phone.md  # 手机故障排查
│       └── troubleshooting_for_tv.md  # 电视故障排查
├── requirements.txt        # Python 依赖
├── README.zh.md               # 项目说明文档
└── .dockerignore
```

## 快速开始

### 1. 安装依赖

注意： 请使用 python3.12+以上版本。

```bash
cd 02-use-cases/customer_support
uv pip install -r requirements.txt
# 或
pip3 install -r requirements.txt
```

### 2. 配置环境变量

本地必需：

```bash
export VOLCENGINE_ACCESS_KEY=AK
export VOLCENGINE_SECRET_KEY=SK
export DATABASE_TOS_BUCKET=agentkit-platform-{{your account_id}}
# 可选：使用已有知识库索引时指定（否则首次运行自动导入）
export DATABASE_VIKING_COLLECTION=<existing_knowledge_index>
# 可选：长期记忆（二选一）
export DATABASE_VIKINGMEM_COLLECTION=<mem_index>
export DATABASE_VIKINGMEM_MEMORY_TYPE=<memory_type>
# 或使用 Mem0
export DATABASE_MEM0_BASE_URL=<mem0_base_url>
export DATABASE_MEM0_API_KEY=<mem0_api_key>
```

说明：
- 若未设置 `DATABASE_VIKING_COLLECTION`，首次运行会将 `pre_build/knowledge` 自动上传至 TOS 并导入 Viking 向量库，需设置 `DATABASE_TOS_BUCKET`。
- 模型名称默认 `deepseek-v3-1-terminus`，如需更改可在代码中调整。

### 3. 启动与部署

#### 本地调试

本地可以使用 veadk web 进行调试

```bash
# 1. 进入 customer_support 的上级目录
cd 02-use-cases

# 2. [可选] 创建配置配置 .env 文件，如果 步骤2 已经配置了环境变量，这里可以跳过
touch .env
# 配置 .env 文件, 
echo "VOLCENGINE_ACCESS_KEY=AK" >> .env
echo "VOLCENGINE_SECRET_KEY=SK" >> .env
# 知识库配置， 建议本地调试，可以在 agentkit 手动创建知识库， 并设置 DATABASE_VIKING_COLLECTION 为知识库索引
echo "DATABASE_VIKING_COLLECTION=agentkit_customer_support" >> .env
# 可选：如果未设置已有知识库，agent会自动创建知识库并做初始化导入， 这一步需要设置 DATABASE_TOS_BUCKET， 主要上传知识库内容并导入
echo "DATABASE_TOS_BUCKET=agentkit-platform-{{your account_id}}" >> .env

# 3.启动 veadk web 调试
veadk web 
```

veadk web 默认会监听 8000 端口， 服务启动后，你可以在浏览器中访问 `http://127.0.0.1:8000`， agent 选择 `customer_support`， 即可在 web 右侧的输入框中输入问题， 并查看智能体的回复。 


#### 部署到火山引擎 AgentKit（runtime）：

使用 agentkit 部署到火山引擎。

```bash
# 1. 进入到 customer_support 目录
cd 02-use-cases/customer_support

# 2. 配置 agentkit
agentkit config \
--agent_name customer_support \
--entry_point 'agent.py' \
--runtime_envs DATABASE_TOS_BUCKET=agentkit-platform-{{your account_id}} \
--launch_type cloud

# 3. 部署到 runtime 
agentkit launch
```

发布成功后，可以登录火山引擎 AgentKit 控制台，点击 Runtime 查看部署的智能体。

## 使用与测试

示例 Prompt：
- 售后场景：你好，我之前买的一个电视坏了
- 售后场景：我的邮箱是 zhang.ming@example.com，电视序列号 SN20240001
- 导购场景：我想买一款客厅用的智能电视，用来打游戏用的，预算 3000 元以内

期望行为：
- 自动识别“导购/售后”意图并路由至对应子智能体
- 基于工具与知识库返回规范化答案，必要时引导校验身份、查询购买与保修信息
- 创建/更新/删除维修单需获得用户明确同意且信息完整

## 常见问题

- 首次运行报错 `DATABASE_TOS_BUCKET not set`：需设置用于知识导入的 TOS Bucket 名称。
- 未设置 `DATABASE_VIKING_COLLECTION`：会触发自动导入，确保 TOS 配置正确且具备权限。
- 默认用户 `CUST001`：示例数据绑定该客户；生产环境建议在请求头中传 `user_id` 并接入真实身份系统。
- 替换为真实 CRM：可将 `tools/crm_mock.py` 替换为真实 API 封装，接口保持“查询/增删改”语义一致。

