# integration/mcp_bridge.py
from fastapi import FastAPI
from pydantic import BaseModel
from registry.agent_registry import AGENT_REGISTRY

app = FastAPI()

class TaskPayload(BaseModel):
    agent: str
    input: str

@app.post("/handle_task")
async def handle_task_request(payload: TaskPayload):
    agent_name = payload.agent
    input_text = payload.input

    agent = AGENT_REGISTRY.get(agent_name)
    if agent:
        result = agent.run(input_text)
        return {"status": "success", "agent_output": result}
    else:
        return {"status": "error", "message": f"Agent '{agent_name}' not found."}

# Document this API using FastAPI's automatic Swagger UI