from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import create_tables
from app.routes.auth_routes import router as auth_router
from app.routes.expense_routes import router as expense_router
from app.routes.health_routes import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="Expense Tracker API", lifespan=lifespan)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(expense_router)
