"""
LangChain 도구(Tools) 및 에이전트 시스템
- 주식 분석 전용 도구들
- 멀티 에이전트 시스템
- 자동화된 분석 워크플로우
"""

import logging
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
import json

from langchain.tools import BaseTool, Tool
from langchain.agents import AgentType, initialize_agent, AgentExecutor
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor

from app.models.stock import Stock
from app.services.stock_service import StockService
from app.core.config import settings

logger = logging.getLogger(__name__)


class StockDataTool(BaseTool):
    """주식 데이터 수집 도구"""
    
    name: str = "stock_data_collector"
    description: str = "주식 데이터를 수집합니다. 급등/급락 종목 정보를 가져올 수 있습니다."
    
    def __init__(self, stock_service: StockService):
        super().__init__()
        self.stock_service = stock_service
    
    def _run(self, query: str) -> str:
        """도구 실행"""
        try:
            if "급등" in query or "상승" in query:
                stocks = self.stock_service.get_rising_stocks(count=5)
            elif "급락" in query or "하락" in query:
                stocks = self.stock_service.get_falling_stocks(count=5)
            else:
                stocks = self.stock_service.get_rising_stocks(count=5)
            
            result = []
            for stock in stocks:
                result.append({
                    "name": stock.name,
                    "price": stock.price,
                    "change": stock.change,
                    "volume": stock.volume
                })
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"주식 데이터 수집 실패: {e}")
            return f"데이터 수집 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """비동기 도구 실행"""
        return self._run(query)


class NewsAnalysisTool(BaseTool):
    """뉴스 분석 도구"""
    
    name: str = "news_analyzer"
    description: str = "주식 관련 뉴스를 수집하고 분석합니다."
    
    def __init__(self, stock_service: StockService):
        super().__init__()
        self.stock_service = stock_service
    
    def _run(self, stock_name: str) -> str:
        """도구 실행"""
        try:
            news_data = self.stock_service.get_stock_news(stock_name, count=5)
            
            if not news_data:
                return f"{stock_name}에 대한 뉴스 정보가 없습니다."
            
            result = []
            for news in news_data:
                result.append({
                    "title": news.get("title", ""),
                    "content": news.get("content", "")[:200] + "...",
                    "source": news.get("source", ""),
                    "published_at": news.get("published_at", "")
                })
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"뉴스 분석 실패: {e}")
            return f"뉴스 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, stock_name: str) -> str:
        """비동기 도구 실행"""
        return self._run(stock_name)


class TechnicalAnalysisTool(BaseTool):
    """기술적 분석 도구"""
    
    name: str = "technical_analyzer"
    description: str = "주식의 기술적 분석을 수행합니다. 차트 패턴, 지표 등을 분석합니다."
    
    def _run(self, stock_data: str) -> str:
        """도구 실행"""
        try:
            data = json.loads(stock_data) if isinstance(stock_data, str) else stock_data
            
            analysis = {
                "analysis_type": "technical",
                "patterns": [],
                "indicators": {},
                "recommendation": ""
            }
            
            # 간단한 기술적 분석 로직 (실제로는 더 복잡한 분석 필요)
            for stock in data:
                change_percent = float(stock.get("change", "0%").replace("%", ""))
                
                if change_percent > 10:
                    analysis["patterns"].append(f"{stock['name']}: 강한 상승 패턴")
                    analysis["recommendation"] = "매수 관심"
                elif change_percent < -10:
                    analysis["patterns"].append(f"{stock['name']}: 강한 하락 패턴")
                    analysis["recommendation"] = "매도 관심"
                else:
                    analysis["patterns"].append(f"{stock['name']}: 횡보 패턴")
                    analysis["recommendation"] = "관망"
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"기술적 분석 실패: {e}")
            return f"기술적 분석 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, stock_data: str) -> str:
        """비동기 도구 실행"""
        return self._run(stock_data)


class RiskAssessmentTool(BaseTool):
    """위험도 평가 도구"""
    
    name: str = "risk_assessor"
    description: str = "주식의 위험도를 평가하고 투자 위험 요소를 분석합니다."
    
    def _run(self, stock_data: str) -> str:
        """도구 실행"""
        try:
            data = json.loads(stock_data) if isinstance(stock_data, str) else stock_data
            
            risk_assessment = {
                "overall_risk_score": 0,
                "risk_factors": [],
                "recommendations": []
            }
            
            total_score = 0
            count = 0
            
            for stock in data:
                change_percent = float(stock.get("change", "0%").replace("%", ""))
                volume = stock.get("volume", "0")
                
                # 위험도 점수 계산 (1-10점)
                risk_score = 5  # 기본 점수
                
                if abs(change_percent) > 20:
                    risk_score += 3
                    risk_assessment["risk_factors"].append(f"{stock['name']}: 급격한 가격 변동")
                elif abs(change_percent) > 10:
                    risk_score += 2
                    risk_assessment["risk_factors"].append(f"{stock['name']}: 높은 변동성")
                
                if "M" in volume or "억" in volume:
                    risk_score += 1
                    risk_assessment["risk_factors"].append(f"{stock['name']}: 높은 거래량")
                
                total_score += min(risk_score, 10)
                count += 1
                
                # 권고사항
                if risk_score > 7:
                    risk_assessment["recommendations"].append(f"{stock['name']}: 고위험, 신중한 투자 필요")
                elif risk_score < 4:
                    risk_assessment["recommendations"].append(f"{stock['name']}: 상대적으로 안정적")
            
            risk_assessment["overall_risk_score"] = total_score / count if count > 0 else 5
            
            return json.dumps(risk_assessment, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"위험도 평가 실패: {e}")
            return f"위험도 평가 중 오류가 발생했습니다: {str(e)}"
    
    async def _arun(self, stock_data: str) -> str:
        """비동기 도구 실행"""
        return self._run(stock_data)


class StockAnalysisAgent:
    """주식 분석 에이전트"""
    
    def __init__(self, stock_service: StockService, llm):
        self.stock_service = stock_service
        self.llm = llm
        
        # 도구들 초기화
        self.tools = [
            StockDataTool(stock_service),
            NewsAnalysisTool(stock_service),
            TechnicalAnalysisTool(),
            RiskAssessmentTool()
        ]
        
        # 메모리 초기화
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 에이전트 초기화
        self.agent = self._create_agent()
        
        logger.info("주식 분석 에이전트 초기화 완료")
    
    def _create_agent(self) -> AgentExecutor:
        """에이전트 생성"""
        try:
            # 시스템 프롬프트
            system_prompt = """당신은 전문 주식 분석가입니다. 
            주어진 도구들을 활용하여 주식 시장을 분석하고 투자 조언을 제공합니다.
            
            분석 과정:
            1. 주식 데이터 수집
            2. 관련 뉴스 분석
            3. 기술적 분석 수행
            4. 위험도 평가
            5. 종합적인 투자 조언 제공
            
            항상 객관적이고 신중한 분석을 제공하며, 투자자의 위험을 최소화하는 것을 우선시합니다."""
            
            # 에이전트 생성
            agent = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.OPENAI_FUNCTIONS,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True,
                agent_kwargs={
                    "system_message": system_prompt
                }
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"에이전트 생성 실패: {e}")
            raise
    
    async def analyze_market(self, query: str) -> str:
        """시장 분석 수행"""
        try:
            result = await self.agent.arun(query)
            logger.info(f"시장 분석 완료: {query}")
            return result
            
        except Exception as e:
            logger.error(f"시장 분석 실패: {e}")
            return f"분석 중 오류가 발생했습니다: {str(e)}"
    
    async def analyze_stock(self, stock_name: str) -> str:
        """특정 종목 분석"""
        try:
            query = f"{stock_name}에 대한 종합적인 분석을 수행해주세요. 데이터 수집부터 위험도 평가까지 모든 과정을 포함해주세요."
            result = await self.agent.arun(query)
            logger.info(f"종목 분석 완료: {stock_name}")
            return result
            
        except Exception as e:
            logger.error(f"종목 분석 실패: {e}")
            return f"분석 중 오류가 발생했습니다: {str(e)}"
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """대화 기록 반환"""
        return self.memory.chat_memory.messages
    
    def clear_memory(self):
        """메모리 초기화"""
        self.memory.clear()
        logger.info("에이전트 메모리 초기화 완료")


class MultiAgentSystem:
    """멀티 에이전트 시스템"""
    
    def __init__(self, stock_service: StockService, llm):
        self.stock_service = stock_service
        self.llm = llm
        
        # 다양한 전문 에이전트들
        self.agents = {
            "data_collector": self._create_data_collector_agent(),
            "news_analyst": self._create_news_analyst_agent(),
            "technical_analyst": self._create_technical_analyst_agent(),
            "risk_analyst": self._create_risk_analyst_agent(),
            "investment_advisor": self._create_investment_advisor_agent()
        }
        
        logger.info("멀티 에이전트 시스템 초기화 완료")
    
    def _create_data_collector_agent(self) -> AgentExecutor:
        """데이터 수집 에이전트"""
        tools = [StockDataTool(self.stock_service)]
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
    
    def _create_news_analyst_agent(self) -> AgentExecutor:
        """뉴스 분석 에이전트"""
        tools = [NewsAnalysisTool(self.stock_service)]
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
    
    def _create_technical_analyst_agent(self) -> AgentExecutor:
        """기술적 분석 에이전트"""
        tools = [TechnicalAnalysisTool()]
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
    
    def _create_risk_analyst_agent(self) -> AgentExecutor:
        """위험 분석 에이전트"""
        tools = [RiskAssessmentTool()]
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
    
    def _create_investment_advisor_agent(self) -> AgentExecutor:
        """투자 조언 에이전트"""
        tools = [
            StockDataTool(self.stock_service),
            NewsAnalysisTool(self.stock_service),
            TechnicalAnalysisTool(),
            RiskAssessmentTool()
        ]
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
    
    async def comprehensive_analysis(self, query: str) -> Dict[str, Any]:
        """종합 분석 수행"""
        try:
            results = {}
            
            # 각 에이전트가 순차적으로 분석 수행
            for agent_name, agent in self.agents.items():
                try:
                    result = await agent.arun(query)
                    results[agent_name] = result
                    logger.info(f"{agent_name} 분석 완료")
                except Exception as e:
                    logger.error(f"{agent_name} 분석 실패: {e}")
                    results[agent_name] = f"분석 실패: {str(e)}"
            
            # 종합 결과 생성
            comprehensive_result = {
                "query": query,
                "analysis_results": results,
                "timestamp": datetime.now().isoformat(),
                "summary": "멀티 에이전트 시스템을 통한 종합 분석이 완료되었습니다."
            }
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"종합 분석 실패: {e}")
            return {"error": f"종합 분석 중 오류가 발생했습니다: {str(e)}"}
    
    async def collaborative_analysis(self, stock_name: str) -> Dict[str, Any]:
        """협업 분석 수행"""
        try:
            # 1단계: 데이터 수집
            data_result = await self.agents["data_collector"].arun(f"{stock_name} 관련 주식 데이터를 수집해주세요")
            
            # 2단계: 뉴스 분석
            news_result = await self.agents["news_analyst"].arun(f"{stock_name}에 대한 뉴스를 분석해주세요")
            
            # 3단계: 기술적 분석
            technical_result = await self.agents["technical_analyst"].arun(f"{stock_name}의 기술적 분석을 수행해주세요")
            
            # 4단계: 위험도 평가
            risk_result = await self.agents["risk_analyst"].arun(f"{stock_name}의 위험도를 평가해주세요")
            
            # 5단계: 투자 조언
            investment_result = await self.agents["investment_advisor"].arun(
                f"위의 모든 분석 결과를 바탕으로 {stock_name}에 대한 투자 조언을 제공해주세요"
            )
            
            return {
                "stock_name": stock_name,
                "analysis_steps": {
                    "data_collection": data_result,
                    "news_analysis": news_result,
                    "technical_analysis": technical_result,
                    "risk_assessment": risk_result,
                    "investment_advice": investment_result
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"협업 분석 실패: {e}")
            return {"error": f"협업 분석 중 오류가 발생했습니다: {str(e)}"}
