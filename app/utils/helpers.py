"""
유틸리티 함수들
"""

import re
from typing import List, Optional
from datetime import datetime


def clean_stock_name(name: str) -> str:
    """종목명 정리"""
    return name.strip().replace('\n', '').replace('\t', '')


def extract_change_percent(change_str: str) -> float:
    """등락률 문자열에서 숫자 추출"""
    try:
        # %, +, - 기호 제거
        cleaned = change_str.replace('%', '').replace('+', '').replace('-', '')
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0


def extract_volume_number(volume_str: str) -> int:
    """거래량 문자열에서 숫자 추출"""
    try:
        # 쉼표 제거
        cleaned = volume_str.replace(',', '').replace(' ', '')
        return int(cleaned)
    except (ValueError, AttributeError):
        return 0


def format_price(price_str: str) -> str:
    """가격 문자열 포맷팅"""
    try:
        # 숫자만 추출
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            return f"{int(numbers[0]):,}원"
        return price_str
    except:
        return price_str


def is_high_risk_stock(change_percent: float) -> bool:
    """고위험 종목 판단"""
    return change_percent >= 20.0


def is_medium_risk_stock(change_percent: float) -> bool:
    """중위험 종목 판단"""
    return 10.0 <= change_percent < 20.0


def get_risk_level(change_percent: float) -> str:
    """위험도 레벨 반환"""
    if change_percent >= 20:
        return "매우 높음"
    elif change_percent >= 10:
        return "높음"
    elif change_percent >= 5:
        return "보통"
    else:
        return "낮음"


def format_datetime(dt: datetime) -> str:
    """날짜시간 포맷팅"""
    return dt.strftime('%Y년 %m월 %d일 %H:%M:%S')


def truncate_text(text: str, max_length: int = 100) -> str:
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
