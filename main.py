from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timedelta
import os

app = FastAPI(title="NBA预测系统")

# 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("NBA_API_KEY", "demo-key")
CACHE = {}

@app.get("/")
async def root():
    return {"message": "NBA API运行中", "time": str(datetime.now())}

@app.get("/api/games/today")
async def get_today_games():
    """今日比赛接口"""
    cache_key = "today"
    
    if cache_key in CACHE:
        cached_time, data = CACHE[cache_key]
        if datetime.now() - cached_time < timedelta(minutes=5):
            return {"source": "cache", "data": data}
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.balldontlie.io/v1/games?dates[]={today}",
                headers={"Authorization": API_KEY},
                timeout=15.0
            )
            if resp.status_code == 200:
                data = resp.json()
                CACHE[cache_key] = (datetime.now(), data)
                return {"source": "live", "data": data}
    except Exception as e:
        return {"error": str(e), "data": []}
    
    return {"data": []}
