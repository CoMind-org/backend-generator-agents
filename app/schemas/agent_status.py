from typing import TypedDict, Optional
from app.schemas.plan import Plan
from app.schemas.orchestrator_tasks import OrchestratorTasks

class AgentState(TypedDict, total=False):
    user_prompt: str
    plan: Optional[Plan]
    orchestrator_tasks: Optional[OrchestratorTasks]
