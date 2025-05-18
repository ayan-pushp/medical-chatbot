# from fastapi import FastAPI
# from app.routes import chat

# app = FastAPI()
# app.include_router(chat.router, prefix="/api")

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.db.session import init_db
from app.auth.router import router as auth_router
from app.chat.router import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="DocBot API",
    description="Medical Chatbot with Authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "DocBot API is running"}