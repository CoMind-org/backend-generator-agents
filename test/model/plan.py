from pydantic import BaseModel

class Plan(BaseModel):
    name: str
    description: str
    complete: bool