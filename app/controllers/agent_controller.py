from fastapi import APIRouter

from app.services.agent_service import AgentService
from app.schemas.plan import PlanRequest
from app.schemas.orchestrator_tasks import PlanWithOrchestration

router = APIRouter()
agent_service = AgentService()


@router.get("/server-connection")
def health_check():
    return {"message": "OK"}


@router.post("/create/plan", response_model=PlanWithOrchestration)
async def create_plan(payload: PlanRequest):
    return await agent_service.start_plan(payload)
