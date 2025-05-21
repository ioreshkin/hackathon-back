from fastapi import FastAPI
from fastapi import APIRouter
app = FastAPI()

router = APIRouter(
    prefix = "/lol",
    tags=["test"]
)

@router.get("lol")
async def Hello():
    print("Hello!")