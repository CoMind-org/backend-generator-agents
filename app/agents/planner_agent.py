from app.schemas.plan import Plan
from app.prompts import get_prompt
from app.schemas.agent_status import AgentState
from app.models import get_model

class PlannerAgent:
    def __init__(self):
        self.model = get_model("openai")

    def agent(self, state: AgentState) -> dict:
        user_prompt = state["user_prompt"]

        prompt_content = get_prompt(
            agent="planner",
            user_prompt=user_prompt,
        )

        plan = self.model.generate(
            user_prompt=prompt_content,
            system_prompt=(
                "You are a strict backend project planning assistant. "
                "Return only a structured response that matches the provided schema."
            ),
            response_schema=Plan,
        )

        return {"plan": plan}