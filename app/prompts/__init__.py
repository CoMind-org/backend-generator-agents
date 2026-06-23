from typing import Optional

from app.prompts.planner_prompt import planner_prompt
from app.prompts.orchestrator_prompt import orchestrator_prompt


def get_prompt(agent: str, user_prompt: Optional[str] = None, previous_plan: Optional[str] = None, feedback: Optional[str] = None) -> str:
    if agent == "planner":
        return planner_prompt(user_prompt, previous_plan, feedback)

    if agent == "orchestrator":
        return orchestrator_prompt(previous_plan)

    raise ValueError(f"Invalid agent type: {agent}")
