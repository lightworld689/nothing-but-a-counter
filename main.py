import fastapi
import fastapi.middleware.cors
import time
import threading

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
        self._sync_from_file()
    
    def _sync_from_file(self) -> None:
        with open(self.file, "r") as f:
            self.count = int(f.read())
    
    def _sync_to_file(self) -> None:
        with open(self.file, "w+") as f:
            f.write(str(self.count))

    def _sync_thread(self, interval: int = 5) -> None:
        while 1:
            self._sync_to_file()
            time.sleep(interval)
    
    def start_sync(self, interval: int = 5) -> None:
        threading.Thread(target=self._sync_thread, args=(interval,)).start()
    
    def increase(self) -> int:
        self.count+=1
        return self.count

counter = Counter()
counter.start_sync()

@app.get("/")
async def increase_v1():
    return {"status": 200, "description": "Nothing but a counter.", "count": counter.increase()}

@app.get("/readonly")
async def readonly_v1():
    return {"status": 200, "description": "Nothing but a read-only counter.", "count": counter.count}
