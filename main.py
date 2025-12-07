from dotenv import load_dotenv
from langchain_core.globals import set_verbose, set_debug
from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from prompts import planner_prompt, orchestrator_prompt
from states import Plan, OrchestratorTasks, PlanWithOrchestration

_ = load_dotenv()

set_debug(True)
set_verbose(True)

llm = ChatGroq(model="openai/gpt-oss-120b")


def planner_agent(state: dict) -> dict:
    user_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    if resp is None:
        raise ValueError("Planner did not return a valid response.")
    return {"plan": resp}


def orchestrator_agent(state: dict) -> dict:
    plan = state["plan"]
    if not isinstance(plan, Plan):
        plan = Plan.model_validate(plan)
    plan_json = plan.model_dump_json(indent=2)
    prompt = orchestrator_prompt(plan_json)
    msg = llm.invoke(prompt)
    content = msg.content if hasattr(msg, "content") else str(msg)
    tasks = OrchestratorTasks.model_validate_json(content)
    return {"plan": plan, "orchestrator_tasks": tasks}


graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("orchestrator", orchestrator_agent)
graph.set_entry_point("planner")
graph.add_edge("planner", "orchestrator")
graph.set_finish_point("orchestrator")
agent = graph.compile()

app = FastAPI(
    title="Project Planner API",
    version="1.0.0",
    description="API for generating engineering project plans from natural language prompts.",
)


class PlanRequest(BaseModel):
    user_prompt: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/plan", response_model=Plan)
async def create_plan(payload: PlanRequest):
    try:
        result = agent.invoke(
            {"user_prompt": payload.user_prompt},
            {"recursion_limit": 100},
        )
        plan = result.get("plan")
        if plan is None:
            raise HTTPException(status_code=500, detail="Planner did not return a plan")
        if isinstance(plan, Plan):
            return plan
        return Plan.model_validate(plan)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan-with-orchestration", response_model=PlanWithOrchestration)
async def create_plan_with_orchestration(payload: PlanRequest):
    try:
        result = agent.invoke(
            {"user_prompt": payload.user_prompt},
            {"recursion_limit": 100},
        )
        plan = result.get("plan")
        tasks = result.get("orchestrator_tasks")
        if plan is None or tasks is None:
            raise HTTPException(status_code=500, detail="Planner or Orchestrator did not return a valid response")
        if not isinstance(plan, Plan):
            plan = Plan.model_validate(plan)
        if not isinstance(tasks, OrchestratorTasks):
            tasks = OrchestratorTasks.model_validate(tasks)
        return PlanWithOrchestration(plan=plan, orchestratorTasks=tasks)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    result = agent.invoke(
        {"user_prompt": "Build a colourful modern todo app in html css and js"},
        {"recursion_limit": 100},
    )
    print("Final State:", result)


# if __name__ == "__main__":
#     result = agent.invoke({"user_prompt": "Build a colourful modern todo app in html css and js"},
#                           {"recursion_limit": 100})
#     print("Final State:", result)