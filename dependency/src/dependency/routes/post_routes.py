from fastapi import APIRouter, status
from validation.models import UserBase, UserResponse

router = APIRouter()

@router.post("/user/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(register_data: UserBase):
    return "user registered"