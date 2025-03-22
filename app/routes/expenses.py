
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.models import Expense, ExpenseType
from app.db import expenses_collection
from bson import ObjectId
from typing import List, Optional

router = APIRouter()

@router.post("/")
async def create_expense(expense: Expense):
    expense_dict = expense.model_dump(exclude={'id'})
    result = await expenses_collection.insert_one(expense_dict)
    return {"id": str(result.inserted_id)}

@router.get("/", response_model=List[Expense])
async def get_expenses(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    expense_type: Optional[ExpenseType] = None
):
    query = {}
    
    # Date range filter
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query["date"] = {"$gte": start, "$lt": end}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Expense type filter
    if expense_type:
        query["expense_type"] = expense_type

    expenses = await expenses_collection.find(query).sort("date", -1).to_list(1000)
    return [{
        "id": str(expense["_id"]),
        **{k: v for k, v in expense.items() if k != "_id"}
    } for expense in expenses]

@router.get("/{expense_id}")
async def get_expense(expense_id: str):
    expense = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return {
        "id": str(expense["_id"]),
        **{k: v for k, v in expense.items() if k != "_id"}
    }

@router.put("/{expense_id}")
async def update_expense(expense_id: str, expense: Expense):
    existing = await expenses_collection.find_one({"_id": ObjectId(expense_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense_dict = expense.model_dump(exclude={'id'})
    await expenses_collection.update_one(
        {"_id": ObjectId(expense_id)},
        {"$set": expense_dict}
    )
    return {"message": "Expense updated successfully"}

@router.delete("/{expense_id}")
async def delete_expense(expense_id: str):
    result = await expenses_collection.delete_one({"_id": ObjectId(expense_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

@router.get("/summary/{month}/{year}")
async def get_expense_summary(month: int, year: int):
    # Validate month
    if not 1 <= month <= 12:
        raise HTTPException(status_code=400, detail="Invalid month")

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    pipeline = [
        {
            "$match": {
                "date": {
                    "$gte": start_date,
                    "$lt": end_date
                }
            }
        },
        {
            "$group": {
                "_id": "$expense_type",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        }
    ]

    summary = await expenses_collection.aggregate(pipeline).to_list(None)
    return {
        "month": month,
        "year": year,
        "expenses": summary
    }

