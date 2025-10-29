from fastapi import APIRouter

from app.api.v1.endpoints import stocks, reports, langchain

api_router = APIRouter()

api_router.include_router(
    stocks.router, 
    prefix="/stocks", 
    tags=["stocks"]
)

api_router.include_router(
    reports.router, 
    prefix="/reports", 
    tags=["reports"]
)

api_router.include_router(
    langchain.router, 
    prefix="/langchain", 
    tags=["langchain"]
)
