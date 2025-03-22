from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.models import CounterSale
from app.db import counter_sales_collection
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_counter_sale(sale: CounterSale):
    sale_dict = sale.model_dump(exclude={'id'})
    result = await counter_sales_collection.insert_one(sale_dict)
    return {"id": str(result.inserted_id)}

@router.get("/")
async def get_all_counter_sales():
    sales = await counter_sales_collection.find().sort("date", -1).to_list(1000)
    return [{
        "id": str(sale["_id"]),
        **{k: v for k, v in sale.items() if k != "_id"}
    } for sale in sales]

@router.get("/{sale_id}")
async def get_counter_sale(sale_id: str):
    sale = await counter_sales_collection.find_one({"_id": ObjectId(sale_id)})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    return {
        "id": str(sale["_id"]),
        **{k: v for k, v in sale.items() if k != "_id"}
    }

@router.get("/date/{date}")
async def get_counter_sales_by_date(date: str):
    try:
        search_date = datetime.strptime(date, "%Y-%m-%d")
        next_date = search_date + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    sales = await counter_sales_collection.find({
        "date": {
            "$gte": search_date,
            "$lt": next_date
        }
    }).to_list(1000)

    return [{
        "id": str(sale["_id"]),
        **{k: v for k, v in sale.items() if k != "_id"}
    } for sale in sales]

@router.delete("/{sale_id}")
async def delete_counter_sale(sale_id: str):
    result = await counter_sales_collection.delete_one({"_id": ObjectId(sale_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"message": "Sale deleted successfully"}