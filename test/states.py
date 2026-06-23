from typing import Literal, Optional, List

from pydantic import BaseModel, Field, ConfigDict


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Architecture(StrictBaseModel):
    pattern: str = Field(
        description="The architecture pattern to be used, e.g. microservices, monolithic, layered, or serverless."
    )
    services: list[str] = Field(
        description="A list of services or major architectural components included in the architecture."
    )


class TechStack(StrictBaseModel):
    backend: str = Field(
        description="The backend technology to be used. Use 'None' if the project does not need a backend."
    )
    language: str = Field(
        description="The main programming language or languages to be used."
    )
    database: str = Field(
        description="The database technology to be used. Use 'None' if no database is required."
    )
    cache: str = Field(
        description="The caching technology to be used. Use 'None' if caching is not required."
    )
    auth: str = Field(
        description="The authentication method to be used. Use 'None' if authentication is not required."
    )
    apiStyle: str = Field(
        description="The API style to be used, e.g. REST, GraphQL, WebSocket, or None."
    )


# class FileSystemNode(BaseModel):
#     name: str
#     type: Literal["file", "folder"]
#     children: Optional[List["FileSystemNode"]] = None

class FileSystemNode(BaseModel):
    name: str
    type: Literal["file", "folder"]
    children: Optional[List["FileSystemNode"]] = Field(
        default=None,
        description="If type is 'folder', this MUST contain the actual files (e.g., .java, .py) expected inside it. Do not leave logical folders empty."
    )


class FolderStructure(StrictBaseModel):
    baseFolderName: str = Field(
        description="The name of the folder to be built."
    )
    fileNames: list[str] = Field(
        description="The name of the file to be built."
    )
    subfolders: FileSystemNode = Field(
        description="Folder structure to be built. Also every file in the structure (like folders and files in that folder)."
    )




class Plan(StrictBaseModel):
    projectName: str = Field(
        description="The name of the app or project to be built."
    )
    projectType: str = Field(
        description="The type of app to be built, e.g. web app, backend API, mobile app, dashboard, CLI tool."
    )
    description: str = Field(
        description="A clear description of the app to be built."
    )
    complexityLevel: str = Field(
        description="The complexity level of the app, e.g. simple, medium, complex."
    )
    functionalRequirements: list[str] = Field(
        description="A list of functional requirements for the app."
    )
    nonFunctionalRequirements: list[str] = Field(
        description="A list of non-functional requirements such as performance, security, accessibility, scalability, or maintainability."
    )
    agents: list[str] = Field(
        description="A list of agents to be used in the app planning workflow, ordered by execution order."
    )
    entities: list[str] = Field(
        description="A list of entities involved in the app."
    )
    relationships: list[str] = Field(
        description="A list of relationships between entities in the app."
    )
    apiBlueprint: list[str] = Field(
        description="A list of API endpoints and their purposes. Use an empty list if no API is needed."
    )
    architecture: Architecture = Field(
        description="The architecture details of the app."
    )
    techStack: TechStack = Field(
        description="The tech stack details of the app."
    )
    # folderStructure: list[str] = Field(
    #     description="A list of folders and their purposes for the project."
    # )
    folderStructure: FolderStructure = Field(
        description="The folder structure of the app."
    )


class OrchestratorTasks(StrictBaseModel):
    codeGenerationTask: str = Field(
        description="Create the prompt to pass for the code generation agent to generate codes for all files in the project."
    )
    testingTask: str = Field(
        description="Create the prompt to pass for the testing agent to generate test cases for the project."
    )


class PlanWithOrchestration(StrictBaseModel):
    plan: Plan = Field(
        description="The planner output."
    )
    orchestratorTasks: OrchestratorTasks = Field(
        description="The orchestrator output for downstream agents."
    )