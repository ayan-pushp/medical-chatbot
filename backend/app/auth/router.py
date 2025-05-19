from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.auth.schemas import Token, UserCreate, User
from app.auth.service import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user
)
from app.db.session import get_db

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    print("Form Data - Username:", form_data.username)
    print("Form Data - Password:", form_data.password)

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register_user(user_data: UserCreate):
    async with get_db() as db:  # Proper async context usage
        existing_user = await db.users.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = get_password_hash(user_data.password)
        await db.users.insert_one({
            "username": user_data.username,
            "hashed_password": hashed_password
        })
    return {"message": "User created successfully"}