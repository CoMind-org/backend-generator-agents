import asyncio
from typing import TypedDict, Optional, Literal

from dotenv import load_dotenv
from langchain_groq.chat_models import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from prompts import planner_prompt, orchestrator_prompt
from states import Plan, OrchestratorTasks

from test.config.database import plans_collection


# -------------- Configurations --------------
_ = load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


class AgentState(TypedDict):
    user_prompt: str
    plan: Optional[Plan]
    orchestrator_tasks: Optional[OrchestratorTasks]

    is_approved: bool
    refinement_feedback: Optional[str]



def planner_agent(state: AgentState) -> dict:
    user_prompt = state["user_prompt"]
    feedback = state.get("refinement_feedback")
    previous_plan = state.get("plan")

    prev_plan_str = previous_plan.model_dump_json(indent=2) if previous_plan else None

    structured_llm = llm.with_structured_output(Plan, method="json_schema", strict=True)

    prompt_content = planner_prompt(user_prompt, prev_plan_str, feedback)
    plan = structured_llm.invoke(prompt_content)

    if plan is None:
        raise ValueError("Planner did not return a valid structured Plan.")

    return {
        "plan": plan,
        "refinement_feedback": None
    }


def orchestrator_agent(state: AgentState) -> dict:
    plan = state["plan"]

    if not isinstance(plan, Plan):
        plan = Plan.model_validate(plan)

    plan_json = plan.model_dump_json(indent=2)

    structured_llm = llm.with_structured_output(OrchestratorTasks, method="json_schema", strict=True)
    tasks = structured_llm.invoke(orchestrator_prompt(plan_json))

    if tasks is None:
        raise ValueError("Orchestrator did not return valid structured tasks.")

    return {"orchestrator_tasks": tasks}


def route_after_planner(state: AgentState) -> Literal["orchestrator", "planner"]:
    if state.get("is_approved"):
        print("-> ROUTING TO ORCHESTRATOR (Approved)")
        return "orchestrator"

    print("-> ROUTING BACK TO PLANNER (Rejected, refining)")
    return "planner"


workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_agent)
workflow.add_node("orchestrator", orchestrator_agent)

workflow.set_entry_point("planner")

workflow.add_conditional_edges(
    "planner",
    route_after_planner,
    {
        "orchestrator": "orchestrator",
        "planner": "planner"
    }
)

workflow.add_edge("orchestrator", END)

checkpointer = MemorySaver()
app_agent = workflow.compile(
    checkpointer=checkpointer,
    interrupt_after=["planner"]
)


app = FastAPI(
    title="Project Planner API",
    version="1.0.0",
    description="API for generating engineering project plans from natural language prompts.",
)


class PlanStartRequest(BaseModel):
    user_prompt: str


class PlanReviewRequest(BaseModel):
    thread_id: str
    approve: bool
    feedback: Optional[str] = Field(None, description="Required if approve is false.")



@app.get("/health")
async def health():
    return {"status": "ok"}


# @app.post("/plan/start")
# async def start_plan(payload: PlanStartRequest):
#     thread_id = str(uuid.uuid4())
#     config = {"configurable": {"thread_id": thread_id}}
#
#     try:
#         initial_state = {
#             "user_prompt": payload.user_prompt,
#             "is_approved": False
#         }
#
#         app_agent.invoke(initial_state, config)
#
#         snapshot = app_agent.get_state(config)
#         plan = snapshot.values.get("plan")
#
#         return {
#             "thread_id": thread_id,
#             "status": "PAUSED_FOR_REVIEW",
#             "plan": plan
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan/start")
async def start_plan(payload: PlanStartRequest):
    try:
        # 1. Insert an initial document into MongoDB
        initial_doc = {
            "user_prompt": payload.user_prompt,
            "status": "PROCESSING",
            "plan": None
        }
        # Note the 'await' keyword here, which is why we needed motor
        insert_result = await plans_collection.insert_one(initial_doc)

        # 2. Extract the auto-generated MongoDB ObjectId and convert it to a string
        thread_id = str(insert_result.inserted_id)
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "user_prompt": payload.user_prompt,
            "is_approved": False
        }

        # 3. Run the LangGraph agent in a separate thread so it doesn't block FastAPI
        await asyncio.to_thread(app_agent.invoke, initial_state, config)

        # 4. Fetch the generated plan from the graph's state
        snapshot = app_agent.get_state(config)
        plan = snapshot.values.get("plan")

        # Convert the Pydantic plan model to a dictionary for MongoDB
        plan_dict = plan.model_dump() if plan else None

        # 5. Update the existing document in MongoDB with the generated plan
        await plans_collection.update_one(
            {"_id": insert_result.inserted_id},
            {"$set": {
                "status": "PAUSED_FOR_REVIEW",
                "plan": plan_dict
            }}
        )

        return {
            "thread_id": thread_id,
            "status": "PAUSED_FOR_REVIEW",
            "plan": plan
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))









@app.post("/plan/review")
async def review_plan(payload: PlanReviewRequest):
    config = {"configurable": {"thread_id": payload.thread_id}}

    snapshot = app_agent.get_state(config)
    if not snapshot.values:
        raise HTTPException(status_code=404, detail="Thread ID not found.")

    if not payload.approve and not payload.feedback:
        raise HTTPException(status_code=400, detail="Feedback must be provided when rejecting.")

    try:
        app_agent.update_state(
            config,
            {
                "is_approved": payload.approve,
                "refinement_feedback": payload.feedback if not payload.approve else None
            }
        )

        app_agent.invoke(None, config)

        final_snapshot = app_agent.get_state(config)

        if final_snapshot.next:
            return {
                "thread_id": payload.thread_id,
                "status": "REFINED_AND_PAUSED_FOR_REVIEW",
                "plan": final_snapshot.values.get("plan")
            }

        return {
            "thread_id": payload.thread_id,
            "status": "COMPLETED",
            "plan": final_snapshot.values.get("plan"),
            "orchestrator_tasks": final_snapshot.values.get("orchestrator_tasks")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/plan", response_model=Plan)
# async def create_plan(payload: PlanRequest):
#     try:
#         result = agent.invoke(
#             {"user_prompt": payload.user_prompt},
#             {"recursion_limit": 100},
#         )
#
#         plan = result.get("plan")
#
#         if plan is None:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Planner did not return a plan.",
#             )
#
#         if isinstance(plan, Plan):
#             return plan
#
#         return Plan.model_validate(plan)
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/plan-with-orchestration", response_model=PlanWithOrchestration)
# async def create_plan_with_orchestration(payload: PlanRequest):
#     try:
#         result = agent.invoke(
#             {"user_prompt": payload.user_prompt},
#             {"recursion_limit": 100},
#         )
#
#         plan = result.get("plan")
#         tasks = result.get("orchestrator_tasks")
#
#         if plan is None or tasks is None:
#             raise HTTPException(
#                 status_code=500,
#                 detail="Planner or Orchestrator did not return a valid response.",
#             )
#
#         if not isinstance(plan, Plan):
#             plan = Plan.model_validate(plan)
#
#         if not isinstance(tasks, OrchestratorTasks):
#             tasks = OrchestratorTasks.model_validate(tasks)
#
#         return PlanWithOrchestration(
#             plan=plan,
#             orchestratorTasks=tasks,
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#

if __name__ == "__main__":
    # result = agent.invoke(
    #     {"user_prompt": "Build a colourful modern todo app"},
    #     {"recursion_limit": 100},
    # )
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)