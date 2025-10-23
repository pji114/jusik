from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import logging

from app.models.stock import Stock, RisingStocksResponse, StockAnalysisRequest, StockAnalysisResponse
from app.services.stock_service import StockService
from app.core.exceptions import create_http_exception

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/rising", response_model=RisingStocksResponse)
async def get_rising_stocks(
    count: int = Query(5, ge=1, le=20, description="조회할 급등 종목 수"),
    stock_service: StockService = Depends()
):
    """
    급등 종목 조회
    
    - **count**: 조회할 종목 수 (1-20개)
    """
    try:
        stocks = await stock_service.get_rising_stocks(count=count)
        
        return RisingStocksResponse(
            stocks=stocks,
            total_count=len(stocks),
            generated_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"급등 종목 조회 실패: {e}")
        raise create_http_exception(e)


@router.get("/{stock_name}/analysis", response_model=StockAnalysisResponse)
async def analyze_stock(
    stock_name: str,
    use_ai: bool = Query(True, description="AI 분석 사용 여부"),
    stock_service: StockService = Depends()
):
    """
    특정 종목 분석
    
    - **stock_name**: 분석할 종목명
    - **use_ai**: AI 분석 사용 여부
    """
    try:
        # 먼저 급등 종목에서 해당 종목 찾기
        rising_stocks = await stock_service.get_rising_stocks(count=20)
        target_stock = None
        
        for stock in rising_stocks:
            if stock.name == stock_name:
                target_stock = stock
                break
        
        if not target_stock:
            raise HTTPException(
                status_code=404, 
                detail=f"종목 '{stock_name}'을 급등 종목에서 찾을 수 없습니다."
            )
        
        # 종목 분석 수행
        analysis = await stock_service.analyze_stock(target_stock, use_ai=use_ai)
        
        return StockAnalysisResponse(
            stock=target_stock,
            analysis=analysis,
            generated_at=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"종목 분석 실패 ({stock_name}): {e}")
        raise create_http_exception(e)


@router.post("/analyze", response_model=StockAnalysisResponse)
async def analyze_stock_by_request(
    request: StockAnalysisRequest,
    stock_service: StockService = Depends()
):
    """
    요청 기반 종목 분석
    
    - **stock_name**: 분석할 종목명
    - **use_ai**: AI 분석 사용 여부
    """
    try:
        # 급등 종목에서 해당 종목 찾기
        rising_stocks = await stock_service.get_rising_stocks(count=20)
        target_stock = None
        
        for stock in rising_stocks:
            if stock.name == request.stock_name:
                target_stock = stock
                break
        
        if not target_stock:
            raise HTTPException(
                status_code=404, 
                detail=f"종목 '{request.stock_name}'을 급등 종목에서 찾을 수 없습니다."
            )
        
        # 종목 분석 수행
        analysis = await stock_service.analyze_stock(target_stock, use_ai=request.use_ai)
        
        return StockAnalysisResponse(
            stock=target_stock,
            analysis=analysis,
            generated_at=datetime.now()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"종목 분석 실패 ({request.stock_name}): {e}")
        raise create_http_exception(e)


@router.get("/{stock_name}/news")
async def get_stock_news(
    stock_name: str,
    stock_service: StockService = Depends()
):
    """
    특정 종목의 관련 뉴스 조회
    
    - **stock_name**: 뉴스를 조회할 종목명
    """
    try:
        news_list = await stock_service.get_stock_news(stock_name)
        return {
            "stock_name": stock_name,
            "news_count": len(news_list),
            "news_list": news_list,
            "generated_at": datetime.now()
        }
    except Exception as e:
        logger.error(f"뉴스 조회 실패 ({stock_name}): {e}")
        raise create_http_exception(e)
