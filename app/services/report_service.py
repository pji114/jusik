import logging
import os
from typing import List
from datetime import datetime
from jinja2 import Template

from app.models.stock import Stock, StockAnalysis
from app.core.exceptions import AnalysisException

logger = logging.getLogger(__name__)


class ReportService:
    """보고서 생성 서비스"""
    
    def __init__(self):
        self.html_template = self._get_html_template()
    
    async def generate_html_report(
        self, 
        stocks: List[Stock], 
        analyses: List[StockAnalysis],
        use_ai: bool = True
    ) -> str:
        """HTML 보고서 생성"""
        try:
            today = datetime.today().strftime('%Y년 %m월 %d일')
            
            # 가장 급등률이 높은 종목 선택
            top_stock = stocks[0] if stocks else None
            top_analysis = analyses[0] if analyses else None
            
            if not top_stock or not top_analysis:
                raise AnalysisException("보고서 생성에 필요한 데이터가 없습니다.")
            
            # AI 분석 결과가 있으면 사용, 없으면 기본 분석 사용
            ai_analysis = top_analysis.ai_analysis if use_ai and top_analysis.ai_analysis else self._get_fallback_analysis(top_stock, top_analysis)
            
            template = Template(self.html_template)
            html_content = template.render(
                today=today,
                stock=top_stock,
                analysis=top_analysis,
                ai_analysis=ai_analysis,
                all_stocks=stocks,
                all_analyses=analyses,
                use_ai=use_ai
            )
            
            logger.info(f"HTML 보고서 생성 완료: {top_stock.name}")
            return html_content
            
        except Exception as e:
            logger.error(f"HTML 보고서 생성 실패: {e}")
            raise AnalysisException(f"보고서 생성에 실패했습니다: {str(e)}")
    
    def _get_fallback_analysis(self, stock: Stock, analysis: StockAnalysis) -> str:
        """AI 분석이 없을 때 사용할 기본 분석"""
        return f"""
        <div class="analysis-content">
            <h4>📊 기본 분석</h4>
            <p><strong>등락률:</strong> {stock.change} - {analysis.basic_analysis}</p>
            <p><strong>급등 특성:</strong> {analysis.urgency}</p>
            
            <h4>📈 거래량 분석</h4>
            <p><strong>거래량:</strong> {stock.volume}</p>
            <p>{analysis.volume_analysis}</p>
            
            <h4>📰 관련 뉴스</h4>
            <div class="news-section">
                {self._format_news_list(analysis.news_list)}
            </div>
            
            <h4>⚠️ 투자 위험도</h4>
            <p><strong>위험도:</strong> {analysis.risk_level}</p>
            
            <h4>💡 투자자 유의사항</h4>
            <ul>
                <li>급등 종목은 변동성이 크므로 신중한 투자 결정이 필요합니다</li>
                <li>실적, 뉴스, 시장 상황을 종합적으로 고려하세요</li>
                <li>분산투자를 통해 리스크를 관리하세요</li>
                <li>단기 투자보다는 중장기 관점에서 검토해보세요</li>
            </ul>
        </div>
        """
    
    def _format_news_list(self, news_list) -> str:
        """뉴스 리스트를 HTML로 포맷팅"""
        if not news_list:
            return '<p><em>최신 뉴스 정보를 찾을 수 없습니다.</em></p>'
        
        news_html = ""
        for news in news_list:
            news_html += f"""
                <div class="news-item">
                    <strong>{news.title}</strong><br>
                    <small>{news.desc}</small>
                </div>
            """
        return news_html

    async def save_html_report(self, html_content: str, use_ai: bool = True) -> str:
        """HTML 보고서를 report 폴더에 저장"""
        try:
            # report 폴더가 없으면 생성
            report_dir = "report"
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            analysis_type = "AI분석" if use_ai else "기본분석"
            filename = f"급등종목_{analysis_type}_{timestamp}.html"
            filepath = os.path.join(report_dir, filename)
            
            # 파일 저장
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.info(f"HTML 보고서 저장 완료: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"HTML 보고서 저장 실패: {e}")
            raise AnalysisException(f"보고서 저장에 실패했습니다: {str(e)}")

    def _get_html_template(self) -> str:
        """HTML 템플릿 반환"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{{ today }} 급등종목 심층분석</title>
            <style>
                body { 
                    font-family: 'Apple SD Gothic Neo', sans-serif; 
                    padding: 20px; 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    line-height: 1.6;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                }
                .stock-card { 
                    background-color: #f8f9fa; 
                    padding: 25px; 
                    margin: 20px 0; 
                    border-radius: 15px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                .basic-info {
                    background-color: #e3f2fd;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 15px 0;
                }
                .analysis { 
                    background-color: #fff; 
                    padding: 20px; 
                    border-left: 5px solid #007bff; 
                    margin: 15px 0;
                    border-radius: 5px;
                }
                .analysis-content h4 { 
                    color: #333; 
                    margin-top: 20px; 
                    border-bottom: 2px solid #e9ecef; 
                    padding-bottom: 8px;
                    font-size: 1.2em;
                }
                .analysis-content ul { 
                    margin: 10px 0; 
                    padding-left: 20px; 
                }
                .analysis-content li { 
                    margin: 8px 0; 
                    line-height: 1.6; 
                }
                .news-section { 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 15px 0; 
                }
                .news-item {
                    background-color: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid #007bff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                .news-item small { 
                    color: #666; 
                    font-size: 0.9em; 
                }
                .notice { 
                    background-color: #e3f2fd; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin-top: 25px;
                    border-left: 4px solid #2196f3;
                }
                .notice em { 
                    color: #666; 
                }
                .highlight { 
                    background-color: #fff3cd; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 15px 0;
                    border-left: 4px solid #ffc107;
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
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }
                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 {{ today }} 급등종목 심층분석 보고서</h1>
                <p>AI 기반 주식 분석 플랫폼</p>
            </div>
            
            <div class="stock-card">
                <h2>⭐ {{ stock.name }} 종목분석</h2>
                
                <div class="basic-info">
                    <h3>📊 기본 정보</h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <h4>현재가</h4>
                            <p style="font-size: 1.5em; color: #333;">{{ stock.price }}원</p>
                        </div>
                        <div class="stat-card">
                            <h4>등락률</h4>
                            <p style="font-size: 1.5em; color: #dc3545;">{{ stock.change }}</p>
                        </div>
                        <div class="stat-card">
                            <h4>거래량</h4>
                            <p style="font-size: 1.5em; color: #333;">{{ stock.volume }}</p>
                        </div>
                    </div>
                </div>
                
                <div class="analysis">
                    <h3>🤖 {% if use_ai %}AI 심층분석{% else %}기본 분석{% endif %}</h3>
                    {{ ai_analysis | safe }}
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{{ stock.link }}" target="_blank" class="btn">
                        네이버 금융에서 자세히 보기 →
                    </a>
                </div>
            </div>
            
            {% if all_stocks|length > 1 %}
            <div class="stock-card">
                <h3>📈 전체 급등 종목 현황</h3>
                <div class="stats-grid">
                    {% for stock_item in all_stocks %}
                    <div class="stat-card">
                        <h4>{{ stock_item.name }}</h4>
                        <p><strong>등락률:</strong> <span style="color: #dc3545;">{{ stock_item.change }}</span></p>
                        <p><strong>거래량:</strong> {{ stock_item.volume }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            <div class="notice">
                <h4>📋 분석 참고사항</h4>
                <p><em>💻 참고: 이 분석은 기본적인 데이터와 뉴스 정보를 바탕으로 한 일반적인 안내입니다. 
                더 정확한 분석을 위해서는 전문가 상담이나 추가적인 정보 수집이 필요합니다.</em></p>
            </div>
        </body>
        </html>
        """
