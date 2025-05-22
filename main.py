from fastapi import FastAPI
from fastapi import APIRouter
from client import client


app = FastAPI()

router = APIRouter(
    prefix = "/lol",
    tags=["test"]
)

@app.get("/")
async def root():
    return {"message": "It works!"}

@router.get("/lol")
async def Hello():
    return await get_events()

async def get_events():
    response = await client.get()
    response.raise_for_status()
    return response.json()

app.include_router(router)