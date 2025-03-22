from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.models import DailySummary
from app.db import summary_collection, sales_collection, counter_sales_collection, expenses_collection
from bson import ObjectId

router = APIRouter()

@router.post("/generate/{date}")
async def generate_daily_summary(date: str):
    try:
        summary_date = datetime.strptime(date, "%Y-%m-%d")
        next_date = summary_date + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get hotel sales for the day
    hotel_sales = await sales_collection.find({
        "date": {
            "$gte": summary_date,
            "$lt": next_date
        }
    }).to_list(None)

    # Get counter sales for the day
    counter_sales = await counter_sales_collection.find({
        "date": {
            "$gte": summary_date,
            "$lt": next_date
        }
    }).to_list(None)

    # Get expenses for the day
    expenses = await expenses_collection.find({
        "date": {
            "$gte": summary_date,
            "$lt": next_date
        }
    }).to_list(None)

    # Calculate totals
    hotel_kgs = sum(sale["kgs"] for sale in hotel_sales)
    hotel_amount = sum(sale["bill_amount"] for sale in hotel_sales)
    counter_kgs = sum(sale["kgs"] for sale in counter_sales)
    counter_amount = sum(sale["amount"] for sale in counter_sales)
    total_expenses = sum(expense["amount"] for expense in expenses)

    # Calculate final balance
    total_income = hotel_amount + counter_amount
    balance = total_income - total_expenses

    # Create or update summary
    summary = DailySummary(
        date=summary_date,
        counter_kgs=counter_kgs,
        counter_amount=counter_amount,
        hotel_kgs=hotel_kgs,
        hotel_amount=hotel_amount,
        expenses=total_expenses,
        balance=balance
    )

    # Check if summary already exists
    existing_summary = await summary_collection.find_one({"date": summary_date})
    if existing_summary:
        await summary_collection.update_one(
            {"_id": existing_summary["_id"]},
            {"$set": summary.model_dump(exclude={'id'})}
        )
    else:
        await summary_collection.insert_one(summary.model_dump(exclude={'id'}))

    return summary

@router.put("/{date}")
async def update_daily_summary(date: str, summary: DailySummary):
    try:
        summary_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Check if summary exists
    existing_summary = await summary_collection.find_one({"date": summary_date})
    if not existing_summary:
        raise HTTPException(status_code=404, detail="Summary not found for this date")
    
    # Update summary
    summary_dict = summary.model_dump(exclude={'id'})
    await summary_collection.update_one(
        {"_id": existing_summary["_id"]},
        {"$set": summary_dict}
    )
    
    # Return updated document
    updated_summary = await summary_collection.find_one({"_id": existing_summary["_id"]})
    return {
        "id": str(updated_summary["_id"]),
        **{k: v for k, v in updated_summary.items() if k != '_id'}
    }

@router.get("/")
async def get_all_summaries():
    summaries = await summary_collection.find().sort("date", -1).to_list(1000)
    return [{
        "id": str(summary["_id"]),
        **{k: v for k, v in summary.items() if k != "_id"}
    } for summary in summaries]

@router.get("/{date}")
async def get_daily_summary(date: str):
    try:
        summary_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    summary = await summary_collection.find_one({"date": summary_date})
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found for this date")

    return {
        "id": str(summary["_id"]),
        **{k: v for k, v in summary.items() if k != "_id"}
    }

@router.get("/range/{start_date}/{end_date}")
async def get_summary_range(start_date: str, end_date: str):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    summaries = await summary_collection.find({
        "date": {
            "$gte": start,
            "$lt": end
        }
    }).sort("date", 1).to_list(None)

    return [{
        "id": str(summary["_id"]),
        **{k: v for k, v in summary.items() if k != "_id"}
    } for summary in summaries]
