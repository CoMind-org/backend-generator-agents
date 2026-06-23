from typing import Optional


agent_list = {
    "agents": [
        {
            "name": "CodeGenerationAgent",
            "description": "Generates production-ready backend source code following the planned architecture and design specifications.",
        },
        {
            "name": "TestingAgent",
            "description": "Creates unit tests, integration tests, and API tests to verify correctness and prevent regressions.",
        },
        {
            "name": "SecurityAgent",
            "description": "Performs security analysis, identifies vulnerabilities, and implements security best practices in the codebase and architecture.",
        },
        {
            "name": "DevOpsAgent",
            "description": "Creates CI/CD pipelines, Docker configurations, environment setups, and infrastructure scripts.",
        },
        {
            "name": "DocumentationAgent",
            "description": "Generates API documentation, setup guides, architectural explanations, and usage instructions.",
        },
    ]
}


def planner_prompt(
    user_prompt: str,
    previous_plan: Optional[str] = None,
    feedback: Optional[str] = None,
) -> str:
    return f"""
You are the PLANNER agent.

Here we create backend projects only.

Your task is to analyze the user requirement and create a comprehensive backend project plan.

The plan must include:

- Project name
- Project type
- Brief description
- Complexity level
- Functional requirements
- Non-functional requirements
- Required agents
- Entities
- Entity relationships
- API blueprint
- Architecture
- Tech stack
- Folder structure

Available agents:
{agent_list["agents"]}

Rules:
- Choose only the agents that are useful for the requested project.
- Put the selected agents in the correct execution order.
- If the project does not need a database, set database to "None".
- If the project does not need cache, set cache to "None".
- If the project does not need authentication, set auth to "None".
- If the project does not need an API, use an empty list for apiBlueprint.
- Do not invent unnecessary backend components for simple projects.
- The folder structure must include actual files, not only folder names.
- The output must match the required structured JSON schema exactly.

User request:
{user_prompt}
"""