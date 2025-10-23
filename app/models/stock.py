from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class StockBase(BaseModel):
    name: str = Field(..., description="종목명")
    price: str = Field(..., description="현재가")
    change: str = Field(..., description="등락률")
    volume: str = Field(..., description="거래량")
    link: str = Field(..., description="네이버 금융 링크")


class Stock(StockBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NewsItem(BaseModel):
    title: str = Field(..., description="뉴스 제목")
    desc: str = Field(..., description="뉴스 설명")


class StockAnalysis(BaseModel):
    basic_analysis: str = Field(..., description="기본 분석")
    risk_level: str = Field(..., description="위험도")
    urgency: str = Field(..., description="긴급도")
    volume_analysis: str = Field(..., description="거래량 분석")
    news_list: List[NewsItem] = Field(default=[], description="관련 뉴스")
    ai_analysis: Optional[str] = Field(None, description="AI 분석 결과")


class RisingStocksResponse(BaseModel):
    stocks: List[Stock] = Field(..., description="급등 종목 리스트")
    total_count: int = Field(..., description="총 종목 수")
    generated_at: datetime = Field(..., description="생성 시간")


class StockAnalysisRequest(BaseModel):
    stock_name: str = Field(..., description="분석할 종목명")
    use_ai: bool = Field(True, description="AI 분석 사용 여부")


class StockAnalysisResponse(BaseModel):
    stock: Stock = Field(..., description="종목 정보")
    analysis: StockAnalysis = Field(..., description="분석 결과")
    generated_at: datetime = Field(..., description="분석 생성 시간")
