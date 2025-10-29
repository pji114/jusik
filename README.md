# 🔍 주식 분석 API (LangChain 고도화)

AI 기반 주식 분석 플랫폼으로, 네이버 금융 데이터를 활용한 급등/급락 종목 분석 서비스를 제공합니다. **LangChain**을 통한 고도화된 AI 분석 시스템을 지원합니다.

## ✨ 주요 기능

### 🚀 기본 기능
- **📈 급등 종목 조회**: 실시간 급등 종목 데이터 수집
- **📉 급락 종목 조회**: 실시간 급락 종목 데이터 수집
- **🤖 AI 분석**: OpenAI GPT를 활용한 종목 분석
- **📰 뉴스 수집**: 종목별 관련 뉴스 자동 수집
- **📊 보고서 생성**: HTML 형태의 종합 분석 보고서
- **🔍 시장 요약**: 전체 시장 동향 분석

### 🧠 LangChain 고도화 기능
- **🔗 체인 기반 분석**: 순차적 분석 워크플로우
- **🧠 RAG 시스템**: 벡터 스토어 기반 지식 검색
- **🤖 에이전트 시스템**: 전문 도구 기반 자동 분석
- **👥 멀티 에이전트**: 협업 분석 시스템
- **💾 메모리 관리**: 대화 기록 및 컨텍스트 유지
- **📚 지식 베이스**: 과거 분석 결과 학습 및 활용

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

### 🚀 기본 API

#### 급등 종목 조회
```http
GET /api/v1/stocks/rising?count=5
```

#### 급락 종목 조회
```http
GET /api/v1/stocks/falling?count=5
```

#### 종목 분석
```http
GET /api/v1/stocks/{stock_name}/analysis?use_ai=true
```

#### HTML 보고서 생성
```http
GET /api/v1/reports/html?count=3&use_ai=true&save_file=true
```

#### HTML 보고서 저장
```http
POST /api/v1/reports/save?count=3&use_ai=true
```

#### 시장 요약
```http
GET /api/v1/reports/summary?count=5
```

#### 종목 뉴스 조회
```http
GET /api/v1/stocks/{stock_name}/news
```

### 🎨 티스토리 블로그 최적화 API

#### 급등 종목 티스토리 HTML 생성
```http
GET /api/v1/reports/tistory?count=3&use_ai=true&save_file=true
```

#### 급등 종목 티스토리 HTML 저장
```http
POST /api/v1/reports/tistory/save?count=3&use_ai=true
```

#### 급락 종목 티스토리 HTML 생성
```http
GET /api/v1/reports/falling/tistory?count=3&use_ai=true&save_file=true
```

#### 급락 종목 티스토리 HTML 저장
```http
POST /api/v1/reports/falling/tistory/save?count=3&use_ai=true
```

### 🧠 LangChain 고급 API

#### 시스템 상태 확인
```http
GET /api/v1/langchain/langchain/status
```

#### RAG 기반 컨텍스트 분석
```http
POST /api/v1/langchain/contextual-analysis
Content-Type: application/json
{
  "query": "삼성전자 주가 분석",
  "context_type": "general"
}
```

#### 벡터 스토어 통계
```http
GET /api/v1/langchain/vectorstore/stats
```

#### 대화 기록 조회
```http
GET /api/v1/langchain/conversation/history
```

#### 메모리 초기화
```http
POST /api/v1/langchain/conversation/clear
```

#### 고급 주식 분석
```http
POST /api/v1/langchain/advanced-analysis?stock_name=삼성전자&analysis_depth=comprehensive&include_technical=true&include_fundamental=true&include_sentiment=true
```

#### 시장 인사이트 분석
```http
POST /api/v1/langchain/market-insights?sector=반도체&timeframe=daily
```

#### 위험도 평가
```http
POST /api/v1/langchain/risk-assessment?stock_name=삼성전자&risk_factors=["시장변동성","거래량급증"]
```

### 🤖 에이전트 API

#### 에이전트 기반 시장 분석
```http
POST /api/v1/langchain/agent/market-analysis?query=오늘 시장 동향 분석
```

#### 에이전트 기반 종목 분석
```http
POST /api/v1/langchain/agent/stock-analysis?stock_name=삼성전자
```

#### 멀티 에이전트 종합 분석
```http
POST /api/v1/langchain/multi-agent/comprehensive-analysis?query=삼성전자 종합 분석
```

#### 멀티 에이전트 협업 분석
```http
POST /api/v1/langchain/multi-agent/collaborative-analysis?stock_name=삼성전자
```

#### 에이전트 대화 기록
```http
GET /api/v1/langchain/agent/conversation-history
```

#### 에이전트 메모리 초기화
```http
POST /api/v1/langchain/agent/clear-memory
```

## 🏗️ 프로젝트 구조

```
app/
├── api/                           # API 라우터
│   └── v1/
│       ├── endpoints/            # 엔드포인트 정의
│       │   ├── stocks.py         # 주식 관련 API
│       │   ├── reports.py        # 보고서 생성 API
│       │   └── langchain.py      # LangChain 고급 API
│       └── api.py                # API 라우터 통합
├── core/                          # 핵심 설정
│   ├── config.py                 # 설정 관리 (LangChain 설정 포함)
│   └── exceptions.py             # 예외 처리
├── models/                        # Pydantic 모델
│   └── stock.py                  # 주식 관련 모델
├── services/                      # 비즈니스 로직
│   ├── stock_service.py          # 주식 데이터 서비스
│   ├── ai_service.py             # AI 분석 서비스 (LangChain 통합)
│   ├── langchain_ai_service.py   # LangChain 고도화 AI 서비스
│   ├── agent_service.py          # 에이전트 시스템 서비스
│   └── report_service.py         # 보고서 생성 서비스
├── chroma_db/                     # 벡터 스토어 데이터베이스
│   └── chroma.sqlite3            # ChromaDB 저장소
├── report/                        # 생성된 보고서 저장소
│   ├── 급등종목_티스토리_*.html   # 급등 종목 티스토리 보고서
│   └── 급락종목_티스토리_*.html   # 급락 종목 티스토리 보고서
└── main.py                       # FastAPI 앱 진입점
```

## 🔧 설정

### 환경 변수

#### 기본 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 키 | 필수 |
| `DEBUG` | 디버그 모드 | false |
| `APP_NAME` | 애플리케이션 이름 | 주식 분석 API |
| `REQUEST_TIMEOUT` | 요청 타임아웃 (초) | 30 |

#### LangChain 설정
| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `LANGCHAIN_ENABLED` | LangChain 기능 활성화 | true |
| `VECTORSTORE_PERSIST_DIRECTORY` | 벡터 스토어 저장 경로 | ./chroma_db |
| `EMBEDDING_MODEL` | 임베딩 모델 | text-embedding-ada-002 |
| `MAX_CHUNK_SIZE` | 텍스트 청크 크기 | 1000 |
| `CHUNK_OVERLAP` | 청크 겹침 크기 | 200 |
| `AGENT_VERBOSE` | 에이전트 상세 로그 | true |
| `AGENT_MAX_ITERATIONS` | 에이전트 최대 반복 | 10 |
| `AGENT_TIMEOUT` | 에이전트 타임아웃 (초) | 300 |

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

### 🚀 기본 API 사용 예시

#### Python 클라이언트 예시

```python
import requests

# 급등 종목 조회
response = requests.get("http://localhost:8000/api/v1/stocks/rising?count=5")
stocks = response.json()

# 급락 종목 조회
response = requests.get("http://localhost:8000/api/v1/stocks/falling?count=5")
falling_stocks = response.json()

# 종목 분석
response = requests.get("http://localhost:8000/api/v1/stocks/삼성전자/analysis?use_ai=true")
analysis = response.json()

# HTML 보고서 생성
response = requests.get("http://localhost:8000/api/v1/reports/html?count=3&use_ai=true")
html_report = response.text
```

#### cURL 예시

```bash
# 급등 종목 조회
curl "http://localhost:8000/api/v1/stocks/rising?count=5"

# 급락 종목 조회
curl "http://localhost:8000/api/v1/stocks/falling?count=5"

# 종목 분석
curl "http://localhost:8000/api/v1/stocks/삼성전자/analysis?use_ai=true"

# HTML 보고서 생성 및 저장
curl "http://localhost:8000/api/v1/reports/html?count=3&use_ai=true&save_file=true" -o report.html

# HTML 보고서를 report 폴더에 저장
curl -X POST "http://localhost:8000/api/v1/reports/save?count=3&use_ai=true"
```

### 🎨 티스토리 블로그 최적화 예시

```bash
# 급등 종목 티스토리 블로그용 HTML 생성 및 저장
curl -X POST "http://localhost:8000/api/v1/reports/tistory/save?count=5&use_ai=true"

# 급락 종목 티스토리 블로그용 HTML 생성 및 저장
curl -X POST "http://localhost:8000/api/v1/reports/falling/tistory/save?count=3&use_ai=true"

# 티스토리 HTML 직접 생성 (브라우저에서 확인)
curl "http://localhost:8000/api/v1/reports/tistory?count=3&use_ai=true" -o tistory_report.html
```

### 🧠 LangChain 고급 기능 예시

#### Python 클라이언트 예시

```python
import requests
import json

# LangChain 시스템 상태 확인
response = requests.get("http://localhost:8000/api/v1/langchain/langchain/status")
status = response.json()
print(f"LangChain 서비스 상태: {status['langchain_service']}")

# RAG 기반 컨텍스트 분석
query_data = {
    "query": "삼성전자 주가 분석",
    "context_type": "general"
}
response = requests.post(
    "http://localhost:8000/api/v1/langchain/contextual-analysis",
    json=query_data
)
analysis = response.json()
print(f"분석 결과: {analysis['analysis']}")

# 에이전트 기반 종목 분석
response = requests.post(
    "http://localhost:8000/api/v1/langchain/agent/stock-analysis",
    params={"stock_name": "삼성전자"}
)
agent_analysis = response.json()
print(f"에이전트 분석: {agent_analysis['analysis']}")

# 멀티 에이전트 협업 분석
response = requests.post(
    "http://localhost:8000/api/v1/langchain/multi-agent/collaborative-analysis",
    params={"stock_name": "삼성전자"}
)
multi_agent_result = response.json()
print(f"멀티 에이전트 분석: {multi_agent_result}")
```

#### cURL 예시

```bash
# LangChain 시스템 상태 확인
curl -X GET "http://localhost:8000/api/v1/langchain/langchain/status"

# RAG 기반 컨텍스트 분석
curl -X POST "http://localhost:8000/api/v1/langchain/contextual-analysis" \
  -H "Content-Type: application/json" \
  -d '{"query": "삼성전자 주가 분석", "context_type": "general"}'

# 벡터 스토어 통계 조회
curl -X GET "http://localhost:8000/api/v1/langchain/vectorstore/stats"

# 고급 주식 분석
curl -X POST "http://localhost:8000/api/v1/langchain/advanced-analysis?stock_name=삼성전자&analysis_depth=comprehensive&include_technical=true&include_fundamental=true&include_sentiment=true"

# 에이전트 기반 시장 분석
curl -X POST "http://localhost:8000/api/v1/langchain/agent/market-analysis?query=오늘 시장 동향 분석"

# 멀티 에이전트 종합 분석
curl -X POST "http://localhost:8000/api/v1/langchain/multi-agent/comprehensive-analysis?query=삼성전자 종합 분석"

# 시장 인사이트 분석
curl -X POST "http://localhost:8000/api/v1/langchain/market-insights?sector=반도체&timeframe=daily"

# 위험도 평가
curl -X POST "http://localhost:8000/api/v1/langchain/risk-assessment?stock_name=삼성전자&risk_factors=[\"시장변동성\",\"거래량급증\"]"
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

### LangChain 개발 가이드

#### 새로운 에이전트 추가

```python
# app/services/agent_service.py에 새로운 도구 추가
class CustomAnalysisTool(BaseTool):
    name: str = "custom_analyzer"
    description: str = "사용자 정의 분석 도구"
    
    def _run(self, input_data: str) -> str:
        # 분석 로직 구현
        return analysis_result
```

#### 새로운 체인 생성

```python
# app/services/langchain_ai_service.py에 새로운 체인 추가
custom_chain = LLMChain(
    llm=self.llm,
    prompt=custom_prompt_template,
    output_key="custom_analysis"
)
```

## 🔧 문제 해결

### 일반적인 문제들

#### 1. LangChain 서비스 초기화 실패
```bash
# OpenAI API 키 확인
echo $OPEN_AI_API_KEY

# 서버 재시작
pkill -f uvicorn
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 벡터 스토어 오류
```bash
# 벡터 스토어 초기화
rm -rf chroma_db/
# 서버 재시작하면 자동으로 재생성됨
```

#### 3. 메모리 부족 오류
```bash
# 에이전트 메모리 초기화
curl -X POST "http://localhost:8000/api/v1/langchain/agent/clear-memory"
```

## 📈 성능 최적화

### 벡터 스토어 최적화
- 청크 크기 조정: `MAX_CHUNK_SIZE` (기본값: 1000)
- 청크 겹침 조정: `CHUNK_OVERLAP` (기본값: 200)
- 검색 결과 수 조정: `RAG_SEARCH_KWARGS` (기본값: {"k": 3})

### 에이전트 최적화
- 최대 반복 수 조정: `AGENT_MAX_ITERATIONS` (기본값: 10)
- 타임아웃 조정: `AGENT_TIMEOUT` (기본값: 300초)