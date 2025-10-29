"""
LangChain 기반 고급 분석 API 엔드포인트
- RAG 기반 분석
- 컨텍스트 기반 질의응답
- 벡터 스토어 관리
- 대화 기록 관리
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.services.ai_service import AIService
from app.services.agent_service import StockAnalysisAgent, MultiAgentSystem
from app.services.stock_service import StockService
from app.core.exceptions import create_http_exception

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic 모델들
class ContextualAnalysisRequest(BaseModel):
    query: str
    context_type: str = "general"  # general, technical, fundamental


class ContextualAnalysisResponse(BaseModel):
    query: str
    analysis: str
    sources: List[Dict[str, Any]] = []
    timestamp: datetime


class VectorStoreStats(BaseModel):
    status: str
    document_count: Optional[int] = None
    collection_name: Optional[str] = None
    error: Optional[str] = None


class ConversationHistory(BaseModel):
    messages: List[Dict[str, Any]]
    total_count: int


@router.post("/contextual-analysis", response_model=ContextualAnalysisResponse)
async def contextual_analysis(
    request: ContextualAnalysisRequest,
    ai_service: AIService = Depends()
):
    """
    컨텍스트 기반 분석 (RAG)
    - 벡터 스토어에서 관련 정보를 검색하여 분석
    - 과거 분석 결과와 패턴을 활용한 고도화된 분석
    """
    try:
        analysis = await ai_service.get_contextual_analysis(request.query)
        
        return ContextualAnalysisResponse(
            query=request.query,
            analysis=analysis,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"컨텍스트 기반 분석 실패: {e}")
        raise create_http_exception(e)


@router.get("/vectorstore/stats", response_model=VectorStoreStats)
async def get_vectorstore_stats(ai_service: AIService = Depends()):
    """
    벡터 스토어 통계 정보 조회
    - 저장된 문서 수
    - 컬렉션 상태
    - 시스템 상태
    """
    try:
        stats = ai_service.get_vectorstore_stats()
        return VectorStoreStats(**stats)
        
    except Exception as e:
        logger.error(f"벡터 스토어 통계 조회 실패: {e}")
        raise create_http_exception(e)


@router.get("/conversation/history", response_model=ConversationHistory)
async def get_conversation_history(ai_service: AIService = Depends()):
    """
    대화 기록 조회
    - AI와의 이전 대화 내용
    - 컨텍스트 유지를 위한 메모리 정보
    """
    try:
        history = ai_service.get_conversation_history()
        
        # 메시지를 딕셔너리 형태로 변환
        messages = []
        for msg in history:
            messages.append({
                "type": msg.__class__.__name__,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        
        return ConversationHistory(
            messages=messages,
            total_count=len(messages)
        )
        
    except Exception as e:
        logger.error(f"대화 기록 조회 실패: {e}")
        raise create_http_exception(e)


@router.post("/conversation/clear")
async def clear_conversation_history(ai_service: AIService = Depends()):
    """
    대화 기록 초기화
    - 메모리 클리어
    - 새로운 대화 세션 시작
    """
    try:
        ai_service.clear_memory()
        
        return {
            "message": "대화 기록이 성공적으로 초기화되었습니다.",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"대화 기록 초기화 실패: {e}")
        raise create_http_exception(e)


@router.post("/advanced-analysis")
async def advanced_stock_analysis(
    stock_name: str = Query(..., description="분석할 종목명"),
    analysis_depth: str = Query("comprehensive", description="분석 깊이: basic, comprehensive, deep"),
    include_technical: bool = Query(True, description="기술적 분석 포함 여부"),
    include_fundamental: bool = Query(True, description="기본적 분석 포함 여부"),
    include_sentiment: bool = Query(True, description="감정 분석 포함 여부"),
    ai_service: AIService = Depends()
):
    """
    고급 주식 분석
    - 다차원 분석 (기술적, 기본적, 감정 분석)
    - 분석 깊이 조절 가능
    - RAG 기반 컨텍스트 활용
    """
    try:
        # 분석 쿼리 구성
        analysis_query = f"""
        {stock_name}에 대한 {analysis_depth} 분석을 수행해주세요.
        
        포함할 분석 유형:
        - 기술적 분석: {include_technical}
        - 기본적 분석: {include_fundamental}  
        - 감정 분석: {include_sentiment}
        
        각 분석 유형별로 상세한 내용을 제공하고, 
        과거 유사한 패턴과 비교하여 종합적인 투자 관점을 제시해주세요.
        """
        
        analysis = await ai_service.get_contextual_analysis(analysis_query)
        
        return {
            "stock_name": stock_name,
            "analysis_depth": analysis_depth,
            "analysis": analysis,
            "analysis_types": {
                "technical": include_technical,
                "fundamental": include_fundamental,
                "sentiment": include_sentiment
            },
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"고급 주식 분석 실패: {e}")
        raise create_http_exception(e)


@router.post("/market-insights")
async def get_market_insights(
    sector: str = Query(None, description="특정 섹터 (선택사항)"),
    timeframe: str = Query("daily", description="시간대: daily, weekly, monthly"),
    ai_service: AIService = Depends()
):
    """
    시장 인사이트 분석
    - 섹터별 시장 동향
    - 시간대별 패턴 분석
    - 투자 기회 포인트 제시
    """
    try:
        query = f"""
        {sector if sector else '전체'} 시장의 {timeframe} 인사이트를 분석해주세요.
        
        다음 내용을 포함해주세요:
        1. 주요 시장 동향
        2. 섹터별 성과 분석
        3. 투자 기회 포인트
        4. 위험 요소
        5. 향후 전망
        
        최근 뉴스와 시장 데이터를 바탕으로 객관적이고 실용적인 분석을 제공해주세요.
        """
        
        insights = await ai_service.get_contextual_analysis(query)
        
        return {
            "sector": sector or "전체",
            "timeframe": timeframe,
            "insights": insights,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"시장 인사이트 분석 실패: {e}")
        raise create_http_exception(e)


@router.post("/risk-assessment")
async def risk_assessment(
    stock_name: str = Query(..., description="평가할 종목명"),
    risk_factors: List[str] = Query([], description="특정 위험 요소 (선택사항)"),
    ai_service: AIService = Depends()
):
    """
    위험도 평가
    - 종목별 위험 요소 분석
    - 위험도 점수 산출
    - 대응 방안 제시
    """
    try:
        risk_factors_text = ", ".join(risk_factors) if risk_factors else "일반적인 위험 요소"
        
        query = f"""
        {stock_name}의 위험도 평가를 수행해주세요.
        
        평가할 위험 요소: {risk_factors_text}
        
        다음 내용을 포함해주세요:
        1. 위험 요소 식별 및 분석
        2. 위험도 점수 (1-10점)
        3. 위험 요소별 영향도
        4. 대응 방안 및 완화 전략
        5. 투자 시 고려사항
        
        객관적이고 정량적인 평가를 제공해주세요.
        """
        
        assessment = await ai_service.get_contextual_analysis(query)
        
        return {
            "stock_name": stock_name,
            "risk_factors": risk_factors,
            "assessment": assessment,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"위험도 평가 실패: {e}")
        raise create_http_exception(e)


@router.get("/langchain/status")
async def get_langchain_status(ai_service: AIService = Depends()):
    """
    LangChain 시스템 상태 확인
    - 서비스 초기화 상태
    - 각 컴포넌트 상태
    - 성능 메트릭
    """
    try:
        status = {
            "langchain_service": ai_service.langchain_service is not None,
            "vectorstore_stats": ai_service.get_vectorstore_stats(),
            "conversation_history_count": len(ai_service.get_conversation_history()),
            "timestamp": datetime.now()
        }
        
        return status
        
    except Exception as e:
        logger.error(f"LangChain 상태 확인 실패: {e}")
        raise create_http_exception(e)


# 에이전트 관련 엔드포인트들
@router.post("/agent/market-analysis")
async def agent_market_analysis(
    query: str = Query(..., description="시장 분석 쿼리"),
    ai_service: AIService = Depends(),
    stock_service: StockService = Depends()
):
    """
    에이전트 기반 시장 분석
    - 자동화된 분석 워크플로우
    - 다단계 분석 과정
    - 도구 기반 데이터 수집 및 분석
    """
    try:
        if not ai_service.langchain_service:
            raise HTTPException(status_code=503, detail="LangChain 서비스가 초기화되지 않았습니다.")
        
        # 에이전트 생성
        agent = StockAnalysisAgent(stock_service, ai_service.langchain_service.llm)
        
        # 시장 분석 수행
        result = await agent.analyze_market(query)
        
        return {
            "query": query,
            "analysis": result,
            "agent_type": "market_analysis",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"에이전트 시장 분석 실패: {e}")
        raise create_http_exception(e)


@router.post("/agent/stock-analysis")
async def agent_stock_analysis(
    stock_name: str = Query(..., description="분석할 종목명"),
    ai_service: AIService = Depends(),
    stock_service: StockService = Depends()
):
    """
    에이전트 기반 종목 분석
    - 종합적인 종목 분석
    - 데이터 수집부터 투자 조언까지
    - 자동화된 분석 프로세스
    """
    try:
        if not ai_service.langchain_service:
            raise HTTPException(status_code=503, detail="LangChain 서비스가 초기화되지 않았습니다.")
        
        # 에이전트 생성
        agent = StockAnalysisAgent(stock_service, ai_service.langchain_service.llm)
        
        # 종목 분석 수행
        result = await agent.analyze_stock(stock_name)
        
        return {
            "stock_name": stock_name,
            "analysis": result,
            "agent_type": "stock_analysis",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"에이전트 종목 분석 실패: {e}")
        raise create_http_exception(e)


@router.post("/multi-agent/comprehensive-analysis")
async def multi_agent_comprehensive_analysis(
    query: str = Query(..., description="종합 분석 쿼리"),
    ai_service: AIService = Depends(),
    stock_service: StockService = Depends()
):
    """
    멀티 에이전트 종합 분석
    - 여러 전문 에이전트의 협업
    - 각 에이전트별 전문 분석
    - 종합적인 분석 결과 제공
    """
    try:
        if not ai_service.langchain_service:
            raise HTTPException(status_code=503, detail="LangChain 서비스가 초기화되지 않았습니다.")
        
        # 멀티 에이전트 시스템 생성
        multi_agent = MultiAgentSystem(stock_service, ai_service.langchain_service.llm)
        
        # 종합 분석 수행
        result = await multi_agent.comprehensive_analysis(query)
        
        return result
        
    except Exception as e:
        logger.error(f"멀티 에이전트 종합 분석 실패: {e}")
        raise create_http_exception(e)


@router.post("/multi-agent/collaborative-analysis")
async def multi_agent_collaborative_analysis(
    stock_name: str = Query(..., description="분석할 종목명"),
    ai_service: AIService = Depends(),
    stock_service: StockService = Depends()
):
    """
    멀티 에이전트 협업 분석
    - 순차적 분석 프로세스
    - 각 단계별 전문 에이전트 참여
    - 협업을 통한 정확한 분석
    """
    try:
        if not ai_service.langchain_service:
            raise HTTPException(status_code=503, detail="LangChain 서비스가 초기화되지 않았습니다.")
        
        # 멀티 에이전트 시스템 생성
        multi_agent = MultiAgentSystem(stock_service, ai_service.langchain_service.llm)
        
        # 협업 분석 수행
        result = await multi_agent.collaborative_analysis(stock_name)
        
        return result
        
    except Exception as e:
        logger.error(f"멀티 에이전트 협업 분석 실패: {e}")
        raise create_http_exception(e)


@router.get("/agent/conversation-history")
async def get_agent_conversation_history(
    ai_service: AIService = Depends(),
    stock_service: StockService = Depends()
):
    """
    에이전트 대화 기록 조회
    - 에이전트와의 이전 대화 내용
    - 분석 과정 기록
    """
    try:
        if not ai_service.langchain_service:
            raise HTTPException(status_code=503, detail="LangChain 서비스가 초기화되지 않았습니다.")
        
        # 에이전트 생성 및 대화 기록 조회
        agent = StockAnalysisAgent(stock_service, ai_service.langchain_service.llm)
        history = agent.get_conversation_history()
        
        messages = []
        for msg in history:
            messages.append({
                "type": msg.__class__.__name__,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "messages": messages,
            "total_count": len(messages),
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"에이전트 대화 기록 조회 실패: {e}")
        raise create_http_exception(e)


@router.post("/agent/clear-memory")
async def clear_agent_memory(
    ai_service: AIService = Depends(),
    stock_service: StockService = Depends()
):
    """
    에이전트 메모리 초기화
    - 대화 기록 삭제
    - 새로운 분석 세션 시작
    """
    try:
        if not ai_service.langchain_service:
            raise HTTPException(status_code=503, detail="LangChain 서비스가 초기화되지 않았습니다.")
        
        # 에이전트 생성 및 메모리 초기화
        agent = StockAnalysisAgent(stock_service, ai_service.langchain_service.llm)
        agent.clear_memory()
        
        return {
            "message": "에이전트 메모리가 성공적으로 초기화되었습니다.",
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"에이전트 메모리 초기화 실패: {e}")
        raise create_http_exception(e)
