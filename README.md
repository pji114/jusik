# 🔍 주식 분석 API

AI 기반 주식 분석 플랫폼으로, 네이버 금융 데이터를 활용한 급등 종목 분석 서비스를 제공합니다.

## ✨ 주요 기능

- **📈 급등 종목 조회**: 실시간 급등 종목 데이터 수집
- **🤖 AI 분석**: OpenAI GPT를 활용한 종목 분석
- **📰 뉴스 수집**: 종목별 관련 뉴스 자동 수집
- **📊 보고서 생성**: HTML 형태의 종합 분석 보고서
- **🔍 시장 요약**: 전체 시장 동향 분석

## 🚀 빠른 시작

### 방법 1: 자동 설정 (권장)

```bash
# 설정 스크립트 실행
./setup.sh

# 가상환경 활성화 및 서버 실행
source venv/bin/activate
python3 run.py
```

### 방법 2: 수동 설정

#### 1. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate
```

#### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

#### 3. 환경 변수 설정

```bash
# 로컬 환경변수 설정 (터미널에서)
export OPEN_AI_API_KEY=your_openai_api_key_here

# 또는 .zshrc/.bashrc에 추가
echo 'export OPEN_AI_API_KEY=your_openai_api_key_here' >> ~/.zshrc
source ~/.zshrc

# .env 파일 복사
cp .env.example .env
```

#### 4. 서버 실행

```bash
# 개발 모드 (권장)
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 직접 실행
python3 run.py
```

### 4. API 문서 확인

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **메인 페이지**: http://localhost:8000

## 📚 API 엔드포인트

### 급등 종목 조회
```http
GET /api/v1/stocks/rising?count=5
```

### 종목 분석
```http
GET /api/v1/stocks/{stock_name}/analysis?use_ai=true
```

### HTML 보고서 생성
```http
GET /api/v1/reports/html?count=3&use_ai=true&save_file=true
```

### HTML 보고서 저장
```http
POST /api/v1/reports/save?count=3&use_ai=true
```

### 시장 요약
```http
GET /api/v1/reports/summary?count=5
```

### 종목 뉴스 조회
```http
GET /api/v1/stocks/{stock_name}/news
```

## 🏗️ 프로젝트 구조

```
app/
├── api/                    # API 라우터
│   └── v1/
│       ├── endpoints/      # 엔드포인트 정의
│       └── api.py         # API 라우터 통합
├── core/                  # 핵심 설정
│   ├── config.py          # 설정 관리
│   └── exceptions.py      # 예외 처리
├── models/                # Pydantic 모델
│   └── stock.py           # 주식 관련 모델
├── services/              # 비즈니스 로직
│   ├── stock_service.py   # 주식 데이터 서비스
│   ├── ai_service.py      # AI 분석 서비스
│   └── report_service.py  # 보고서 생성 서비스
└── main.py               # FastAPI 앱 진입점
```

## 🔧 설정

### 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | 필수 |
| `DEBUG` | 디버그 모드 | false |
| `APP_NAME` | 애플리케이션 이름 | 주식 분석 API |
| `REQUEST_TIMEOUT` | 요청 타임아웃 (초) | 30 |

### OpenAI API 설정

1. [OpenAI 웹사이트](https://platform.openai.com/)에서 API 키 발급
2. 로컬 환경변수 설정:
   ```bash
   # 터미널에서 실행
   export OPEN_AI_API_KEY=sk-your-api-key-here
   
   # 영구적으로 설정하려면
   echo 'export OPEN_AI_API_KEY=sk-your-api-key-here' >> ~/.zshrc
   source ~/.zshrc
   ```

## 📊 사용 예시

### Python 클라이언트 예시

```python
import requests

# 급등 종목 조회
response = requests.get("http://localhost:8000/api/v1/stocks/rising?count=5")
stocks = response.json()

# 종목 분석
response = requests.get("http://localhost:8000/api/v1/stocks/삼성전자/analysis")
analysis = response.json()

# HTML 보고서 생성
response = requests.get("http://localhost:8000/api/v1/reports/html?count=3")
html_report = response.text
```

### cURL 예시

```bash
# 급등 종목 조회
curl "http://localhost:8000/api/v1/stocks/rising?count=5"

# 종목 분석
curl "http://localhost:8000/api/v1/stocks/삼성전자/analysis?use_ai=true"

# HTML 보고서 생성 및 저장
curl "http://localhost:8000/api/v1/reports/html?count=3&use_ai=true&save_file=true" -o report.html

# HTML 보고서를 report 폴더에 저장
curl -X POST "http://localhost:8000/api/v1/reports/save?count=3&use_ai=true"

# 티스토리 금등 종목 블로깅용 HTML Report 폴더에 저장
curl -X POST "http://localhost:8000/api/v1/reports/tistory/save?count=5&use_ai=true"

## 티스토리 급락 종목 불로깅용 HTML Report 폴더에 저장
curl -X GET "http://localhost:8000/api/v1/reports/falling/tistory?count=5&use_ai=false"
```

## 🛠️ 개발

### 코드 스타일

- **Black**: 코드 포맷팅
- **isort**: import 정렬
- **flake8**: 린팅

### 테스트

```bash
# 테스트 실행 (추후 구현 예정)
pytest tests/
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해 주세요.

---

**⚡ Powered by FastAPI & OpenAI**
