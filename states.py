from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Architecture(BaseModel):
    pattern: str = Field(description="The architecture pattern to be used, e.g. 'microservices', 'monolithic', etc.")
    services: list[str] = Field(description="A list of services to be included in the architecture")


class TechStack(BaseModel):
    backend: str = Field(description="The backend technology to be used, e.g. 'Django', 'Flask', etc.")
    language: str = Field(description="The programming language to be used, e.g. 'Python', 'JavaScript', etc.")
    database: str = Field(description="The database technology to be used, e.g. 'PostgreSQL', 'MongoDB', etc.")
    cache: str = Field(description="The caching technology to be used, e.g. 'Redis', 'Memcached', etc.")
    auth: str = Field(description="The authentication method to be used, e.g. 'OAuth', 'JWT', etc.")
    apiStyle: str = Field(description="The API style to be used, e.g. 'REST', 'GraphQL', etc.")


class Plan(BaseModel):
    projectName: str = Field(description="The name of app to be built")
    projectType: str = Field(description="The type of app to be built")
    description: str = Field(description="The description of app to be built")
    complexityLevel: str = Field(description="The complexity level of app to be built")
    functionalRequirements: list[str] = Field(description="A list of functional requirements for the app")
    nonFunctionalRequirements: list[str] = Field(description="A list of non-functional requirements for the app")
    constraints: list[str] = Field(description="A list of constraints for the app")
    modules: list[str] = Field(description="A list of modules to be included in the app")
    entities: list[str] = Field(description="A list of entities involved in the app")
    relationships: list[str] = Field(description="A list of relationships between entities in the app")
    apiBlueprint: list[str] = Field(description="A list of API endpoints and their purposes")
    architecture: Architecture = Field(description="The architecture details of the app")
    techStack: TechStack = Field(description="The tech stack details of the app")
    executionPipeline: list[str] = Field(description="A list of steps in the execution pipeline")
    risks: list[str] = Field(description="A list of potential risks for the app")
    recommendations: list[str] = Field(description="A list of recommendations for the app")


class OrchestratorTasks(BaseModel):
    requirementsTask: str = Field(description="Detailed instructions for the REQUIREMENTS_AGENT")
    databaseSchemaTask: str = Field(description="Detailed instructions for the DATABASE_SCHEMA_AGENT")
    apiDesignTask: str = Field(description="Detailed instructions for the API_DESIGN_AGENT")
    notes: Optional[str] = Field(default=None, description="Global notes for coordination between agents")


class PlanWithOrchestration(BaseModel):
    plan: Plan = Field(description="The planner output")
    orchestratorTasks: OrchestratorTasks = Field(description="The orchestrator output for downstream agents")
