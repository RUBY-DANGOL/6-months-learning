import logging

from fastapi import FastAPI

from app.core.logger import setup_logging
from app.database import Base, engine
from app.routers import customers

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Customer API", version="1.0.0")


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Creating database tables if missing")
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "ok"}


app.include_router(customers.router)
