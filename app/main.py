from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import logging
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.exceptions import create_http_exception


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    logger.info("🚀 주식 분석 API 서버가 시작됩니다...")
    yield
    # 종료 시
    logger.info("👋 주식 분석 API 서버가 종료됩니다...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI 기반 주식 분석 API - 네이버 금융 데이터를 활용한 급등 종목 분석 서비스",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 미들웨어: 요청 로깅
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 요청 로깅
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    # 응답 로깅
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response


# 루트 엔드포인트
@app.get("/", response_class=HTMLResponse)
async def root():
    """API 루트 페이지"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>주식 분석 API</title>
        <style>
            body { 
                font-family: 'Apple SD Gothic Neo', sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 40px 20px;
                line-height: 1.6;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 15px;
                text-align: center;
                margin-bottom: 30px;
            }
            .feature {
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                border-left: 4px solid #007bff;
            }
            .btn {
                display: inline-block;
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                margin: 10px 5px;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 주식 분석 API</h1>
            <p>AI 기반 주식 분석 플랫폼</p>
        </div>
        
        <div class="feature">
            <h3>📈 주요 기능</h3>
            <ul>
                <li><strong>급등 종목 조회:</strong> 실시간 급등 종목 데이터 수집</li>
                <li><strong>AI 분석:</strong> OpenAI GPT를 활용한 종목 분석</li>
                <li><strong>뉴스 수집:</strong> 종목별 관련 뉴스 자동 수집</li>
                <li><strong>보고서 생성:</strong> HTML 형태의 종합 분석 보고서</li>
            </ul>
        </div>
        
        <div class="feature">
            <h3>🚀 API 엔드포인트</h3>
            <ul>
                <li><code>GET /api/v1/stocks/rising</code> - 급등 종목 조회</li>
                <li><code>GET /api/v1/stocks/{stock_name}/analysis</code> - 종목 분석</li>
                <li><code>GET /api/v1/reports/html</code> - HTML 보고서 생성</li>
                <li><code>GET /api/v1/reports/summary</code> - 시장 요약</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/docs" class="btn">📚 API 문서 보기</a>
            <a href="/redoc" class="btn">📖 ReDoc 문서</a>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #e3f2fd; border-radius: 10px;">
            <h4>💡 사용 예시</h4>
            <p><strong>급등 종목 조회:</strong> <code>GET /api/v1/stocks/rising?count=5</code></p>
            <p><strong>종목 분석:</strong> <code>GET /api/v1/stocks/삼성전자/analysis?use_ai=true</code></p>
            <p><strong>HTML 보고서:</strong> <code>GET /api/v1/reports/html?count=3&use_ai=true</code></p>
        </div>
    </body>
    </html>
    """


# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time()
    }


# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")


# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"전역 예외 발생: {exc}")
    return create_http_exception(exc)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
