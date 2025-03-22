from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Configuration
MONGO_URI = "mongodb+srv://bkkvarun24:VarunReddy%40135@ledger-db.tmyoi.mongodb.net/?retryWrites=true&w=majority&appName=ledger-db"
DB_NAME = "ledger_db"
SECRET_KEY = "your-super-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Models
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserInDB(UserBase):
    id: Optional[str] = None
    hashed_password: str

class User(UserBase):
    id: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Database connection
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_user(username: str) -> Optional[UserInDB]:
    user_dict = await db["users"].find_one({"username": username})
    if user_dict:
        return UserInDB(**{**user_dict, "id": str(user_dict["_id"])})
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def create_admin():
    try:
        # Check if admin already exists
        existing_admin = await db["users"].find_one({"username": "admin"})
        if existing_admin:
            print("Admin user already exists!")
            return

        # Admin user data
        admin_data = {
            "email": "admin@example.com",
            "username": "admin",
            "full_name": "Admin User",
            "hashed_password": get_password_hash("admin123"),
            "role": UserRole.ADMIN,
            "created_at": datetime.utcnow()
        }
        
        # Create admin user
        result = await db["users"].insert_one(admin_data)
        print(f"Admin user created successfully with id: {result.inserted_id}")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_admin())
