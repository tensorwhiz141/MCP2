import importlib.util
import os
from pathlib import Path

def discover_agents():
    agents = {}
    for path in Path("agents").rglob("*_agent.py"):
        try:
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
