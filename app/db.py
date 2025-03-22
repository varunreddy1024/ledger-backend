from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME
import certifi

# Create a client with SSL configuration
client = AsyncIOMotorClient(
    MONGO_URI,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=5000,
    tls=True,
    tlsCAFile=certifi.where()
)
database = client[DB_NAME]

hotels_collection = database["hotels"]
sales_collection = database["sales"]
counter_sales_collection = database["counter_sales"]
summary_collection = database["daily_summary"]
expenses_collection = database["expenses"]
