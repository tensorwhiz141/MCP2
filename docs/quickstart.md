*How to run the repo in the development mode?*
1.Clone the repository
git clone https://github.com/<your-username>/blackhole_core_mcp.git
cd blackhole_core_mcp

2.Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

3.Install required dependencies
pip install -r requirements.txt

4.Create a .env file in the root directory
MONGODB_URI=mongodb://localhost:27017
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
TIMEZONE=Asia/Kolkata


*Example usage of using an agent*
Example:Calendar Agent
python blackhole_core/agents/calendar_agent.py

*Where to add new agents?*
blackhole_core/agents/

To create a new agent:

Create a new file in blackhole_core/agents/, e.g. my_custom_agent.py

Inherit from BaseMCPAgent

Define capabilities and handler methods like handle_process, handle_info, etc.

Register the agent using create_agent() or get_agent_info() at the bottom of the file.

Use base_agent.py as a blueprint for standardization



*How Agents are called by the MCP?*
The Multi-Agent Control Protocol (MCP) enables agents to communicate with each other using standardized messages.
How Calls Work:
Each agent defines message_handlers mapped to methods like process, send_email, etc.The BaseMCPAgent handles routing internally:


await agent.process_message(message)
If agent_registry is set, agents can call other agents via:


await self.call_agent("calendar_agent", "process", {"query": "..."})
This allows for building pipelines, multi-agent workflows, and chained reasoning across agents.

