import httpx
from config import settings

headers = {
    "Authorization": f"Bearer {settings.API_TOKEN}",
    "Content-Type": "application/json"
}

client = httpx.AsyncClient(
    base_url=settings.API_HOST,
    headers=headers,
    timeout=10,
    follow_redirects=True
)