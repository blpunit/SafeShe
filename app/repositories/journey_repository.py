from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import BaseRepository
from app.models.journey import Journey, JourneyStateEnum
from typing import Optional, List, Any
from bson import ObjectId

class JourneyRepository(BaseRepository[Journey]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "journeys", Journey)

    async def get_active_journey(self, user_id: str) -> Optional[Journey]:
        if not ObjectId.is_valid(user_id):
            return None
        doc = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "state.current_state": {"$in": [JourneyStateEnum.ACTIVE.value, JourneyStateEnum.MONITORING.value]}
        })
        if doc:
            return self.model(**doc)
        return None

    async def get_journey_history(self, user_id: str, limit: int = 10) -> List[Journey]:
        if not ObjectId.is_valid(user_id):
            return []
        cursor = self.collection.find({
            "user_id": ObjectId(user_id)
        }).sort("created_timestamp", -1).limit(limit)
        
        journeys = []
        async for doc in cursor:
            journeys.append(self.model(**doc))
        return journeys

    async def add_journey_log(self, journey_id: str, log: Any) -> Optional[Journey]:
        # Temporarily simplified for phase 1
        if not ObjectId.is_valid(journey_id):
            return None
        result = await self.collection.update_one(
            {"_id": ObjectId(journey_id)},
            {"$push": {"logs": log}}
        )
        if result.modified_count > 0:
            return await self.get_by_id(journey_id)
        return None

    async def update_status(self, journey_id: str, status: str) -> Optional[Journey]:
        return await self.update(journey_id, {"state.current_state": status})
