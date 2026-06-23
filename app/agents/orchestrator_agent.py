from app.schemas.orchestrator_tasks import Plan, OrchestratorTasks
from app.prompts import get_prompt
from app.schemas.agent_status import AgentState
from app.models import get_model

class OrchestratorAgent:
    def __init__(self):
        self.model = get_model("openai")

    def agent(self, state: AgentState) -> dict:
        plan = state.get("plan")

        if plan is None:
            raise ValueError("Planner output is missing. Cannot run orchestrator.")

        if not isinstance(plan, Plan):
            plan = Plan.model_validate(plan)

        plan_json = plan.model_dump_json(indent=2)

        prompt_content = get_prompt(
            agent="orchestrator",
            previous_plan=plan_json,
        )

        orchestrator_tasks = self.model.generate(
            user_prompt=prompt_content,
            system_prompt=(
                "You are a strict orchestration assistant. "
                "Return only a structured response that matches the provided schema."
            ),
            response_schema=OrchestratorTasks,
        )

        return {"orchestrator_tasks": orchestrator_tasks}
