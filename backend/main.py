"""
MeetAI FastAPI Application Entry Point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

# Ensure WinGet Links and System PATH are present for FFmpeg
winget_links = os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Links")
if os.path.exists(winget_links) and winget_links not in os.environ.get("PATH", ""):
    os.environ["PATH"] = winget_links + os.pathsep + os.environ.get("PATH", "")

from database import engine
import models
from routers import meetings, tasks, search, analytics
from seed import seed_database

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MeetAI API",
    description="Agentic AI Meeting Assistant — Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(meetings.router)
app.include_router(tasks.router)
app.include_router(search.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup_event():
    """Seed database on startup if empty."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        count = db.query(models.Meeting).count()
        if count == 0:
            print("Database is empty — seeding with sample data...")
            seed_database()
    finally:
        db.close()


@app.get("/")
async def root():
    return {
        "message": "MeetAI API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "provider_mode": os.getenv("AI_PROVIDER", "mock"),
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
