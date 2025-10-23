import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API 설정
    app_name: str = "주식 분석 API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI 설정 - 환경변수에서 직접 읽기
    openai_api_key: Optional[str] = None
    
    # 네이버 금융 설정
    naver_finance_url: str = "https://finance.naver.com/sise/sise_rise.naver"
    naver_news_url: str = "https://search.naver.com/search.naver"
    
    # 요청 설정
    request_timeout: int = 30
    max_retries: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()

# OpenAI API 키 설정 - 환경변수에서 직접 읽기
openai_key = os.getenv('OPEN_AI_API_KEY') or settings.openai_api_key
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
    print(f"DEBUG: OpenAI API 키 설정됨: {openai_key[:20]}...")
else:
    print("DEBUG: OpenAI API 키가 설정되지 않음")
