
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models import Sale
from app.db import sales_collection, hotels_collection
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_sale(sale: Sale):
    # Verify hotel exists
    hotel = await hotels_collection.find_one({"_id": ObjectId(sale.hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    sale_dict = sale.model_dump(exclude={'id'})
    new_sale = await sales_collection.insert_one(sale_dict)
    return {"id": str(new_sale.inserted_id)}

@router.get("/hotel/{hotel_id}")
async def get_hotel_sales(hotel_id: str):
    # Verify hotel exists
    hotel = await hotels_collection.find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    
    sales = await sales_collection.find({"hotel_id": hotel_id}).to_list(1000)
    return [{
        "id": str(sale["_id"]),
        "date": sale["date"],
        "bill_no": sale["bill_no"],
        "kgs": sale["kgs"],
        "bill_amount": sale["bill_amount"],
        "received_amount": sale["received_amount"],
        "balance": sale["balance"]
    } for sale in sales]

@router.get("/{sale_id}")
async def get_sale(sale_id: str):
    sale = await sales_collection.find_one({"_id": ObjectId(sale_id)})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    return {
        "id": str(sale["_id"]),
        "hotel_id": sale["hotel_id"],
        "date": sale["date"],
        "bill_no": sale["bill_no"],
        "kgs": sale["kgs"],
        "bill_amount": sale["bill_amount"],
        "received_amount": sale["received_amount"],
        "balance": sale["balance"]
    }

@router.put("/{sale_id}")
async def update_sale(sale_id: str, sale: Sale):
    # Verify sale exists
    existing_sale = await sales_collection.find_one({"_id": ObjectId(sale_id)})
    if not existing_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    sale_dict = sale.model_dump(exclude={'id'})
    await sales_collection.update_one(
        {"_id": ObjectId(sale_id)},
        {"$set": sale_dict}
    )
    return {"message": "Sale updated successfully"}

@router.delete("/{sale_id}")
async def delete_sale(sale_id: str):
    result = await sales_collection.delete_one({"_id": ObjectId(sale_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Sale deleted successfully"}

@router.get("/")
async def get_all_sales():
    sales = await sales_collection.find().to_list(1000)
    return [{
        "id": str(sale["_id"]),
        "hotel_id": sale["hotel_id"],
        "date": sale["date"],
        "bill_no": sale["bill_no"],
        "kgs": sale["kgs"],
        "bill_amount": sale["bill_amount"],
        "received_amount": sale["received_amount"],
        "balance": sale["balance"]
    } for sale in sales]

