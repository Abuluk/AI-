from fastapi import APIRouter

router = APIRouter()  # 必须命名为 router

@router.get("/")
async def get_messages():
    return {"message": "Messages list"}