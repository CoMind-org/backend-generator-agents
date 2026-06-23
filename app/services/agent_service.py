from datetime import datetime, timezone

from fastapi import HTTPException
from langgraph.graph import END, StateGraph

from app.agents.planner_agent import PlannerAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.repositories.plan_repository import PlanRepository
from app.schemas.agent_status import AgentState
from app.schemas.plan import (
    Plan,
    PlanRequest,
    PlanDetails,
)

from app.schemas.orchestrator_tasks import (
    OrchestratorTasks,
    PlanWithOrchestration,
)


class AgentService:
    def __init__(self):
        self.planner = PlannerAgent()
        self.orchestrator = OrchestratorAgent()
        self.plan_repository = PlanRepository()
        self.app_agent = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("planner", self.planner.agent)
        workflow.add_node("orchestrator", self.orchestrator.agent)

        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "orchestrator")
        workflow.add_edge("orchestrator", END)

        return workflow.compile()

    async def start_plan(self, payload: PlanRequest) -> PlanWithOrchestration:
        try:
            result = self.app_agent.invoke(
                {
                    "user_prompt": payload.user_prompt,
                }
            )

            plan = result.get("plan")
            orchestrator_tasks = result.get("orchestrator_tasks")

            if plan is None:
                raise HTTPException(
                    status_code=500,
                    detail="Planner did not return a valid plan.",
                )

            if orchestrator_tasks is None:
                raise HTTPException(
                    status_code=500,
                    detail="Orchestrator did not return valid tasks.",
                )

            if not isinstance(plan, Plan):
                plan = Plan.model_validate(plan)

            if not isinstance(orchestrator_tasks, OrchestratorTasks):
                orchestrator_tasks = OrchestratorTasks.model_validate(orchestrator_tasks)

            now = datetime.now(timezone.utc).isoformat()

            plan_details = PlanDetails(
                user_prompt=payload.user_prompt,
                current_plan=plan,
                plan_history=[],
                status=1,
                refined_count=0,
                created_at=now,
                updated_at=now,
            )

            await self.plan_repository.insert_one(plan_details)

            return PlanWithOrchestration(
                plan=plan,
                orchestratorTasks=orchestrator_tasks,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
