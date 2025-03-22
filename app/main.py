
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.dashboard import router as dashboard_router
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.hotels import router as hotels_router
from app.routes.sales import router as sales_router
from app.routes.daily_summary import router as summary_router
from app.routes.expenses import router as expenses_router
from app.routes.counter_sales import router as counter_sales_router

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the routers
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(hotels_router, prefix="/hotels", tags=["hotels"])
app.include_router(sales_router, prefix="/sales", tags=["sales"])
app.include_router(counter_sales_router, prefix="/counter-sales", tags=["counter-sales"])
app.include_router(summary_router, prefix="/daily-summary", tags=["daily-summary"])
app.include_router(expenses_router, prefix="/expenses", tags=["expenses"])

@app.get("/")
async def root():
    return {"message": "API is running"}
