from fastapi import APIRouter
from test.model.plan import Plan
from test.config.database import collection
from test.schema.schemas import list_serial
from bson import ObjectId

router = APIRouter()

# GET Request Method
@router.get("/plan")
async def get_plan():
    plan = list(collection.find())
    return list_serial(plan)

@router.get("/plan/{id}")
async def get_plan(id: str):
    plan = list(collection.find({"_id": ObjectId(id)}))
    return list_serial(plan)


# POST Request Method
@router.post("/plan")
async def create_plan(plan: Plan):
    collection.insert_one(dict(plan))



# PUT Request Method
@router.put("/plan/{id}")
async def update_plan(id: str, plan: Plan):
    collection.update_one({"_id": ObjectId(id)}, {"$set": dict(plan)})

