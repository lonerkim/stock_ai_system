# 주식 시장 AI 분석 시스템 - 백엔드

이 디렉토리는 주식 시장 AI 분석 시스템의 백엔드 서비스를 포함합니다.

## 설치 방법

### 1. 가상 환경 설정

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 가상 환경 활성화 (Linux/Mac)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.

```bash
cp .env.example .env
```

## 실행 방법

### 개발 모드로 실행

```bash
uvicorn app.main:app --reload
```

### 프로덕션 모드로 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 문서

서버가 실행되면 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 디렉토리 구조

- `app/`: 애플리케이션 코드
  - `ai_integration/`: AI 통합 모듈
  - `data_fetchers/`: 데이터 수집 모듈
  - `database/`: 데이터베이스 모듈
  - `embedding/`: 임베딩 및 RAG 모듈
  - `main.py`: 애플리케이션 진입점

## 필요한 외부 서비스

- Neo4j 데이터베이스
- (선택 사항) Redis 캐시 서버
- (선택 사항) OpenAI, Mistral, Gemini API 키
