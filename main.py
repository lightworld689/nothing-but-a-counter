import fastapi
import time
import threading
from collections import defaultdict
import re
from fastapi import Request
from fastapi.responses import JSONResponse

import fastapi.middleware.cors

app = fastapi.FastAPI()

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Counter:
    def __init__(self, file="count.txt") -> None:
        self.file: str = file
        self.users = defaultdict(int)
        self._sync_from_file()
    
    def _sync_from_file(self) -> None:
        try:
            with open(self.file, "r") as f:
                for line in f:
                    username, count = line.strip().split(":")
                    self.users[username] = int(count)
        except FileNotFoundError:
            pass
    
    def _sync_to_file(self) -> None:
        with open(self.file, "w+") as f:
            for username, count in self.users.items():
                f.write(f"{username}:{count}\n")

    def _sync_thread(self, interval: int = 5) -> None:
        while 1:
            self._sync_to_file()
            time.sleep(interval)
    
    def start_sync(self, interval: int = 5) -> None:
        threading.Thread(target=self._sync_thread, args=(interval,)).start()
    
    def increase(self, username: str) -> int:
        self.users[username] += 1
        return self.users[username]

    def get_rank(self, username: str) -> int:
        sorted_users = sorted(self.users.items(), key=lambda item: item[1], reverse=True)
        for rank, (user, _) in enumerate(sorted_users, start=1):
            if user == username:
                return rank if rank <= 10 else "10+"
        return -1
    RATE_LIMIT = 50  # 每秒最多50请求
    RATE_LIMIT_INTERVAL = 1  # 限制间隔为1秒
    rate_limiter = defaultdict(lambda: {"count": 0, "last_reset": time.time()})

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client = request.client.host
        now = time.time()
        if now - Counter.rate_limiter[client]["last_reset"] > Counter.RATE_LIMIT_INTERVAL:
            Counter.rate_limiter[client] = {"count": 1, "last_reset": now}
        else:
            Counter.rate_limiter[client]["count"] += 1
            if Counter.rate_limiter[client]["count"] > Counter.RATE_LIMIT:
                return JSONResponse(status_code=429, content={"status": 429, "description": "Too Many Requests"})
        response = await call_next(request)
        return response
counter = Counter()
counter.start_sync()

@app.get("/{username}")
async def increase_v1(username: str):
    if len(username) > 20 or not re.match(r"^[a-zA-Z0-9_]+$", username):
        return {"status": 400, "description": "Bad Request: Username can only contain letters, numbers, and underscores, and must be 20 characters or less."}
    count = counter.increase(username)
    rank = counter.get_rank(username)
    return {"status": 200, "description": f"User {username} clicked {count} times.", "count": count, "rank": rank}

@app.get("/readonly")
async def readonly_v1():
    return {"status": 200, "description": "Nothing but a read-only counter.", "count": sum(counter.users.values())}

@app.get("/")
async def top_users_and_total_clicks():
    sorted_users = sorted(counter.users.items(), key=lambda item: item[1], reverse=True)[:10]
    top_users = [{"username": user, "clicks": clicks, "rank": rank + 1} for rank, (user, clicks) in enumerate(sorted_users)]
    total_clicks = sum(counter.users.values())
    return {"status": 200, "description": "Top 10 users and total clicks", "top_users": top_users, "total_clicks": total_clicks}