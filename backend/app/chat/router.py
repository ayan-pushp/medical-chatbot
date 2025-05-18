from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.auth.dependencies import get_current_active_user
from app.auth.schemas import User
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import process_message, get_chat_history

router = APIRouter()

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
):
    return await process_message(request.message, request.dialog_state, current_user.username)

@router.get("/history")
async def chat_history(
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
):
    return await get_chat_history(current_user.username, limit)