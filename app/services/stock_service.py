import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
from datetime import datetime

from app.models.stock import Stock, NewsItem, StockAnalysis
from app.core.config import settings
from app.core.exceptions import DataFetchException, AnalysisException

logger = logging.getLogger(__name__)


class StockService:
    """주식 데이터 수집 및 분석 서비스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def get_rising_stocks(self, count: int = 5) -> List[Stock]:
        """급등 종목 데이터 수집"""
        try:
            response = self.session.get(
                settings.naver_finance_url,
                timeout=settings.request_timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.select('table.type_2 tr')[2:]  # 데이터가 있는 줄만 추출
            
            rising_stocks = []
            
            for row in table:
                if len(rising_stocks) >= count:
                    break
                    
                cols = row.select('td')
                if len(cols) < 10:
                    continue
                    
                name = cols[1].text.strip()
                current_price = cols[2].text.strip()
                change_percent = cols[4].text.strip()
                volume = cols[5].text.strip()
                link = 'https://finance.naver.com' + cols[1].select_one('a')['href']
                
                stock = Stock(
                    name=name,
                    price=current_price,
                    change=change_percent,
                    volume=volume,
                    link=link,
                    created_at=datetime.now()
                )
                rising_stocks.append(stock)
            
            logger.info(f"수집된 급등 종목 수: {len(rising_stocks)}")
            return rising_stocks
            
        except requests.RequestException as e:
            logger.error(f"네이버 금융 데이터 수집 실패: {e}")
            raise DataFetchException(f"급등 종목 데이터 수집에 실패했습니다: {str(e)}")
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise DataFetchException(f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
    
    async def get_stock_news(self, stock_name: str) -> List[NewsItem]:
        """종목별 최신 뉴스 수집"""
        try:
            search_url = f"{settings.naver_news_url}?where=news&query={stock_name}"
            response = self.session.get(search_url, timeout=settings.request_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.select('.list_news')[:3]  # 최신 3개 뉴스
            news_list = []
            
            for item in news_items:
                text = item.get_text().strip()
                if text and len(text) > 50:
                    import re
                    
                    # 뉴스 제목 패턴 추출
                    news_titles = []
                    
                    # 패턴 1: [언론사]제목 형태
                    pattern1 = r'\[([^\]]+)\]([^가-힣]*' + re.escape(stock_name) + r'[^가-힣]*[가-힣\s\d%.,()]+)'
                    matches1 = re.findall(pattern1, text)
                    for match in matches1:
                        if len(match[1]) > 10:
                            news_titles.append(match[1].strip())
                    
                    # 패턴 2: 종목명으로 시작하는 제목
                    pattern2 = r'' + re.escape(stock_name) + r'[^가-힣]*([가-힣\s\d%.,()]{10,})'
                    matches2 = re.findall(pattern2, text)
                    for match in matches2:
                        if len(match) > 10 and stock_name not in match:
                            news_titles.append(f'{stock_name} {match.strip()}')
                    
                    # 패턴 3: 급등, 상한가 등 키워드가 있는 제목
                    pattern3 = r'([가-힣\s]*' + re.escape(stock_name) + r'[가-힣\s\d%.,()]{5,})'
                    matches3 = re.findall(pattern3, text)
                    for match in matches3:
                        if len(match) > 15 and any(keyword in match for keyword in ['급등', '상한가', '특징주', '폭등', '강세']):
                            news_titles.append(match.strip())
                    
                    # 중복 제거하고 최대 3개까지
                    unique_titles = []
                    seen = set()
                    for title in news_titles:
                        if title not in seen and len(title) > 10:
                            unique_titles.append(title)
                            seen.add(title)
                            if len(unique_titles) >= 3:
                                break
                    
                    for title in unique_titles:
                        display_title = title[:80] + '...' if len(title) > 80 else title
                        news_list.append(NewsItem(
                            title=display_title,
                            desc=f'{stock_name} 관련 뉴스: {title[:60]}...' if len(title) > 60 else f'{stock_name} 관련 뉴스: {title}'
                        ))
            
            logger.info(f"{stock_name} 뉴스 수집 완료: {len(news_list)}건")
            return news_list
            
        except requests.RequestException as e:
            logger.error(f"뉴스 수집 실패 ({stock_name}): {e}")
            return []
        except Exception as e:
            logger.error(f"뉴스 처리 오류 ({stock_name}): {e}")
            return []
    
    async def analyze_stock(self, stock: Stock, use_ai: bool = True) -> StockAnalysis:
        """종목 분석 수행"""
        try:
            # 기본 분석
            change_percent = stock.change.replace('%', '').replace('+', '')
            try:
                change_value = float(change_percent)
            except:
                change_value = 0
            
            # 거래량 분석
            volume_str = stock.volume.replace(',', '')
            try:
                volume_num = int(volume_str)
            except:
                volume_num = 0
            
            # 등락률에 따른 분석
            if change_value >= 20:
                risk_level = "매우 높음"
                analysis = "급등주로 분류되며, 높은 변동성을 보입니다."
                urgency = "상한가 근접으로 매우 주의가 필요합니다."
            elif change_value >= 10:
                risk_level = "높음"
                analysis = "상당한 상승을 보이며, 주의깊은 관찰이 필요합니다."
                urgency = "급등 패턴으로 신중한 접근이 필요합니다."
            elif change_value >= 5:
                risk_level = "보통"
                analysis = "안정적인 상승세를 보이고 있습니다."
                urgency = "점진적 상승으로 관심을 가져볼 만합니다."
            else:
                risk_level = "낮음"
                analysis = "점진적인 상승을 보이고 있습니다."
                urgency = "안정적인 상승세를 보이고 있습니다."
            
            # 거래량 분석
            if volume_num > 1000000:
                volume_analysis = "거래량이 매우 활발하여 관심도가 높습니다."
            elif volume_num > 100000:
                volume_analysis = "거래량이 평소보다 높아 관심이 증가하고 있습니다."
            else:
                volume_analysis = "거래량이 평소 수준입니다."
            
            # 뉴스 수집
            news_list = await self.get_stock_news(stock.name)
            
            # AI 분석 (선택적)
            ai_analysis = None
            if use_ai:
                try:
                    ai_analysis = await self._get_ai_analysis(stock)
                except Exception as e:
                    logger.warning(f"AI 분석 실패: {e}")
                    ai_analysis = "AI 분석을 사용할 수 없습니다."
            
            return StockAnalysis(
                basic_analysis=analysis,
                risk_level=risk_level,
                urgency=urgency,
                volume_analysis=volume_analysis,
                news_list=news_list,
                ai_analysis=ai_analysis
            )
            
        except Exception as e:
            logger.error(f"종목 분석 실패 ({stock.name}): {e}")
            raise AnalysisException(f"종목 분석에 실패했습니다: {str(e)}")
    
    async def _get_ai_analysis(self, stock: Stock) -> str:
        """OpenAI를 활용한 AI 분석"""
        from app.services.ai_service import AIService
        
        ai_service = AIService()
        return await ai_service.analyze_stock(stock)
