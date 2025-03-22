from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from passlib.context import CryptContext
from datetime import datetime
from enum import Enum

# Configuration
MONGO_URI = "mongodb+srv://bkkvarun24:VarunReddy%40135@ledger-db.tmyoi.mongodb.net/?retryWrites=true&w=majority&appName=ledger-db"
DB_NAME = "ledger_db"

# Define UserRole enum (copied from your models)
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Admin user data
    admin_data = {
        "email": "admin@example.com",
        "username": "admin",
        "full_name": "Admin User",
        "hashed_password": pwd_context.hash("admin123"),
        "role": UserRole.ADMIN,
        "created_at": datetime.utcnow()
    }
    
    try:
        # Check if admin already exists
        existing_admin = await db["users"].find_one({"username": admin_data["username"]})
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        result = await db["users"].insert_one(admin_data)
        print(f"Admin user created successfully with id: {result.inserted_id}")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        # Close the client connection
        client.close()

# Run the script
if __name__ == "__main__":
    asyncio.run(create_admin())