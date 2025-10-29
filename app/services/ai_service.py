import logging
from typing import Optional
from openai import OpenAI

from app.models.stock import Stock
from app.core.config import settings
from app.core.exceptions import OpenAIException

logger = logging.getLogger(__name__)


class AIService:
    """OpenAI API를 활용한 AI 분석 서비스 (LangChain 통합)"""
    
    def __init__(self):
        if not settings.open_ai_api_key:
            raise OpenAIException("OpenAI API 키가 설정되지 않았습니다.")
        
        self.client = OpenAI(api_key=settings.open_ai_api_key)
        
        # LangChain 서비스 초기화 (선택적)
        self.langchain_service = None
        try:
            from app.services.langchain_ai_service import LangChainAIService
            self.langchain_service = LangChainAIService()
            logger.info("LangChain 서비스 통합 완료")
        except Exception as e:
            logger.warning(f"LangChain 서비스 초기화 실패: {e}")
            self.langchain_service = None
    
    async def analyze_stock(self, stock: Stock, news_data: list = None) -> str:
        """종목에 대한 AI 분석 수행 (LangChain 우선)"""
        try:
            # LangChain 서비스가 있으면 사용
            if self.langchain_service:
                return await self.langchain_service.analyze_stock_with_chain(stock, news_data)
            
            # 기존 방식으로 폴백
            return await self._analyze_stock_legacy(stock, news_data)
            
        except Exception as e:
            logger.error(f"AI 분석 실패 ({stock.name}): {e}")
            raise OpenAIException(f"AI 분석에 실패했습니다: {str(e)}")
    
    async def _analyze_stock_legacy(self, stock: Stock, news_data: list = None) -> str:
        """기존 방식의 주식 분석 (폴백)"""
        try:
            # 뉴스 데이터가 있으면 포함
            news_context = ""
            if news_data:
                news_context = f"""
                
                관련 뉴스 정보:
                {self._format_news_for_ai(news_data)}
                """
            
            prompt = f"""
            다음은 오늘 한국 주식시장에서 급등한 종목의 정보입니다:
            
            종목명: {stock.name}
            현재가: {stock.price}원
            등락률: {stock.change}
            거래량: {stock.volume}{news_context}
            
            위 종목에 대해 다음 내용을 HTML 형식으로 분석해주세요:
            <h3>1. 급등 원인 분석</h3>
            <h3>2. 거래량 특징 분석</h3>
            <h3>3. 투자 위험도 평가</h3>
            <h3>4. 향후 전망</h3>
            <h3>5. 투자자 유의사항</h3>
            
            각 섹션은 HTML 태그를 사용하여 구조화하고, 한국어로 전문적이고 객관적으로 작성해주세요.
            """
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 금융분석 전문가입니다. 주식 종목 분석을 전문적이고 객관적으로 제공합니다. 응답은 반드시 HTML 태그를 사용하여 구조화된 형태로 작성되어야 하며, 마크다운 코드 블록(```html)으로 감싸지 않은 순수한 HTML 코드여야 합니다."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"레거시 AI 분석 완료: {stock.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"레거시 OpenAI API 오류 ({stock.name}): {e}")
            raise OpenAIException(f"AI 분석에 실패했습니다: {str(e)}")
    
    async def analyze_falling_stock(self, stock: Stock, news_data: list = None) -> str:
        """급락 종목에 대한 AI 분석 수행 (LangChain 우선)"""
        try:
            # LangChain 서비스가 있으면 사용
            if self.langchain_service:
                return await self.langchain_service.analyze_falling_stock_with_chain(stock, news_data)
            
            # 기존 방식으로 폴백
            return await self._analyze_falling_stock_legacy(stock, news_data)
            
        except Exception as e:
            logger.error(f"급락 종목 AI 분석 실패 ({stock.name}): {e}")
            raise OpenAIException(f"급락 종목 AI 분석에 실패했습니다: {str(e)}")
    
    async def _analyze_falling_stock_legacy(self, stock: Stock, news_data: list = None) -> str:
        """기존 방식의 급락 종목 분석 (폴백)"""
        try:
            # 뉴스 데이터가 있으면 포함
            news_context = ""
            if news_data:
                news_context = f"""
                
                관련 뉴스 정보:
                {self._format_news_for_ai(news_data)}
                """
            
            prompt = f"""
            다음은 오늘 한국 주식시장에서 급락한 종목의 정보입니다:
            
            종목명: {stock.name}
            현재가: {stock.price}원
            등락률: {stock.change}
            거래량: {stock.volume}{news_context}
            
            위 종목에 대해 다음 내용을 HTML 형식으로 분석해주세요:
            <h3>1. 급락 원인 분석</h3>
            <h3>2. 거래량 특징 분석</h3>
            <h3>3. 투자 위험도 평가</h3>
            <h3>4. 향후 전망</h3>
            <h3>5. 투자자 유의사항</h3>
            
            각 섹션은 HTML 태그를 사용하여 구조화하고, 한국어로 전문적이고 객관적으로 작성해주세요.
            """
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 금융분석 전문가입니다. 주식 종목 분석을 전문적이고 객관적으로 제공합니다. 응답은 반드시 HTML 태그를 사용하여 구조화된 형태로 작성되어야 하며, 마크다운 코드 블록(```html)으로 감싸지 않은 순수한 HTML 코드여야 합니다."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"레거시 급락 종목 AI 분석 완료: {stock.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"레거시 급락 종목 OpenAI API 오류 ({stock.name}): {e}")
            raise OpenAIException(f"급락 종목 AI 분석에 실패했습니다: {str(e)}")
    
    # LangChain 추가 기능들
    async def get_contextual_analysis(self, query: str) -> str:
        """컨텍스트 기반 분석 (RAG)"""
        if not self.langchain_service:
            return "LangChain 서비스가 초기화되지 않았습니다."
        
        return await self.langchain_service.get_contextual_analysis(query)
    
    def get_conversation_history(self) -> list:
        """대화 기록 반환"""
        if not self.langchain_service:
            return []
        
        return self.langchain_service.get_conversation_history()
    
    def clear_memory(self):
        """메모리 초기화"""
        if self.langchain_service:
            self.langchain_service.clear_memory()
    
    def get_vectorstore_stats(self) -> dict:
        """벡터 스토어 통계 정보"""
        if not self.langchain_service:
            return {"status": "not_available"}
        
        return self.langchain_service.get_vectorstore_stats()
    
    async def generate_report(self, stocks: list[Stock], analysis_results: list) -> str:
        """종목 리스트에 대한 종합 보고서 생성"""
        try:
            prompt = f"""
            다음은 오늘 급등한 주식 종목들의 정보와 분석 결과입니다:
            
            {self._format_stocks_for_ai(stocks, analysis_results)}
            
            위 종목들을 종합하여 다음 내용으로 HTML 보고서를 작성해주세요:
            <h2>1. 전체 시장 동향 분석</h2>
            <h2>2. 주요 급등 종목들의 공통점</h2>
            <h2>3. 업종별/테마별 분석</h2>
            <h2>4. 투자자 주의사항</h2>
            <h2>5. 향후 전망</h2>
            
            각 섹션은 HTML 태그를 사용하여 구조화하고, 전문적이고 객관적으로 작성해주세요.
            """
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 금융분석 전문가입니다. 주식 시장 분석 보고서를 전문적으로 작성합니다. 응답은 반드시 HTML 태그를 사용하여 구조화된 형태로 작성되어야 하며, 마크다운 코드 블록(```html)으로 감싸지 않은 순수한 HTML 코드여야 합니다."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai_max_tokens * 2,  # 보고서는 더 긴 토큰 사용
                temperature=settings.openai_temperature
            )
            
            report = response.choices[0].message.content
            logger.info("종합 보고서 생성 완료")
            return report
            
        except Exception as e:
            logger.error(f"보고서 생성 오류: {e}")
            raise OpenAIException(f"보고서 생성에 실패했습니다: {str(e)}")
    
    def _format_news_for_ai(self, news_data: list) -> str:
        """AI 분석을 위한 뉴스 데이터 포맷팅"""
        if not news_data:
            return "관련 뉴스 정보가 없습니다."
        
        formatted_news = []
        for i, news in enumerate(news_data, 1):
            # NewsItem 객체의 속성에 직접 접근
            title = getattr(news, 'title', '제목 없음')
            desc = getattr(news, 'desc', '내용 없음')
            
            formatted_news.append(f"""
            {i}. {title}
               - 내용: {desc}
            """)
        
        return "\n".join(formatted_news)
    
    def _format_stocks_for_ai(self, stocks: list[Stock], analysis_results: list) -> str:
        """AI 분석을 위한 종목 데이터 포맷팅"""
        formatted_data = []
        for i, (stock, analysis) in enumerate(zip(stocks, analysis_results), 1):
            formatted_data.append(f"""
            {i}. {stock.name}
               - 현재가: {stock.price}원
               - 등락률: {stock.change}
               - 거래량: {stock.volume}
               - 위험도: {analysis.risk_level}
               - 분석: {analysis.basic_analysis}
            """)
        
        return "\n".join(formatted_data)
