from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request, APIRouter
from src.schemas.users import User

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def my_endpoint(request: Request):
    return {"message": "Це мій маршрут з обмеженням швидкості"}
