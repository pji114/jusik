from fastapi import HTTPException
from typing import Optional


class StockAnalysisException(Exception):
    """주식 분석 관련 예외"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DataFetchException(StockAnalysisException):
    """데이터 수집 실패 예외"""
    def __init__(self, message: str = "데이터 수집에 실패했습니다."):
        super().__init__(message, 503)


class AnalysisException(StockAnalysisException):
    """분석 실패 예외"""
    def __init__(self, message: str = "분석 처리에 실패했습니다."):
        super().__init__(message, 500)


class OpenAIException(StockAnalysisException):
    """OpenAI API 오류 예외"""
    def __init__(self, message: str = "AI 분석 서비스에 오류가 발생했습니다."):
        super().__init__(message, 503)


def create_http_exception(exception: StockAnalysisException) -> HTTPException:
    """StockAnalysisException을 HTTPException으로 변환"""
    return HTTPException(
        status_code=exception.status_code,
        detail={
            "error": exception.__class__.__name__,
            "message": exception.message
        }
    )
