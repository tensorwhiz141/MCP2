"""
MCP Agents Package
Production agents for the Model Context Protocol system
"""

# Production agents auto-discovery
from .live.weather_agent import RealTimeWeatherAgent  # ensure this path matches your structure

PRODUCTION_AGENTS = [
    "weather_agent",
    "math_agent", 
    "calendar_agent",
    "real_gmail_agent",
    "document_processor"
]

def get_production_agents():
    """Get list of production agent names."""
    return PRODUCTION_AGENTS

def is_production_agent(agent_name):
    """Check if an agent is a production agent."""
    return agent_name in PRODUCTION_AGENTS

def discover_agents():
    agents = {}
    for path in Path("agents").rglob("*_agent.py"):
        try:
            # ↓ MUST contain get_agent_info and create_agent
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "get_agent_info") and hasattr(module, "create_agent"):
                info = module.get_agent_info()
                agent_id = info.get("id", path.stem)
                info["path"] = str(path)
                agents[agent_id] = info
        except Exception as e:
            print(f"⚠️ Failed to discover {path}: {e}")
    return agents


