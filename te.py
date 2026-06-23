import os
from typing import Optional, TypedDict, Type, TypeVar

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from langgraph.graph import END, StateGraph

from app.prompts import get_prompt
from app.schemas.plan import Plan, OrchestratorTasks, PlanWithOrchestration
from app.core.config import Settings

router = APIRouter()
settings = Settings()


GITHUB_TOKEN = settings.github_token
GITHUB_MODELS_ENDPOINT = settings.github_endpoint
GITHUB_MODEL = settings.github_model

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is missing. Add GITHUB_TOKEN to your .env file.")

client = OpenAI(
    base_url=GITHUB_MODELS_ENDPOINT,
    api_key=GITHUB_TOKEN,
)


StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


def call_github_model(prompt: str, response_schema: Type[StructuredModel], system_prompt: str) -> StructuredModel:
    response = client.chat.completions.parse(
        model=GITHUB_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.1,
        top_p=1.0,
        max_tokens=8192,
        response_format=response_schema,
    )

    parsed_response = response.choices[0].message.parsed

    if parsed_response is None:
        raise ValueError("LLM did not return a valid structured response.")

    return parsed_response


class AgentState(TypedDict, total=False):
    user_prompt: str
    plan: Optional[Plan]
    orchestrator_tasks: Optional[OrchestratorTasks]


def planner_agent(user_prompt: str) -> dict:
    prompt_content = get_prompt("planner", user_prompt)

    plan = call_github_model(
        prompt=prompt_content,
        response_schema=Plan,
        system_prompt=(
            "You are a strict backend project planning assistant. "
            "Return only a structured response that matches the provided schema."
        ),
    )

    return {"plan": plan}



workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_agent)

workflow.set_entry_point("planner")
workflow.add_edge("planner", END)

app_agent = workflow.compile()


class PlanRequest(BaseModel):
    user_prompt: str


@router.get("/server-connection")
def health_check():
    return {"message": "OK"}


@router.post("/plan/start", response_model=PlanWithOrchestration)
async def start_plan(payload: PlanRequest):
    try:
        result = app_agent.invoke(
            {
                "user_prompt": payload.user_prompt,
            }
        )

        plan = result.get("plan")

        if plan is None:
            raise HTTPException(
                status_code=500,
                detail="Planner did not return a valid plan.",
            )

        if not isinstance(plan, Plan):
            plan = Plan.model_validate(plan)

        return PlanWithOrchestration(
            plan=plan
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))