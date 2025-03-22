import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# Database settings
username = quote_plus("bkkvarun24")
password = quote_plus("VarunReddy@135")
MONGO_URI = f"mongodb+srv://{username}:{password}@ledger-db.tmyoi.mongodb.net/?retryWrites=true&w=majority&appName=ledger-db"
DB_NAME = "ledger_db"

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
