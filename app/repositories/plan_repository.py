from bson import ObjectId
from bson.errors import InvalidId

from app.core.database import db
from app.schemas.plan import PlanDetails


class PlanRepository:
    def __init__(self):
        self.collection = db["plan"]

    @staticmethod
    def _to_object_id(plan_id: str) -> ObjectId:
        try:
            return ObjectId(plan_id)
        except InvalidId as exc:
            raise ValueError("Invalid ID format") from exc

    @staticmethod
    def _serialize(document):
        if not document:
            return None

        document = dict(document)
        document["_id"] = str(document["_id"])
        return document

    @staticmethod
    def _to_document(plan_details: PlanDetails) -> dict:
        if hasattr(plan_details, "model_dump"):
            return plan_details.model_dump(mode="json")

        return dict(plan_details)

    async def find_all(self) -> list[dict]:
        plans = []

        async for plan in self.collection.find():
            plans.append(self._serialize(plan))

        return plans

    async def find_by_id(self, plan_id: str) -> dict | None:
        object_id = self._to_object_id(plan_id)
        document = await self.collection.find_one({"_id": object_id})
        return self._serialize(document)

    async def insert_one(self, plan_details: PlanDetails) -> dict:
        document = self._to_document(plan_details)

        if not document:
            return {
                "message": "No plan details provided",
                "inserted_id": None,
            }

        result = await self.collection.insert_one(document)

        return {
            "message": "Plan details inserted successfully",
            "inserted_id": str(result.inserted_id),
        }

    async def update_one(self, plan_id: str, plan_details: PlanDetails) -> dict:
        object_id = self._to_object_id(plan_id)
        document = self._to_document(plan_details)

        result = await self.collection.update_one(
            {"_id": object_id},
            {"$set": document},
        )

        return {
            "message": "Plan details updated successfully",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
        }

    async def delete_one(self, plan_id: str) -> dict:
        object_id = self._to_object_id(plan_id)
        result = await self.collection.delete_one({"_id": object_id})

        return {
            "message": "Plan deleted successfully" if result.deleted_count else "Plan not found",
            "deleted_count": result.deleted_count,
        }

    async def clear_all_plans(self) -> dict:
        result = await self.collection.delete_many({})

        return {
            "message": "All plans cleared successfully",
            "deleted_count": result.deleted_count,
        }
