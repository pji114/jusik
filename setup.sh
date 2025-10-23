#!/bin/bash

# 주식 분석 API 설정 스크립트

echo "🔍 주식 분석 API 설정을 시작합니다..."

# 가상환경 생성
echo "📦 가상환경을 생성합니다..."
python3 -m venv venv

# 가상환경 활성화
echo "🔧 가상환경을 활성화합니다..."
source venv/bin/activate

# 의존성 설치
echo "📥 의존성을 설치합니다..."
pip install -r requirements.txt

# 환경변수 파일 생성
if [ ! -f .env ]; then
    echo "⚙️ 환경변수 파일을 생성합니다..."
    cp .env.example .env
    echo "✅ .env 파일이 생성되었습니다. OPENAI_API_KEY를 설정해주세요."
fi

echo ""
echo "🎉 설정이 완료되었습니다!"
echo ""
echo "🚀 서버를 실행하려면:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "📚 API 문서: http://localhost:8000/docs"
