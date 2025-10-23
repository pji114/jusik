##미사용

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai
import os
from openai import OpenAI

# OpenAI API 키 설정 (환경변수에서 읽기)
import os
api_key = os.getenv('OPENAI_API_KEY', "your-openai-api-key-here")
openai.api_key = api_key
client = OpenAI(api_key=api_key)


def get_top_rising_stocks(count=5):
    url = 'https://finance.naver.com/sise/sise_rise.naver'
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(res.text, 'html.parser')

    table = soup.select('table.type_2 tr')[2:]  # 데이터가 있는 줄만 추출
    rising_stocks = []

    for row in table:
        cols = row.select('td')
        if len(cols) < 10:
            continue
        name = cols[1].text.strip()
        current_price = cols[2].text.strip()
        change_percent = cols[4].text.strip()  # 등락률은 컬럼 4
        volume = cols[5].text.strip()  # 거래량은 컬럼 5
        link = 'https://finance.naver.com' + cols[1].select_one('a')['href']
        
        rising_stocks.append({
            'name': name,
            'price': current_price,
            'change': change_percent,
            'volume': volume,
            'link': link
        })
        if len(rising_stocks) == count:
            break

    return rising_stocks


def get_stock_news(stock_name):
    """종목별 최신 뉴스 수집"""
    try:
        # 네이버 뉴스 검색
        search_url = f"https://search.naver.com/search.naver?where=news&query={stock_name}"
        res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 새로운 선택자 사용
        news_items = soup.select('.list_news')[:3]  # 최신 3개 뉴스
        news_list = []
        
        for item in news_items:
            # 뉴스 텍스트에서 제목과 내용 추출
            text = item.get_text().strip()
            if text and len(text) > 50:
                # 텍스트가 한 줄로 되어 있으므로 패턴으로 분리
                # "이수화학" 키워드 주변의 뉴스 제목들을 찾기
                import re
                
                # 이수화학 관련 뉴스 제목 패턴 찾기
                # 더 정확한 패턴으로 뉴스 제목 추출
                news_titles = []
                
                # 패턴 1: [언론사]제목 형태
                pattern1 = r'\[([^\]]+)\]([^가-힣]*이수화학[^가-힣]*[가-힣\s\d%.,()]+)'
                matches1 = re.findall(pattern1, text)
                for match in matches1:
                    if len(match[1]) > 10:
                        news_titles.append(match[1].strip())
                
                # 패턴 2: 이수화학으로 시작하는 제목
                pattern2 = r'이수화학[^가-힣]*([가-힣\s\d%.,()]{10,})'
                matches2 = re.findall(pattern2, text)
                for match in matches2:
                    if len(match) > 10 and '이수화학' not in match:
                        news_titles.append(f'이수화학 {match.strip()}')
                
                # 패턴 3: 특징주, 급등 등 키워드가 있는 제목
                pattern3 = r'([가-힣\s]*이수화학[가-힣\s\d%.,()]{5,})'
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
                    # 제목이 너무 길면 잘라내기
                    display_title = title[:80] + '...' if len(title) > 80 else title
                    
                    news_list.append({
                        'title': display_title,
                        'desc': f'이수화학 관련 뉴스: {title[:60]}...' if len(title) > 60 else f'이수화학 관련 뉴스: {title}'
                    })
        
        return news_list
    except Exception as e:
        print(f"뉴스 검색 오류: {e}")
        return []

def get_enhanced_analysis(stock_data):
    """향상된 종목 분석 (뉴스 포함)"""
    change_percent = stock_data['change'].replace('%', '').replace('+', '')
    try:
        change_value = float(change_percent)
    except:
        change_value = 0
    
    # 거래량 분석
    volume_str = stock_data['volume'].replace(',', '')
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
    news_list = get_stock_news(stock_data['name'])
    
    return f"""
    <div class="analysis-content">
        <h4>📊 기본 분석</h4>
        <p><strong>등락률:</strong> {stock_data['change']} - {analysis}</p>
        <p><strong>급등 특성:</strong> {urgency}</p>
        
        <h4>📈 거래량 분석</h4>
        <p><strong>거래량:</strong> {stock_data['volume']}</p>
        <p>{volume_analysis}</p>
        
        <h4>📰 관련 뉴스</h4>
        <div class="news-section">
    """ + (f"""
            <ul>
    """ + "".join([f"""
                <li>
                    <strong>{news['title']}</strong><br>
                    <small>{news['desc']}</small>
                </li>
    """ for news in news_list]) + f"""
            </ul>
    """ if news_list else """
            <p><em>최신 뉴스 정보를 찾을 수 없습니다.</em></p>
    """) + f"""
        </div>
        
        <h4>🔍 급등 원인 추정</h4>
        <ul>
    """ + (f"""
            <li><strong>뉴스 이슈:</strong> 관련 뉴스가 {len(news_list)}건 발견되어 뉴스 이슈가 급등 원인일 가능성이 높습니다.</li>
    """ if news_list else """
            <li><strong>뉴스 이슈:</strong> 관련 뉴스가 발견되지 않아 다른 요인을 고려해야 합니다.</li>
    """) + f"""
            <li><strong>거래량 패턴:</strong> {volume_analysis}</li>
            <li><strong>시장 상황:</strong> 전체 시장 상황과 업종별 동향을 확인이 필요합니다.</li>
            <li><strong>공시 정보:</strong> 공시정보센터에서 최근 공시사항을 확인해보세요.</li>
        </ul>
        
        <h4>⚠️ 투자 위험도</h4>
        <p><strong>위험도:</strong> {risk_level}</p>
        
        <h4>💡 투자자 유의사항</h4>
        <ul>
            <li>급등 종목은 변동성이 크므로 신중한 투자 결정이 필요합니다</li>
            <li>실적, 뉴스, 시장 상황을 종합적으로 고려하세요</li>
            <li>분산투자를 통해 리스크를 관리하세요</li>
            <li>단기 투자보다는 중장기 관점에서 검토해보세요</li>
            <li>공시정보센터(https://dart.fss.or.kr)에서 최근 공시사항을 확인하세요</li>
        </ul>
        
        <div class="notice">
            <p><em>💻 참고: 이 분석은 기본적인 데이터와 뉴스 정보를 바탕으로 한 일반적인 안내입니다. 
            더 정확한 분석을 위해서는 전문가 상담이나 추가적인 정보 수집이 필요합니다.</em></p>
        </div>
    </div>
    """

def get_fallback_analysis(stock_data):
    """API 없이 기본적인 종목 분석 제공 (향상된 버전)"""
    return get_enhanced_analysis(stock_data)


def get_stock_analysis_from_gpt(stock_data, force_ai=False):
    """ChatGPT에게 종목 분석 요청 (API 할당량 초과 시 대체 분석 제공)"""
    prompt = f"""
    다음은 오늘 한국 주식시장에서 급등한 종목의 정보입니다:
    
    종목명: {stock_data['name']}
    현재가: {stock_data['price']}원
    등락률: {stock_data['change']}
    거래량: {stock_data['volume']}
    
    위 종목에 대해 다음 내용을 분석해주세요:
    1. 급등 원인 분석
    2. 거래량 특징 분석
    3. 투자 위험도 평가
    4. 향후 전망
    5. 투자자 유의사항
    
    HTML 형식으로 작성해주세요.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # GPT-4에서 GPT-3.5-turbo로 변경
            messages=[
                {"role": "system", "content": "당신은 금융분석 전문가입니다. 주식 종목 분석을 전문적이고 객관적으로 제공합니다."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        if force_ai:
            return f"<p>AI 분석을 요청했지만 API 오류가 발생했습니다: {str(e)}</p>"
        else:
            # API 오류 시 대체 분석 제공
            return get_enhanced_analysis(stock_data)


def generate_html(stocks):
    today = datetime.today().strftime('%Y년 %m월 %d일')
    html = f"<h1>📈 {today} 코스피/코스닥 급등 종목 TOP {len(stocks)}</h1>\n"

    for stock in stocks:
        html += f"""
        <hr>
        <h2>🔺 {stock['name']}</h2>
        <ul>
            <li><strong>현재가:</strong> {stock['price']}원</li>
            <li><strong>등락률:</strong> <span style="color:red">{stock['change']}</span></li>
            <li><strong>거래량:</strong> {stock['volume']}</li>
            <li><strong>네이버 금융:</strong> <a href="{stock['link']}" target="_blank">종목 상세보기</a></li>
        </ul>
        <p><em>해당 종목은 당일 기준 상승률이 높은 종목입니다. 향후 투자 전 실적 및 뉴스 확인이 필요합니다.</em></p>
        """
    return html


def generate_enhanced_html(stocks, use_ai=True):
    """향상된 HTML 보고서 생성"""
    today = datetime.today().strftime('%Y년 %m월 %d일')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{today} 급등종목 심층분석</title>
        <style>
            body {{ font-family: 'Apple SD Gothic Neo', sans-serif; padding: 20px; max-width: 1000px; margin: 0 auto; }}
            .stock-card {{ background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 10px; }}
            .analysis {{ background-color: #fff; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0; }}
            .analysis-content h4 {{ color: #333; margin-top: 20px; border-bottom: 2px solid #e9ecef; padding-bottom: 5px; }}
            .analysis-content ul {{ margin: 10px 0; padding-left: 20px; }}
            .analysis-content li {{ margin: 8px 0; line-height: 1.5; }}
            .news-section {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .news-section ul {{ list-style: none; padding: 0; }}
            .news-section li {{ margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px; border-left: 3px solid #007bff; }}
            .news-section small {{ color: #666; font-size: 0.9em; }}
            .notice {{ background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            .notice em {{ color: #666; }}
            .highlight {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>🔍 {today} 급등종목 심층분석 보고서</h1>
    """
    
    # 가장 급등률이 높은 종목 선택 (첫 번째 종목)
    top_stock = stocks[0]
    
    # AI 분석 또는 대체 분석 선택
    if use_ai:
        gpt_analysis = get_stock_analysis_from_gpt(top_stock, force_ai=True)
    else:
        gpt_analysis = get_enhanced_analysis(top_stock)
    
    html += f"""
        <div class="stock-card">
            <h2>⭐ {top_stock['name']} 종목분석</h2>
            <div class="basic-info">
                <h3>📊 기본 정보</h3>
                <ul>
                    <li><strong>현재가:</strong> {top_stock['price']}원</li>
                    <li><strong>등락률:</strong> <span style="color:red">{top_stock['change']}</span></li>
                    <li><strong>거래량:</strong> {top_stock['volume']}</li>
                </ul>
            </div>
            
            <div class="analysis">
                <h3>🤖 AI 심층분석</h3>
                {gpt_analysis}
            </div>
            
            <p>
                <a href="{top_stock['link']}" target="_blank" style="
                    display: inline-block;
                    background-color: #007bff;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;">
                    네이버 금융에서 자세히 보기 →
                </a>
            </p>
        </div>
    """
    
    html += """
    </body>
    </html>
    """
    return html

def main(use_ai=True):
    rising_stocks = get_top_rising_stocks(count=1)  # 상위 1개 종목만 가져오기
    html_output = generate_enhanced_html(rising_stocks, use_ai=use_ai)
    
    analysis_type = "AI분석" if use_ai else "기본분석"
    filename = f"급등종목_{analysis_type}_{datetime.today().strftime('%Y%m%d')}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_output)
    
    print(f"{analysis_type} 보고서가 생성되었습니다: {filename}")

if __name__ == "__main__":
    import sys
    # 명령행 인수로 AI 사용 여부 결정
    use_ai = "--no-ai" not in sys.argv
    main(use_ai=use_ai)