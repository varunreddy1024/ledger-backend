from fastapi import APIRouter, Depends, Query, HTTPException
from app.db import hotels_collection, sales_collection, counter_sales_collection, expenses_collection
from app.security import get_current_user, User
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    date: Optional[str] = Query(None, description="Single date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics with optional date filtering"""
    
    # Handle date filtering
    date_filter = {}
    try:
        if date:
            # Single date filter
            search_date = datetime.strptime(date, "%Y-%m-%d")
            next_date = search_date + timedelta(days=1)
            date_filter = {
                "date": {
                    "$gte": search_date,
                    "$lt": next_date
                }
            }
        elif start_date and end_date:
            # Date range filter
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            date_filter = {
                "date": {
                    "$gte": start,
                    "$lt": end
                }
            }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Get total number of hotels (not affected by date filter)
    total_hotels = await hotels_collection.count_documents({})
    
    # Calculate total hotel sales and KGs
    hotel_sales_pipeline = []
    if date_filter:
        hotel_sales_pipeline.append({"$match": date_filter})
    hotel_sales_pipeline.append({
        "$group": {
            "_id": None,
            "total_amount": {"$sum": "$bill_amount"},
            "total_kgs": {"$sum": "$kgs"}
        }
    })
    
    hotel_sales_result = await sales_collection.aggregate(hotel_sales_pipeline).to_list(1)
    total_hotel_sales = hotel_sales_result[0]["total_amount"] if hotel_sales_result else 0
    total_hotel_kgs = hotel_sales_result[0]["total_kgs"] if hotel_sales_result else 0
    
    # Calculate total counter sales and KGs
    counter_sales_pipeline = []
    if date_filter:
        counter_sales_pipeline.append({"$match": date_filter})
    counter_sales_pipeline.append({
        "$group": {
            "_id": None,
            "total_amount": {"$sum": "$amount"},
            "total_kgs": {"$sum": "$kgs"}
        }
    })
    
    counter_sales_result = await counter_sales_collection.aggregate(counter_sales_pipeline).to_list(1)
    total_counter_sales = counter_sales_result[0]["total_amount"] if counter_sales_result else 0
    total_counter_kgs = counter_sales_result[0]["total_kgs"] if counter_sales_result else 0
    
    # Calculate total expenses
    expenses_pipeline = []
    if date_filter:
        expenses_pipeline.append({"$match": date_filter})
    expenses_pipeline.append({
        "$group": {
            "_id": None,
            "total": {"$sum": "$amount"}
        }
    })
    
    expenses_result = await expenses_collection.aggregate(expenses_pipeline).to_list(1)
    total_expenses = expenses_result[0]["total"] if expenses_result else 0
    
    return {
        "totalHotelSales": total_hotel_sales,
        "totalHotelKgs": total_hotel_kgs,
        "totalCounterSales": total_counter_sales,
        "totalCounterKgs": total_counter_kgs,
        "totalHotels": total_hotels,
        "totalExpenses": total_expenses,
        "dateFilter": {
            "single": date,
            "start": start_date,
            "end": end_date
        }
    }
