from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.db.main import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def life_span(app:FastAPI):
    print("Starting up...")
    await init_db()
    yield
    print("Shutting down...")


version = "v1"

app = FastAPI(
    title="Book API",
    description="REST API for Books",
    version=version,
    lifespan=life_span
)


app.include_router(book_router, prefix=f"/api/{version}/books",tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth",tags=["User Authentication"])