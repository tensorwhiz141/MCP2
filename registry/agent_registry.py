# In a real scenario, you would import the actual agent classes
# For now, let's use placeholder classes or mock objects

class ArchiveSearchAgent:
    def run(self, input_text):
        return f"ArchiveSearchAgent processed: {input_text}"

class LiveDataAgent:
    def run(self, input_text):
        return f"LiveDataAgent processed: {input_text}"

class VisionAgent: # Stub
    def run(self, input_text):
        return f"VisionAgent stub processed: {input_text}"

class QueryAgent: # Stub
    def run(self, input_text):
        return f"QueryAgent stub processed: {input_text}"

AGENT_REGISTRY = {
    "ArchiveSearchAgent": ArchiveSearchAgent(),
    "LiveDataAgent": LiveDataAgent(),
    "VisionAgent": VisionAgent(), # stub
    "QueryAgent": QueryAgent(),  # stub
}