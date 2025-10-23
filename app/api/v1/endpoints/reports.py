from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse
from typing import List, Optional
from datetime import datetime
import logging
import os

from app.models.stock import Stock
from app.services.stock_service import StockService
from app.services.report_service import ReportService
from app.core.exceptions import create_http_exception

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/html", response_class=HTMLResponse)
async def generate_html_report(
    count: int = Query(5, ge=1, le=20, description="분석할 종목 수"),
    use_ai: bool = Query(True, description="AI 분석 사용 여부"),
    save_file: bool = Query(False, description="파일로 저장할지 여부"),
    stock_service: StockService = Depends(),
    report_service: ReportService = Depends()
):
    """
    HTML 형태의 종합 보고서 생성
    
    - **count**: 분석할 종목 수 (1-20개)
    - **use_ai**: AI 분석 사용 여부
    - **save_file**: report 폴더에 파일로 저장할지 여부
    """
    try:
        # 급등 종목 조회
        stocks = await stock_service.get_rising_stocks(count=count)
        
        if not stocks:
            raise HTTPException(
                status_code=404,
                detail="급등 종목 데이터를 찾을 수 없습니다."
            )
        
        # 각 종목에 대한 분석 수행
        analyses = []
        for stock in stocks:
            analysis = await stock_service.analyze_stock(stock, use_ai=use_ai)
            analyses.append(analysis)
        
        # HTML 보고서 생성
        html_content = await report_service.generate_html_report(
            stocks=stocks,
            analyses=analyses,
            use_ai=use_ai
        )
        
        # 파일로 저장 (save_file=True인 경우)
        if save_file:
            filename = await report_service.save_html_report(html_content, use_ai)
            logger.info(f"HTML 보고서가 저장되었습니다: {filename}")
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HTML 보고서 생성 실패: {e}")
        raise create_http_exception(e)


@router.post("/save")
async def save_html_report(
    count: int = Query(5, ge=1, le=20, description="분석할 종목 수"),
    use_ai: bool = Query(True, description="AI 분석 사용 여부"),
    stock_service: StockService = Depends(),
    report_service: ReportService = Depends()
):
    """
    HTML 보고서를 report 폴더에 저장
    
    - **count**: 분석할 종목 수 (1-20개)
    - **use_ai**: AI 분석 사용 여부
    """
    try:
        # 급등 종목 조회
        stocks = await stock_service.get_rising_stocks(count=count)
        
        if not stocks:
            raise HTTPException(
                status_code=404,
                detail="급등 종목 데이터를 찾을 수 없습니다."
            )
        
        # 각 종목에 대한 분석 수행
        analyses = []
        for stock in stocks:
            analysis = await stock_service.analyze_stock(stock, use_ai=use_ai)
            analyses.append(analysis)
        
        # HTML 보고서 생성
        html_content = await report_service.generate_html_report(
            stocks=stocks,
            analyses=analyses,
            use_ai=use_ai
        )
        
        # 파일로 저장
        filename = await report_service.save_html_report(html_content, use_ai)
        
        return {
            "message": "HTML 보고서가 성공적으로 저장되었습니다.",
            "filename": filename,
            "filepath": f"report/{os.path.basename(filename)}",
            "generated_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HTML 보고서 저장 실패: {e}")
        raise create_http_exception(e)


@router.get("/summary")
async def get_market_summary(
    count: int = Query(5, ge=1, le=20, description="분석할 종목 수"),
    stock_service: StockService = Depends()
):
    """
    시장 요약 정보 조회
    
    - **count**: 분석할 종목 수 (1-20개)
    """
    try:
        # 급등 종목 조회
        stocks = await stock_service.get_rising_stocks(count=count)
        
        if not stocks:
            raise HTTPException(
                status_code=404,
                detail="급등 종목 데이터를 찾을 수 없습니다."
            )
        
        # 기본 통계 계산
        total_stocks = len(stocks)
        
        # 등락률 분석
        change_values = []
        for stock in stocks:
            try:
                change_str = stock.change.replace('%', '').replace('+', '')
                change_value = float(change_str)
                change_values.append(change_value)
            except:
                continue
        
        avg_change = sum(change_values) / len(change_values) if change_values else 0
        max_change = max(change_values) if change_values else 0
        min_change = min(change_values) if change_values else 0
        
        # 위험도 분류
        high_risk = len([v for v in change_values if v >= 20])
        medium_risk = len([v for v in change_values if 10 <= v < 20])
        low_risk = len([v for v in change_values if v < 10])
        
        return {
            "summary": {
                "total_stocks": total_stocks,
                "average_change": round(avg_change, 2),
                "max_change": round(max_change, 2),
                "min_change": round(min_change, 2),
                "risk_distribution": {
                    "high_risk": high_risk,
                    "medium_risk": medium_risk,
                    "low_risk": low_risk
                }
            },
            "stocks": [
                {
                    "name": stock.name,
                    "change": stock.change,
                    "price": stock.price,
                    "volume": stock.volume
                }
                for stock in stocks
            ],
            "generated_at": datetime.now()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"시장 요약 조회 실패: {e}")
        raise create_http_exception(e)
