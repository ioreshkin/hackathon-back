from fastapi import FastAPI
from fastapi import APIRouter
from client import client


app = FastAPI()

router = APIRouter(
    prefix = "/lol",
    tags=["test"]
)

@router.get("/lol")
async def Hello():
    print("Hello!")

@router.get("/users")
async def get_events():
    response = await client.get("/api/users/")
    response.raise_for_status()
    return response.json()

app.include_router(router)