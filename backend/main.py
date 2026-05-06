"""우리아이살집 (HomeForKid) - Backend Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.safety import router as safety_router

app = FastAPI(
    title="우리아이살집 API",
    description="아이 키우기 안전한 동네 판단 서비스",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(safety_router)


@app.get("/")
def health():
    return {"status": "ok", "service": "HomeForKid API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
