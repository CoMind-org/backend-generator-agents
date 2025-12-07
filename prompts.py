def planner_prompt(user_prompt: str) -> str:
    PLANNER_PROMPT = f"""
You are the PLANNER agent. Convert the user prompt into a COMPLETE engineering project plan. You should generate a detailed plan covering all aspects of the project.

User request:
{user_prompt}
    """
    return PLANNER_PROMPT


def orchestrator_prompt(plan: str) -> str:
    ORCHESTRATOR_PROMPT = f"""
You are the ORCHESTRATOR agent.

You receive the overall project plan created by the PLANNER agent. Your job is to prepare CLEAR, DETAILED instructions for three downstream agents:

1) REQUIREMENTS_AGENT
2) DATABASE_SCHEMA_AGENT
3) API_DESIGN_AGENT

Use the project plan below to:
- Summarize what each agent must focus on
- Specify the exact inputs they should consider
- Specify the expected outputs from each agent
- Mention any ordering/dependency notes between them

You must return ONLY a valid JSON object, with NO markdown, NO backticks, and NO extra commentary.

The JSON object must have exactly these fields:
- "requirementsTask": string with detailed instructions for REQUIREMENTS_AGENT
- "databaseSchemaTask": string with detailed instructions for DATABASE_SCHEMA_AGENT
- "apiDesignTask": string with detailed instructions for API_DESIGN_AGENT
- "notes": string with any global coordination notes

OverallProjectPlanJson:
{plan}
    """
    return ORCHESTRATOR_PROMPT
