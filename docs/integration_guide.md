Integration Guide for Blackhole Core
This document outlines how to integrate new components and understand the existing integration points within the Blackhole Core, focusing on agents, the MCP Bridge, and the Nipun Adapter. The core goal is to enable a plug-and-play hub where multiple agents and LLMs can register, respond to tasks dynamically, and connect to any future Gurukul component.

1. Agent Integration (Agent Registry + Dynamic Routing)
The Blackhole Core uses an Agent Registry to manage available agents and dynamically route tasks to them.


Agent Registry Location: registry/agent_registry.py.



Registry Format: A Python dictionary named AGENT_REGISTRY where keys are agent names (strings) and values are instantiated agent objects

# registry/agent_registry.py
from agents.archive_search_agent import ArchiveSearchAgent # Assuming this is the path
from agents.live_data_agent import LiveDataAgent # Assuming this is the path
from agents.vision_agent import VisionAgent # Stubbed [cite: 25]
from agents.query_agent import QueryAgent # Stubbed [cite: 67]

AGENT_REGISTRY = {
    "ArchiveSearchAgent": ArchiveSearchAgent(), [cite: 63]
    "LiveDataAgent": LiveDataAgent(), [cite: 64]
    "VisionAgent": VisionAgent(), # stub [cite: 65]
    "QueryAgent": QueryAgent(),  # stub [cite: 66, 67]
}

Dynamic Routing: The mcp_bridge.py loads agents from this registry dynamically. When a task request is received, it extracts the 

agent_name and input_text from the payload, retrieves the corresponding agent from AGENT_REGISTRY, and executes its run() method.



How to Add a New Agent:


Create Agent Class: In the agents/ folder, create a new Python file (e.g., 

my_new_agent.py). Define your agent class, ensuring it has a run(self, input_text) method that encapsulates its specific logic. It's recommended to inherit from a 

base_agent.py if a common interface is defined there.

Instantiate and Register:

Import your new agent class into registry/agent_registry.py.

Add an instance of your agent class to the AGENT_REGISTRY dictionary with a unique string key (e.g., "MyNewAgent").

# registry/agent_registry.py
from agents.my_new_agent import MyNewAgent # Assuming you created this file

AGENT_REGISTRY = {
    # ... existing agents
    "MyNewAgent": MyNewAgent(),
}
Your new agent will now be dynamically available via the MCP Bridge.

2. MCP Bridge (FastAPI)
The MCP Bridge, located at 

integration/mcp_bridge.py, serves as the primary external interface for receiving task requests. It is implemented using FastAPI, providing a robust and automatically documented API.


API Endpoint: The primary endpoint for task requests is typically /handle_task (or similar POST endpoint).


Request Payload: The bridge expects a JSON payload with at least agent (the name of the agent to route to, matching a key in 

AGENT_REGISTRY) and 

input  (the text input for the agent).

{
  "agent": "ArchiveSearchAgent",
  "input": "Find all documents related to the Q3 2024 financial review."
}
3. Nipun Adapter
The 

integration/nipun_adapter.py module is responsible for transforming the output of an agent into a format compatible with the Nipun Learning Object standard.



Core Function: map_agent_output_to_nipun(agent_output). This function takes the raw output from an agent and processes it into the required Nipun format.



API Contract / Expected Format: The specific JSON schema for the Nipun Learning Object needs to be explicitly documented  within 

nipun_adapter.py or in this guide.


Example Nipun Learning Object (Conceptual):
{
  "nipun_object_type": "learning_material",
  "title": "Summary of Q3 2024 Financial Review",
  "description": "Key takeaways and insights from the Q3 2024 financial performance.",
  "content_html": "<p>...</p>",
  "tags": ["finance", "Q3", "2024"],
  "source_system": "Blackhole_Core",
  "original_agent_output": { /* full original agent output */ }
}


How to Update Nipun Mapping:

Modify the 

map_agent_output_to_nipun function in integration/nipun_adapter.py  to handle new types of agent outputs or changes in the Nipun Learning Object specification. Ensure the transformation logic is robust and handles various data structures returned by agents.

This guide provides a comprehensive overview of the integration points, ensuring clarity for future development and maintenance.