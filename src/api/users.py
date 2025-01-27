from fastapi import APIRouter, Depends

from src.schemas.users import User
from src.services.auth import get_current_user
from src.services.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
# @limiter.limit("5/minute")
async def me(user: User = Depends(get_current_user)):
    return user
