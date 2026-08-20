from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import TypeVar, Generic, Type, Optional, List
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model: Type[ModelType]):
        self.collection = db[collection_name]
        self.model = model

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        if not ObjectId.is_valid(id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(id)})
        if doc:
            return self.model(**doc)
        return None

    async def create(self, obj_in: ModelType) -> ModelType:
        doc = obj_in.model_dump(by_alias=True, exclude_none=True)
        # Ensure _id is correctly set if missing
        if "_id" not in doc or not doc["_id"]:
            doc["_id"] = ObjectId()
        elif isinstance(doc["_id"], str):
             doc["_id"] = ObjectId(doc["_id"])
             
        result = await self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self.model(**doc)

    async def update(self, id: str, update_data: dict) -> Optional[ModelType]:
        if not ObjectId.is_valid(id):
            return None
        
        # update_data should be a dict of fields to update
        if not update_data:
            return await self.get_by_id(id)

        result = await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: str) -> bool:
        if not ObjectId.is_valid(id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
