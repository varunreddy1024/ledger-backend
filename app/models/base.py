from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Hotel(BaseModel):
    id: Optional[str] = None
    name: str
    address: str
    phone: str
    opening_balance: float

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Hotel Grand",
                "address": "123 Main St",
                "phone": "555-0123",
                "opening_balance": 1000.00
            }
        }

class ExpenseType(str, Enum):
    SALARY = "SALARY"
    RENT = "RENT"
    UTILITIES = "UTILITIES"
    SUPPLIES = "SUPPLIES"
    MAINTENANCE = "MAINTENANCE"
    OTHER = "OTHER"

class Expense(BaseModel):
    id: Optional[str] = None
    date: datetime
    expense_type: ExpenseType
    amount: float
    notes: Optional[str] = None
    paid_to: Optional[str] = None
    payment_method: Optional[str] = None
    reference_no: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "date": "2024-01-20T00:00:00",
                "expense_type": "SALARY",
                "amount": 5000.00,
                "notes": "Monthly salary for staff",
                "paid_to": "John Doe",
                "payment_method": "CASH",
                "reference_no": "SAL/JAN/001"
            }
        }

class Sale(BaseModel):
    id: Optional[str] = None
    hotel_id: str
    date: datetime
    bill_no: str
    kgs: float
    bill_amount: float
    received_amount: float
    balance: float

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "hotel_id": "67deddbad563ab51222036fd",
                "date": "2024-03-22T16:02:58.818Z",
                "bill_no": "BILL-001",
                "kgs": 20.5,
                "bill_amount": 2050.00,
                "received_amount": 2000.00,
                "balance": 50.00
            }
        }

class DailySummary(BaseModel):
    id: Optional[str] = None
    date: datetime
    counter_kgs: float
    counter_amount: float
    hotel_kgs: float
    hotel_amount: float
    expenses: float
    balance: float

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string
        }
        json_schema_extra = {
            "example": {
                "date": "2024-01-20T00:00:00",
                "counter_kgs": 50.5,
                "counter_amount": 2525.00,
                "hotel_kgs": 150.75,
                "hotel_amount": 7537.50,
                "expenses": 1000.00,
                "balance": 9062.50
            }
        }

    def model_dump(self, *args, **kwargs):
        # Convert ObjectId to string in the output
        data = super().model_dump(*args, **kwargs)
        if '_id' in data:
            data['id'] = str(data.pop('_id'))
        return data

class CounterSale(BaseModel):
    id: Optional[str] = None
    date: datetime
    bill_no: str
    kgs: float
    amount: float
    payment_method: Optional[str] = None  # CASH/UPI/CARD etc
    notes: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "date": "2024-03-22T16:02:58.818Z",
                "bill_no": "CS-001",
                "kgs": 10.5,
                "amount": 1050.00,
                "payment_method": "CASH",
                "notes": "Regular customer"
            }
        }
