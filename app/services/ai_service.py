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
    
    async def generate_tech_blog(self, tech_name: str, tech_type: str = "general", 
                               tech2_name: str = None, blog_type: str = "single") -> str:
        """
        IT 기술 블로그 생성
        
        Args:
            tech_name: 기술명
            tech_type: 기술 유형 (general, cloud, frontend, backend, database, algorithm, etc.)
            tech2_name: 비교할 두 번째 기술명 (비교 블로그용)
            blog_type: 블로그 유형 (single, comparison, algorithm)
        
        Returns:
            HTML 형태의 기술 블로그
        """
        try:
            if blog_type == "comparison" and tech2_name:
                return await self._generate_comparison_blog(tech_name, tech2_name, tech_type)
            elif blog_type == "algorithm":
                return await self._generate_algorithm_blog(tech_name, tech_type)
            else:
                return await self._generate_single_tech_blog(tech_name, tech_type)
                
        except Exception as e:
            logger.error(f"기술 블로그 생성 실패 ({tech_name}): {e}")
            raise OpenAIException(f"기술 블로그 생성에 실패했습니다: {str(e)}")
    
    async def _generate_single_tech_blog(self, tech_name: str, tech_type: str) -> str:
        """단일 기술 블로그 생성"""
        system_prompt = f"""당신은 IT 기술 전문가입니다. 
        {tech_type} 분야의 전문가로서 기술에 대해 정확하고 이해하기 쉽게 설명합니다.
        
        블로그 작성 시 다음 사항을 고려하세요:
        1. 기술적 정확성과 최신 정보 반영
        2. 초보자도 이해할 수 있는 설명
        3. 실제 사용 사례와 예시 제공 - 반드시 구체적이고 상세하게 설명
        4. 코드 예시가 있다면 포함
        5. HTML 형식으로 구조화된 응답
        6. 티스토리 블로그에 최적화된 스타일
        7. 최종 응답에 메타 설명이나 블로그 작성 가이드 같은 부가 설명은 절대 포함하지 말 것
        8. 특징과 실제 사용 예시는 특히 상세하게 작성할 것"""
        
        user_prompt = f"""
        '{tech_name}' 기술에 대해 다음 구조로 블로그를 작성해주세요:
        
        <h2>1. 기술의 정의</h2>
        <p>{tech_name}이 무엇인지 명확하고 간결하게 정의해주세요.</p>
        
        <h2>2. 기술의 탄생배경</h2>
        <p>이 기술이 왜 만들어졌는지, 어떤 문제를 해결하려고 하는지 설명해주세요.</p>
        
        <h2>3. 기술의 특징</h2>
        <p>이 기술의 주요 특징을 <strong>상세하게</strong> 설명해주세요. 최소 3-4개의 핵심 특징을 각각 설명하고, 장단점을 명확히 제시해주세요. 각 특징마다 왜 중요한지, 어떤 장점을 제공하는지 구체적으로 설명해주세요.</p>
        
        <h2>4. 실제 사용 예시</h2>
        <p>실제로 어떻게 사용되는지 <strong>구체적이고 상세한</strong> 예시를 들어 설명해주세요. 실제 회사나 서비스에서 어떻게 활용되는지, 어떤 상황에서 사용하는지, 사용 시 어떤 효과를 얻을 수 있는지 등을 포함해서 설명해주세요.</p>
        
        <h2>5. 코드 예시</h2>
        <p>코드로 표현이 가능하다면 실제 사용 예시 코드를 보여주세요.</p>
        
        <strong>중요:</strong> 마지막에 블로그 작성 가이드나 기술적 설명(예: "이 블로그는 HTML 태그로 구조화되어 있습니다") 같은 메타 설명은 절대 포함하지 마세요. 순수한 기술 내용만 제공해주세요.
        
        각 섹션은 HTML 태그를 사용하여 구조화하고, 한국어로 전문적이고 이해하기 쉽게 작성해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"단일 기술 블로그 생성 완료: {tech_name}")
            return content
            
        except Exception as e:
            logger.error(f"단일 기술 블로그 생성 실패 ({tech_name}): {e}")
            raise OpenAIException(f"기술 블로그 생성에 실패했습니다: {str(e)}")
    
    async def _generate_comparison_blog(self, tech1_name: str, tech2_name: str, tech_type: str) -> str:
        """기술 비교 블로그 생성"""
        system_prompt = f"""당신은 IT 기술 전문가입니다. 
        {tech_type} 분야의 전문가로서 두 기술을 객관적이고 정확하게 비교 분석합니다.
        
        비교 분석 시 다음 사항을 고려하세요:
        1. 객관적이고 공정한 비교
        2. 각 기술의 장단점 명확히 제시
        3. 실제 사용 사례와 예시 제공
        4. HTML 테이블을 활용한 비교 도표
        5. HTML 형식으로 구조화된 응답
        6. 티스토리 블로그에 최적화된 스타일"""
        
        user_prompt = f"""
        '{tech1_name}'와 '{tech2_name}' 기술을 비교하여 다음 구조로 블로그를 작성해주세요:
        
        <h2>1. 각 기술에 대한 정의</h2>
        <h3>{tech1_name}</h3>
        <p>{tech1_name}이 무엇인지 정의해주세요.</p>
        
        <h3>{tech2_name}</h3>
        <p>{tech2_name}이 무엇인지 정의해주세요.</p>
        
        <h2>2. 각 기술의 특징</h2>
        <h3>{tech1_name}의 특징</h3>
        <p>{tech1_name}의 주요 특징을 설명해주세요.</p>
        
        <h3>{tech2_name}의 특징</h3>
        <p>{tech2_name}의 주요 특징을 설명해주세요.</p>
        
        <h2>3. 기술 비교 도표</h2>
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead>
        <tr>
        <th style="padding: 10px; background-color: #f0f0f0;">비교 항목</th>
        <th style="padding: 10px; background-color: #f0f0f0;">{tech1_name}</th>
        <th style="padding: 10px; background-color: #f0f0f0;">{tech2_name}</th>
        </tr>
        </thead>
        <tbody>
        <tr><td style="padding: 10px;">성능</td><td style="padding: 10px;"></td><td style="padding: 10px;"></td></tr>
        <tr><td style="padding: 10px;">사용 편의성</td><td style="padding: 10px;"></td><td style="padding: 10px;"></td></tr>
        <tr><td style="padding: 10px;">확장성</td><td style="padding: 10px;"></td><td style="padding: 10px;"></td></tr>
        <tr><td style="padding: 10px;">비용</td><td style="padding: 10px;"></td><td style="padding: 10px;"></td></tr>
        <tr><td style="padding: 10px;">학습 곡선</td><td style="padding: 10px;"></td><td style="padding: 10px;"></td></tr>
        </tbody>
        </table>
        
        <h2>4. 각 기술의 사용 예시</h2>
        <h3>{tech1_name} 사용 예시</h3>
        <p>{tech1_name}이 언제, 어떻게 사용되는지 구체적인 예시를 들어 설명해주세요.</p>
        
        <h3>{tech2_name} 사용 예시</h3>
        <p>{tech2_name}이 언제, 어떻게 사용되는지 구체적인 예시를 들어 설명해주세요.</p>
        
        각 섹션은 HTML 태그를 사용하여 구조화하고, 한국어로 전문적이고 이해하기 쉽게 작성해주세요.
        티스토리 블로그에 최적화된 인라인 스타일을 사용해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"기술 비교 블로그 생성 완료: {tech1_name} vs {tech2_name}")
            return content
            
        except Exception as e:
            logger.error(f"기술 비교 블로그 생성 실패 ({tech1_name} vs {tech2_name}): {e}")
            raise OpenAIException(f"기술 비교 블로그 생성에 실패했습니다: {str(e)}")
    
    async def _generate_algorithm_blog(self, algorithm_name: str, algorithm_type: str) -> str:
        """알고리즘/자료구조/디자인 패턴 블로그 생성"""
        system_prompt = f"""당신은 컴퓨터 과학 전문가입니다. 
        알고리즘, 자료구조, 디자인 패턴 분야의 전문가로서 기술적 내용을 정확하고 이해하기 쉽게 설명합니다.
        
        블로그 작성 시 다음 사항을 고려하세요:
        1. 기술적 정확성과 이론적 배경 설명
        2. 단계별 설명과 시각적 이해 도움
        3. Java 코드 예시 제공
        4. 시간복잡도와 공간복잡도 분석
        5. HTML 형식으로 구조화된 응답
        6. 티스토리 블로그에 최적화된 스타일"""
        
        user_prompt = f"""
        '{algorithm_name}'에 대해 다음 구조로 블로그를 작성해주세요:
        
        <h2>1. 알고리즘의 정의</h2>
        <p>{algorithm_name}이 무엇인지 명확하고 간결하게 정의해주세요.</p>
        
        <h2>2. 알고리즘의 특징</h2>
        <p>이 알고리즘의 주요 특징, 장단점, 시간복잡도와 공간복잡도를 설명해주세요.</p>
        
        <h2>3. 알고리즘 동작 원리</h2>
        <p>알고리즘이 어떻게 동작하는지 단계별로 설명해주세요.</p>
        
        <h2>4. Java 코드 예제</h2>
        <pre style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto;">
        <code>
        // Java 코드 예제를 여기에 작성해주세요
        </code>
        </pre>
        
        <h2>5. 실제 사용 예시</h2>
        <p>이 알고리즘이 실제로 어떤 상황에서 사용되는지 구체적인 예시를 들어 설명해주세요.</p>
        
        각 섹션은 HTML 태그를 사용하여 구조화하고, 한국어로 전문적이고 이해하기 쉽게 작성해주세요.
        티스토리 블로그에 최적화된 인라인 스타일을 사용해주세요.
        코드 블록은 적절한 스타일링을 적용해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            
            content = response.choices[0].message.content
            logger.info(f"알고리즘 블로그 생성 완료: {algorithm_name}")
            return content
            
        except Exception as e:
            logger.error(f"알고리즘 블로그 생성 실패 ({algorithm_name}): {e}")
            raise OpenAIException(f"알고리즘 블로그 생성에 실패했습니다: {str(e)}")
