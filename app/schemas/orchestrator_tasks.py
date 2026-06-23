from pydantic import Field
from app.schemas.plan import Plan
from app.schemas.strict_base_model import StrictBaseModel


class OrchestratorTasks(StrictBaseModel):
    codeGenerationTask: str = Field(
        description="The prompt/instruction for the CodeGenerationAgent to generate code for all files in the project."
    )
    testingTask: str = Field(
        description="The prompt/instruction for the TestingAgent to generate test cases for the project."
    )


class PlanWithOrchestration(StrictBaseModel):
    plan: Plan = Field(
        description="The planner output."
    )
    orchestratorTasks: OrchestratorTasks = Field(
        description="The orchestrator output for downstream agents."
    )
