from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import connect_to_mongo, close_mongo_connection, get_database
from shared.redis_client import connect_to_redis, close_redis_connection
from shared.auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth_service.schemas import UserCreate, UserLogin, Token, UserResponse
from auth_service.crud import create_user, authenticate_user, get_user_by_email
from auth_service.dependencies import get_current_user

REQUIRED_ENV_VARS = ["SECRET_KEY", "MONGODB_URL"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise ValueError(f"Переменная окружения {var} не установлена")

app = FastAPI(title="Auth Service", version="1.0.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Пароль должен содержать не менее 8 символов")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Пароль должен содержать заглавную букву")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Пароль должен содержать строчную букву")
    if not re.search(r'\d', password):
        raise HTTPException(status_code=400, detail="Пароль должен содержать цифру")

def validate_username(username: str):
    if not re.match(r"^[a-zA-Z0-9_]{3,20}$", username):
        raise HTTPException(
            status_code=400, 
            detail="Имя пользователя должно быть от 3 до 20 символов и содержать только буквы, цифры и символ подчеркивания"
        )

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    await connect_to_redis()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    await close_redis_connection()

@app.get("/")
async def root():
    return {"service": "Auth Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "здоровый", "service": "auth_service"}

@app.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate, db = Depends(get_database)):
    validate_username(user.username)
    validate_password(user.password)

    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Этот email уже зарегистрирован")

    new_user = await create_user(db, user)
    return UserResponse(
        id=str(new_user["_id"]),
        email=new_user["email"],
        username=new_user["username"],
        is_active=new_user["is_active"]
    )

@app.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, credentials: UserLogin, db = Depends(get_database)):
    user = await authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token)

@app.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user), db = Depends(get_database)):
    user = await db.backup_db.users.find_one({"_id": current_user["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        is_active=user["is_active"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)