import asyncio  # Asynchronous processing
import logging  # Logging support
from typing import Dict, List, Any, Optional, Callable  # Type hints
from datetime import datetime  # Timestamp handling
from dataclasses import dataclass  # Lightweight data structures
from abc import ABC, abstractmethod  # For defining abstract classes


# -------------------------------
# Data structure representing agent capabilities
# -------------------------------
@dataclass
class AgentCapability:
    name: str  # Capability name (e.g., "math", "calendar")
    description: str  # What this capability does
    input_types: List[str]  # Types of inputs accepted
    output_types: List[str]  # Types of outputs produced
    methods: List[str]  # Supported method names (e.g., process, info)
    version: str = "1.0.0"
    can_call_agents: Optional[List[str]] = None  # Other agent IDs it can invoke


# -------------------------------
# MCPMessage defines how messages are exchanged between agents
# -------------------------------
@dataclass
class MCPMessage:
    id: str  # Unique message ID
    method: str  # Method the agent should run (e.g., "process")
    params: Dict[str, Any]  # Parameters passed to the method
    timestamp: datetime  # When the message was created
    sender: Optional[str] = None  # Who sent the message
    target: Optional[str] = None  # Who should process it


# -------------------------------
# Base agent class for all agents to inherit
# -------------------------------
class BaseMCPAgent(ABC):
    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id  # Unique agent identifier
        self.name = name  # Human-readable agent name
        self.capabilities = capabilities  # List of declared capabilities
        self.logger = self._setup_logging()  # Setup logger
        self.message_handlers: Dict[str, Callable] = {}  # Maps method names to handler functions
        self.agent_registry: Optional[Dict[str, 'BaseMCPAgent']] = None  # Registry of all available agents
        self._register_handlers()  # Automatically hook up handle_* methods
        self.logger.info(f"Initialized agent: {self.agent_id} ({self.name})")

    def _setup_logging(self) -> logging.Logger:
        # Initializes logger for this agent
        logger = logging.getLogger(f"agent.{self.agent_id}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.agent_id} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _register_handlers(self):
        # Registers all handler methods like handle_process, handle_info
        for capability in self.capabilities:
            for method in capability.methods:
                handler_name = f"handle_{method}"
                if hasattr(self, handler_name):
                    self.message_handlers[method] = getattr(self, handler_name)

    # -------------------------------
    # MAIN ENTRY POINT: Input → Processing → Output
    # -------------------------------
    async def process_message(self, message: MCPMessage) -> Dict[str, Any]:
        """Main message processing logic:
        Takes input (message.method + params) → calls corresponding handler → returns output
        """
        try:
            self.logger.info(f"Processing message: {message.method}")

            # 🔍 Input: Method to invoke
            if message.method in self.message_handlers:
                handler = self.message_handlers[message.method]

                # ⚙️ Process: Call handler with parameters
                result = await handler(message)

                # 🧾 Output: Add metadata like processed_by and timestamp
                if isinstance(result, dict):
                    result["processed_by"] = self.agent_id
                    result["processed_at"] = datetime.now().isoformat()

                return result

            else:
                # ❌ Method not found
                return {
                    "status": "error",
                    "message": f"Unknown method: {message.method}",
                    "available_methods": list(self.message_handlers.keys()),
                    "agent": self.agent_id
                }

        except Exception as e:
            self.logger.error(f"Error processing message {message.method}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.agent_id
            }

    # -------------------------------
    # Inter-agent communication
    # -------------------------------
    async def call_agent(self, agent_id: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Allows one agent to call another agent’s method."""
        try:
            # 🔍 Input: Target agent ID and method
            if not self.agent_registry:
                raise Exception("Agent registry not available")
            if agent_id not in self.agent_registry:
                raise Exception(f"Agent {agent_id} not found in registry")

            target_agent = self.agent_registry[agent_id]

            # Create a synthetic message
            message = MCPMessage(
                id=f"{self.agent_id}_{datetime.now().timestamp()}",
                method=method,
                params=params,
                timestamp=datetime.now(),
                sender=self.agent_id,
                target=agent_id
            )

            self.logger.info(f"Calling agent {agent_id}.{method}")

            # ⚙️ Process: Send message to target agent
            return await target_agent.process_message(message)

        except Exception as e:
            self.logger.error(f"Error calling agent {agent_id}.{method}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.agent_id
            }

    # -------------------------------
    # Register other agents to enable inter-agent calls
    # -------------------------------
    def set_agent_registry(self, registry: Dict[str, 'BaseMCPAgent']):
        self.agent_registry = registry
        self.logger.info(f"Agent registry set with {len(registry)} agents")

    def get_capabilities(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": cap.name,
                "description": cap.description,
                "input_types": cap.input_types,
                "output_types": cap.output_types,
                "methods": cap.methods,
                "can_call_agents": cap.can_call_agents or []
            }
            for cap in self.capabilities
        ]

    def get_info(self) -> Dict[str, Any]:
        """Returns agent's metadata for introspection"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "capabilities": self.get_capabilities(),
            "available_methods": list(self.message_handlers.keys()),
            "can_call_agents": [
                agent for cap in self.capabilities
                for agent in (cap.can_call_agents or [])
            ]
        }

    # -------------------------------
    # Utility logging functions
    # -------------------------------
    def log_info(self, message: str): self.logger.info(message)
    def log_warning(self, message: str): self.logger.warning(message)
    def log_error(self, message: str): self.logger.error(message)
    def log_debug(self, message: str): self.logger.debug(message)

    # -------------------------------
    # Abstract method that agents must implement
    # -------------------------------
    @abstractmethod
    async def handle_process(self, message: MCPMessage) -> Dict[str, Any]:
        pass

    def __str__(self) -> str:
        return f"MCPAgent({self.agent_id}: {self.name})"

    def __repr__(self) -> str:
        return f"MCPAgent(id='{self.agent_id}', name='{self.name}', capabilities={len(self.capabilities)})"


# -------------------------------
# Minimal example agent for demo/testing
# -------------------------------
class SimpleMCPAgent(BaseMCPAgent):
    def __init__(self, agent_id: str, name: str, description: str = ""):
        capabilities = [
            AgentCapability(
                name="basic_processing",
                description=description or f"Basic processing for {name}",
                input_types=["text", "dict"],
                output_types=["text", "dict"],
                methods=["process", "info"]
            )
        ]
        super().__init__(agent_id, name, capabilities)

    async def handle_process(self, message: MCPMessage) -> Dict[str, Any]:
        # Simple echo-like behavior
        return {
            "status": "success",
            "message": f"Processed by {self.name}",
            "params": message.params,
            "agent": self.agent_id
        }

    async def handle_info(self, message: MCPMessage) -> Dict[str, Any]:
        return {
            "status": "success",
            "info": self.get_info(),
            "agent": self.agent_id
        }


# -------------------------------
# Utility functions for testing
# -------------------------------
def create_simple_agent(agent_id: str, name: str, description: str = "") -> SimpleMCPAgent:
    return SimpleMCPAgent(agent_id, name, description)


def create_message(method: str, params: Dict[str, Any], sender: str = None) -> MCPMessage:
    return MCPMessage(
        id=f"msg_{datetime.now().timestamp()}",
        method=method,
        params=params,
        timestamp=datetime.now(),
        sender=sender
    )


# -------------------------------
# Main test block for debugging and validation
# -------------------------------
if __name__ == "__main__":
    print("🤖 Testing Base MCP Agent")
    print("=" * 40)

    agent = create_simple_agent("test_agent", "Test Agent", "A simple test agent")
    print(f"Created agent: {agent}")
    print(f"Capabilities: {agent.get_capabilities()}")
    print(f"Methods: {list(agent.message_handlers.keys())}")

    async def test_agent():
        # 👇 Input
        message = create_message("process", {"test": "data"}, "test_sender")

        # ⚙️ Process
        result = await agent.process_message(message)

        # 🧾 Output
        print(f"Process result: {result}")

        info_message = create_message("info", {}, "test_sender")
        info_result = await agent.process_message(info_message)
        print(f"Info result: {info_result}")

    asyncio.run(test_agent())  # Run the async test

    print("\n✅ Base MCP Agent working correctly!")
    print("🎯 Ready for agent development!")
