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
    open_ai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3
    
    # 네이버 금융 설정
    naver_finance_url: str = "https://finance.naver.com/sise/sise_rise.naver"
    naver_falling_url: str = "https://finance.naver.com/sise/sise_fall.naver"
    naver_news_url: str = "https://search.naver.com/search.naver"
    
    # 요청 설정
    request_timeout: int = 30
    max_retries: int = 3
    
    # 뉴스 분석 설정
    news_count: int = 10
    
    # LangChain 설정
    langchain_enabled: bool = True
    vectorstore_persist_directory: str = "./chroma_db"
    embedding_model: str = "text-embedding-ada-002"
    max_chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # 에이전트 설정
    agent_verbose: bool = True
    agent_max_iterations: int = 10
    agent_timeout: int = 300
    
    # RAG 설정
    rag_search_kwargs: dict = {"k": 3}
    rag_chain_type: str = "stuff"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()

# OpenAI API 키 설정 - 환경변수에서 직접 읽기
openai_key = os.getenv('OPEN_AI_API_KEY')
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
    print(f"DEBUG: OpenAI API 키 설정됨: {openai_key[:20]}...")
else:
    print("DEBUG: OpenAI API 키가 설정되지 않음")
