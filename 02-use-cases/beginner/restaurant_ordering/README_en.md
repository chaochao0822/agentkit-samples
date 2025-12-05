# Restaurant Ordering Agent (`restaurant_ordering`)

This project demonstrates an advanced Agent designed to be a friendly and efficient restaurant ordering assistant, showcasing several core capabilities of the Agent Development Kit (ADK).

## Core Features

The Agent's main goal is to help users order food from a predefined menu. It can:

-   **Receive Orders**: Understand user requests (e.g., "I want some spicy dishes") and match them to menu items.
-   **Add to Order**: Use the `add_to_order` tool to add specific dishes to the user's shopping cart.
-   **Summarize Order**: Use the `summarize_order` tool to display the final list of dishes before checkout.
-   **Handle Off-Menu Requests**: When the user wants a dish not on the menu, the Agent uses the `web_search` tool to search the internet and confirms with the user if it should be placed as a special order.

## Special Capabilities and Advanced Features

This Agent goes beyond basic conversations and demonstrates several powerful advanced features:

### 1. Asynchronous Tools and Parallel Invocation

To improve response efficiency, tools in this project (such as `add_to_order`) are defined as asynchronous functions (`async def`). More importantly, the Agent's core instruction explicitly encourages the model to **invoke these tools in parallel** when needed.

> **Prompt Instruction**: `You can use parallel invocations to add multiple dishes to the order.`

This means when a user says "I want Gong Bao Chicken and a plate of dumplings", the Agent can simultaneously initiate two `add_to_order` tool calls, significantly speeding up processing.

### 2. Advanced Context Management and Compression

To maintain efficiency and reduce costs in long conversations, this project uses two advanced context management techniques:

-   **Event Compaction (`EventsCompactionConfig`)**: This is a highlight of the project. By configuring `EventsCompactionConfig`, the Agent can automatically "compress" multi-turn conversation history into a concise summary. This avoids passing the complete, lengthy conversation history with each request, greatly saving token count.
    > **Code Comment**: `events_compaction_config is used to configure event compaction to save context in long conversations.`
-   **Context Filter (`ContextFilterPlugin`)**: As a complement, the `ContextFilterPlugin` plugin is used to precisely control the number of recent conversation turns to retain (e.g., the last 8 turns), ensuring core context is not lost.

### 3. State Management Using `ToolContext`

The Agent can continuously maintain the user's order status across multiple turns of conversation. It achieves this by using the `tool_context.state` dictionary, which is a persistent state passed and shared between tool calls.

-   The `add_to_order` tool adds new dishes to a list located at `tool_context.state["order"]`.
-   The `summarize_order` tool reads data from this shared state to provide a complete order summary.

### 4. Custom Plugin (`CountInvocationPlugin`)

This project includes a custom plugin `CountInvocationPlugin` that is mounted to the Agent's lifecycle to real-time count the number of Agent runs and underlying Large Language Model (LLM) invocations.

This demonstrates how to use the plugin mechanism to monitor the Agent's internal behavior, record logs, or inject custom logic, providing powerful support for Agent observability.

## Usage
### 1. Install veadk and agentkit Python SDKs and configure environment variables

```bash
uv pip install veadk-python
uv pip install agentkit-sdk-python
```

### 2. Run local command line test
```bash
python main.py
```

### 3. Run veadk web client and login via browser at http://127.0.0.1:8000
```bash
cd ..
veadk web

```

### 4. Deploy to vefaas
> **Security Note: Do not disable key authentication in production environments. Ensure `VEFAAS_ENABLE_KEY_AUTH` remains `true` (or not set, which is enabled by default), and properly configure access keys and roles. Only temporarily disable authentication in local controlled environments for debugging purposes, and always include a warning.**

```bash
cd restaurant_ordering
# This step can be run directly
export VEFAAS_ENABLE_KEY_AUTH=false
# Replace YOUR_AK with your own ak
export VOLCENGINE_ACCESS_KEY=YOUR_AK
# Replace YOUR_SK with your own sk
export VOLCENGINE_SECRET_KEY=YOUR_SK
# This step deploys the application to the cloud
veadk deploy --vefaas-app-name=order-agent --use-adk-web --veapig-instance-name=<your veapig instance name> --iam-role "trn:iam::<your account id>:role/<your iam role name>"

```

### 5. Deploy to AgentKit and test with client.py

```bash
cd restaurant_ordering
# Uncomment the following line in agent.py to run the agentkit app server
# agent_server_app.run(host="0.0.0.0", port=8000)
agentkit config
agentkit launch
```