from typing import Optional

agent_list = {
    "agents": [
        {
            "name": "CodeGenerationAgent",
            "description": "Generates production-ready backend source code following the planned architecture and design specifications."
        },
        {
            "name": "TestingAgent",
            "description": "Creates unit tests, integration tests, and API tests to verify correctness and prevent regressions."
        },
        {
            "name": "SecurityAgent",
            "description": "Performs security analysis, identifies vulnerabilities, and implements security best practices in the codebase and architecture."
        },
        {
            "name": "DevOpsAgent",
            "description": "Creates CI/CD pipelines, Docker configurations, environment setups, and infrastructure scripts."
        },
        {
            "name": "DocumentationAgent",
            "description": "Generates API documentation, setup guides, architectural explanations, and usage instructions."
        }
    ]
}


def planner_prompt(user_prompt: str, previous_plan: Optional[str] = None, feedback: Optional[str] = None) -> str:

    prompt = f"""
You are the PLANNER agent. Actually here we create backends only. Therefore, your main task is to analyze the user requirements and create a comprehensive project plan that includes the following components:

- Name of the Project: Provide a clear and concise name for the project that reflects its purpose and scope.
- Brief Description: Write a brief description of the project, outlining its main objectives, features, and target audience.
- Functional Requirements: List the functional requirements of the project, which describe the specific behaviors, features, and functionalities that the system must have.
- Non-Functional Requirements: List the non-functional requirements of the project, such as performance, security, accessibility, scalability, or maintainability.
- Tech Stack: Define the programming languages, frameworks, libraries, and tools that will be used in the project.
- Architecture: Design the overall system architecture, including the architectural pattern (e.g., microservices, monolithic) and major services.
- Database Schema: If the project requires a database, design the database schema. If no database is required, clearly state that no database schema is needed.
- Folder Structure: Define a clear and organized folder structure for the project that promotes maintainability and scalability. CRITICAL: You must explicitly include all necessary source code files (e.g., controllers, models, services), configuration files, and test files inside their respective folders. Do not just list the folders; populate them with the expected files.

Available agents:
{agent_list["agents"]}

Rules:
- Choose only the agents that are useful for the requested project. (e.g., simple projects might not require Security or DevOps agents).
- Put the selected agents in the correct execution order.
- If the project does not need a database or DevOps setup, say "None" or use an empty list where appropriate.
- Do not invent unnecessary backend components for simple projects.
- The output must match the required structured JSON schema exactly.

User request:
{user_prompt}
"""

    if previous_plan and feedback:
        prompt += f"""

==================================================
CRITICAL REVIEW FEEDBACK
==================================================
The user reviewed your previous plan and REJECTED it. You must refine the plan based on the specific feedback below.

PREVIOUS PLAN ATTEMPT:
{previous_plan}

USER FEEDBACK TO APPLY:
{feedback}

Please generate an updated, corrected plan that STRICTLY adheres to the user's feedback. Modify the architecture, tech stack, or agents as requested while maintaining the overall schema structure.
"""

    return prompt


def orchestrator_prompt(plan: str) -> str:

    return f"""
You are the ORCHESTRATOR agent.

You receive the overall project plan created by the PLANNER agent.

Your job is to prepare clear, detailed instructions for two downstream agents:

1. CodeGenerationAgent
2. TestingAgent

Use the project plan below to:
- Explain what each agent must focus on.
- Specify the exact inputs each agent should consider.
- Specify the expected outputs from each agent.
- Mention ordering or dependency notes between them.
- If the project does not require a database, clearly state that no database schema is required.
- If the project does not require an API, clearly state that no API design is required.

The output must match the required structured JSON schema exactly.

Overall project plan JSON:
{plan}
"""