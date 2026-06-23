import datetime
from typing import Literal, Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.strict_base_model import StrictBaseModel


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


class FileSystemNode(BaseModel):
    name: str
    type: Literal["file", "folder"]
    children: Optional[List["FileSystemNode"]] = Field(
        default=None,
        description="If type is 'folder', this must contain the actual files expected inside it. Do not leave logical folders empty.",
    )


class FolderStructure(StrictBaseModel):
    baseFolderName: str = Field(
        description="The name of the folder to be built."
    )
    fileNames: list[str] = Field(
        description="The main file names to be built."
    )
    subfolders: FileSystemNode = Field(
        description="The complete folder structure to be built, including folders and files."
    )


class Plan(StrictBaseModel):
    projectName: str = Field(
        description="The name of the app or project to be built."
    )
    projectType: str = Field(
        description="The type of app to be built, e.g. backend API, CLI tool, worker service, or microservice."
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
        description="A list of non-functional requirements such as performance, security, scalability, or maintainability."
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
    folderStructure: FolderStructure = Field(
        description="The folder structure of the app."
    )


class PlanHistory(BaseModel):
    plan: Plan
    date: str


class PlanDetails(BaseModel):
    user_prompt: str
    current_plan: Plan
    plan_history: list[PlanHistory]
    status: int
    refined_count: int
    created_at: str
    updated_at: str


class PlanRequest(BaseModel):
    user_prompt: str


class PlanCreateResponse(BaseModel):
    plan_id: str
    plan: Plan
