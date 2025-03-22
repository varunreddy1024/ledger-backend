from fastapi import APIRouter, HTTPException, Depends
from app.models import Hotel
from app.db import hotels_collection
from bson import ObjectId
from app.security import get_current_user, User

router = APIRouter()

@router.post("/")
async def create_hotel(hotel: Hotel, current_user: User = Depends(get_current_user)):
    hotel_dict = hotel.model_dump(exclude={'id'})
    new_hotel = await hotels_collection.insert_one(hotel_dict)
    return {"id": str(new_hotel.inserted_id)}

@router.get("/")
async def get_hotels(current_user: User = Depends(get_current_user)):
    hotels = await hotels_collection.find().to_list(100)
    return [{"id": str(h["_id"]), "name": h["name"], "address": h["address"], "phone": h["phone"], "opening_balance": h["opening_balance"]} for h in hotels]

@router.get("/{hotel_id}")
async def get_hotel(hotel_id: str, current_user: User = Depends(get_current_user)):
    hotel = await hotels_collection.find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"id": str(hotel["_id"]), "name": hotel["name"], "address": hotel["address"], "phone": hotel["phone"], "opening_balance": hotel["opening_balance"]}

@router.put("/{hotel_id}")
async def update_hotel(hotel_id: str, hotel: Hotel, current_user: User = Depends(get_current_user)):
    try:
        existing = await hotels_collection.find_one({"_id": ObjectId(hotel_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Hotel not found")
        
        hotel_dict = hotel.model_dump(exclude={'id'})
        await hotels_collection.update_one(
            {"_id": ObjectId(hotel_id)},
            {"$set": hotel_dict}
        )
        return {"message": "Hotel updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: str, current_user: User = Depends(get_current_user)):
    result = await hotels_collection.delete_one({"_id": ObjectId(hotel_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"message": "Hotel deleted successfully"}
