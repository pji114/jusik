"""
LangChain 기반 고도화된 AI 서비스
- 프롬프트 템플릿 시스템
- 체인 기반 분석
- 메모리 및 컨텍스트 관리
- RAG 시스템
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.prompts import ChatPromptTemplate, FewShotPromptTemplate
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import RetrievalQA
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent

from app.core.config import settings
from app.core.exceptions import OpenAIException
from app.models.stock import Stock, StockAnalysis

logger = logging.getLogger(__name__)


class LangChainAIService:
    """LangChain 기반 고도화된 AI 서비스"""
    
    def __init__(self):
        """초기화"""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            openai_api_key=settings.openai_api_key
        )
        
        # 임베딩 모델 초기화
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
        
        # 벡터 스토어 초기화
        self.vectorstore = None
        self._init_vectorstore()
        
        # 메모리 초기화
        self.memory = ConversationSummaryMemory(
            llm=self.llm,
            memory_key="chat_history",
            return_messages=True
        )
        
        # 프롬프트 템플릿 초기화
        self._init_prompt_templates()
        
        # 체인 초기화
        self._init_chains()
        
        logger.info("LangChain AI 서비스 초기화 완료")
    
    def _init_vectorstore(self):
        """벡터 스토어 초기화"""
        try:
            # Chroma 벡터 스토어 생성
            self.vectorstore = Chroma(
                persist_directory=settings.vectorstore_persist_directory,
                embedding_function=self.embeddings
            )
            logger.info("벡터 스토어 초기화 완료")
        except Exception as e:
            logger.warning(f"벡터 스토어 초기화 실패: {e}")
            self.vectorstore = None
    
    def _init_prompt_templates(self):
        """프롬프트 템플릿 초기화"""
        
        # 기본 시스템 프롬프트
        self.system_prompt = """당신은 한국 주식시장의 전문 금융 분석가입니다. 
        주식 종목에 대한 정확하고 객관적인 분석을 제공하며, 
        투자자들이 이해하기 쉽도록 명확하게 설명합니다.
        
        분석 시 다음 사항을 고려하세요:
        1. 객관적이고 사실 기반의 분석
        2. 위험 요소와 기회 요소의 균형적 제시
        3. 투자자 보호를 위한 유의사항 명시
        4. HTML 형식으로 구조화된 응답"""
        
        # 급등 종목 분석 프롬프트 템플릿
        self.rising_stock_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """
            다음은 오늘 한국 주식시장에서 급등한 종목의 정보입니다:
            
            종목명: {stock_name}
            현재가: {stock_price}원
            등락률: {stock_change}
            거래량: {stock_volume}
            
            관련 뉴스 정보:
            {news_context}
            
            위 종목에 대해 다음 내용을 HTML 형식으로 분석해주세요:
            <h3>1. 급등 원인 분석</h3>
            <h3>2. 거래량 특징 분석</h3>
            <h3>3. 기술적 분석</h3>
            <h3>4. 투자 매력도 평가</h3>
            <h3>5. 향후 전망</h3>
            <h3>6. 투자자 유의사항</h3>
            
            각 섹션은 HTML 태그를 사용하여 구조화하고, 한국어로 전문적이고 객관적으로 작성해주세요.
            """)
        ])
        
        # 급락 종목 분석 프롬프트 템플릿
        self.falling_stock_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """
            다음은 오늘 한국 주식시장에서 급락한 종목의 정보입니다:
            
            종목명: {stock_name}
            현재가: {stock_price}원
            등락률: {stock_change}
            거래량: {stock_volume}
            
            관련 뉴스 정보:
            {news_context}
            
            위 종목에 대해 다음 내용을 HTML 형식으로 분석해주세요:
            <h3>1. 급락 원인 분석</h3>
            <h3>2. 거래량 특징 분석</h3>
            <h3>3. 투자 위험도 평가</h3>
            <h3>4. 향후 전망</h3>
            <h3>5. 투자자 유의사항</h3>
            
            각 섹션은 HTML 태그를 사용하여 구조화하고, 한국어로 전문적이고 객관적으로 작성해주세요.
            """)
        ])
        
        # Few-shot 예제들
        self.few_shot_examples = [
            {
                "input": "삼성전자 급등 분석",
                "output": """
                <h3>1. 급등 원인 분석</h3>
                <p>삼성전자의 급등은 반도체 업황 개선과 메모리 가격 상승 기대감이 주요 원인으로 분석됩니다.</p>
                
                <h3>2. 거래량 특징 분석</h3>
                <p>평소 대비 3배 이상 증가한 거래량은 기관투자자들의 매수세가 강화되었음을 시사합니다.</p>
                """
            },
            {
                "input": "LG화학 급락 분석", 
                "output": """
                <h3>1. 급락 원인 분석</h3>
                <p>LG화학의 급락은 배터리 사업 부진과 원자재 가격 상승이 주요 원인으로 분석됩니다.</p>
                
                <h3>2. 투자 위험도 평가</h3>
                <p>단기적 하락 리스크가 높으나 장기적 관점에서는 배터리 시장 성장 잠재력이 있습니다.</p>
                """
            }
        ]
        
        # Few-shot 프롬프트 템플릿
        self.few_shot_template = FewShotPromptTemplate(
            examples=self.few_shot_examples,
            example_prompt=ChatPromptTemplate.from_template(
                "입력: {input}\n출력: {output}"
            ),
            prefix="다음은 주식 분석의 예제입니다:",
            suffix="입력: {input}\n출력:",
            input_variables=["input"]
        )
        
        logger.info("프롬프트 템플릿 초기화 완료")
    
    def _init_chains(self):
        """체인 초기화"""
        
        # 기본 분석 체인
        self.basic_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.rising_stock_template,
            output_key="basic_analysis",
            verbose=True
        )
        
        # 급락 종목 분석 체인
        self.falling_analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.falling_stock_template,
            output_key="falling_analysis",
            verbose=True
        )
        
        # 순차적 분석 체인 (기본 분석 → 심화 분석 → 최종 보고서)
        self.sequential_chain = SequentialChain(
            chains=[
                self.basic_analysis_chain,
                # 추가 체인들을 여기에 연결
            ],
            input_variables=["stock_name", "stock_price", "stock_change", "stock_volume", "news_context"],
            output_variables=["basic_analysis"],
            verbose=True
        )
        
        # RAG 체인 (벡터 검색 + 생성)
        if self.vectorstore:
            self.rag_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type=settings.rag_chain_type,
                retriever=self.vectorstore.as_retriever(search_kwargs=settings.rag_search_kwargs),
                return_source_documents=True
            )
        
        logger.info("분석 체인 초기화 완료")
    
    def _format_news_for_ai(self, news_data: List[Dict[str, Any]]) -> str:
        """뉴스 데이터를 AI 분석용으로 포맷팅"""
        if not news_data:
            return "관련 뉴스 정보가 없습니다."
        
        formatted_news = []
        for i, news in enumerate(news_data[:5], 1):  # 최대 5개 뉴스
            formatted_news.append(f"{i}. {news.get('title', '제목 없음')}")
            if news.get('content'):
                formatted_news.append(f"   내용: {news['content'][:200]}...")
        
        return "\n".join(formatted_news)
    
    def _add_to_knowledge_base(self, content: str, metadata: Dict[str, Any] = None):
        """지식 베이스에 내용 추가"""
        if not self.vectorstore:
            return
        
        try:
            # 텍스트 분할
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.max_chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
            
            # 문서 생성 및 추가
            from langchain.schema import Document
            documents = text_splitter.create_documents([content])
            
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            self.vectorstore.add_documents(documents)
            logger.info(f"지식 베이스에 내용 추가 완료: {len(documents)}개 문서")
            
        except Exception as e:
            logger.error(f"지식 베이스 추가 실패: {e}")
    
    async def analyze_stock_with_chain(self, stock: Stock, news_data: List[Dict[str, Any]] = None) -> str:
        """체인 기반 주식 분석"""
        try:
            # 뉴스 컨텍스트 준비
            news_context = self._format_news_for_ai(news_data) if news_data else "관련 뉴스 정보가 없습니다."
            
            # 체인 실행
            result = self.sequential_chain({
                "stock_name": stock.name,
                "stock_price": stock.price,
                "stock_change": stock.change,
                "stock_volume": stock.volume,
                "news_context": news_context
            })
            
            analysis = result.get("basic_analysis", "")
            
            # 분석 결과를 지식 베이스에 추가
            self._add_to_knowledge_base(
                analysis,
                {
                    "stock_name": stock.name,
                    "analysis_type": "rising" if not stock.change.startswith('-') else "falling",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"체인 기반 주식 분석 완료: {stock.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"체인 기반 분석 실패 ({stock.name}): {e}")
            raise OpenAIException(f"주식 분석에 실패했습니다: {str(e)}")
    
    async def analyze_falling_stock_with_chain(self, stock: Stock, news_data: List[Dict[str, Any]] = None) -> str:
        """체인 기반 급락 종목 분석"""
        try:
            # 뉴스 컨텍스트 준비
            news_context = self._format_news_for_ai(news_data) if news_data else "관련 뉴스 정보가 없습니다."
            
            # 급락 종목 분석 체인 실행
            result = self.falling_analysis_chain({
                "stock_name": stock.name,
                "stock_price": stock.price,
                "stock_change": stock.change,
                "stock_volume": stock.volume,
                "news_context": news_context
            })
            
            analysis = result.get("falling_analysis", "")
            
            # 분석 결과를 지식 베이스에 추가
            self._add_to_knowledge_base(
                analysis,
                {
                    "stock_name": stock.name,
                    "analysis_type": "falling",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"체인 기반 급락 종목 분석 완료: {stock.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"체인 기반 급락 종목 분석 실패 ({stock.name}): {e}")
            raise OpenAIException(f"급락 종목 분석에 실패했습니다: {str(e)}")
    
    async def get_contextual_analysis(self, query: str) -> str:
        """컨텍스트 기반 분석 (RAG)"""
        if not self.vectorstore or not self.rag_chain:
            return "RAG 시스템이 초기화되지 않았습니다."
        
        try:
            result = self.rag_chain({"query": query})
            return result["result"]
        except Exception as e:
            logger.error(f"RAG 분석 실패: {e}")
            return f"분석 중 오류가 발생했습니다: {str(e)}"
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """대화 기록 반환"""
        return self.memory.chat_memory.messages
    
    def clear_memory(self):
        """메모리 초기화"""
        self.memory.clear()
        logger.info("메모리 초기화 완료")
    
    def get_vectorstore_stats(self) -> Dict[str, Any]:
        """벡터 스토어 통계 정보"""
        if not self.vectorstore:
            return {"status": "not_initialized"}
        
        try:
            # 벡터 스토어의 문서 수 반환
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "status": "active",
                "document_count": count,
                "collection_name": collection.name
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
