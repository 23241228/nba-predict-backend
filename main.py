from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timedelta
import os

app = FastAPI(title="NBA预测系统后端")

# 允许前端访问（CORS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量读取 API Key
API_KEY = os.getenv("NBA_API_KEY", "demo-key")
CACHE = {}

async def fetch_nba_data():
    """获取今日比赛数据"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.balldontlie.io/v1/games?dates[]={today}",
                headers={"Authorization": API_KEY},
                timeout=15.0
            )
            
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"data": [], "meta": {"mock": True}}
                
    except Exception as e:
        return {"error": str(e), "data": []}

@app.get("/")
async def root():
    return {"message": "NBA预测系统API运行中", "time": datetime.now()}

@app.get("/api/games/today")
async def get_today_games():
    """今日比赛接口"""
    cache_key = "today"
    
    # 检查缓存（5分钟）
    if cache_key in CACHE:
        cached_time, data = CACHE[cache_key]
        if datetime.now() - cached_time < timedelta(minutes=5):
            return {"source": "cache", "data": data}
    
    data = await fetch_nba_data()
    CACHE[cache_key] = (datetime.now(), data)
    return {"source": "live", "data": data}
