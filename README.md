# 주식 시장 AI 분석 시스템

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)
![AI](https://img.shields.io/badge/AI-powered-orange.svg)

한국과 미국 주식 시장 데이터를 수집하고 임베딩하여 RAG(Retrieval-Augmented Generation) 기반 분석 및 투자 추천을 제공하는 시스템입니다.

## 주요 기능

- **주식 시장 데이터 수집**: 한국과 미국 주식 시장의 실시간 및 과거 데이터 수집
- **RAG 기반 분석**: 수집된 데이터를 임베딩하여 검색 가능한 형태로 저장하고, AI를 활용한 분석 제공
- **AI 통합**: OpenAI, Mistral, Gemini API 또는 로컬 AI 모델과 연동 가능
- **모의 투자**: AI가 분석한 결과를 바탕으로 $100부터 시작하는 모의 투자 기능
- **성과 추적**: 일별 투자 성과 추적 및 보고서 생성
- **다중 인터페이스**: 웹 UI 및 텔레그램 봇을 통한 접근 가능
- **Neo4j 데이터베이스**: 그래프 데이터베이스를 활용한 효율적인 데이터 저장 및 검색

## 시스템 아키텍처

시스템은 다음과 같은 주요 컴포넌트로 구성되어 있습니다:

1. **백엔드 서비스**: FastAPI 기반 RESTful API 서버
2. **프론트엔드**: React 기반 웹 인터페이스
3. **텔레그램 봇**: Node.js 기반 텔레그램 봇 서비스
4. **Neo4j 데이터베이스**: 그래프 데이터베이스
5. **Docker 컨테이너**: 모든 서비스를 컨테이너화하여 쉬운 배포 지원

## 설치 요구사항

- Docker 및 Docker Compose v2 (`docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, `docker-compose-plugin`)
- Debian Bookworm 기반 LXC 또는 호환 가능한 Linux 환경
- 인터넷 연결 (주식 데이터 수집 및 AI API 접근용)
- (선택 사항) 로컬 AI 모델 서버 (Ollama, LM Studio 등)

## 빠른 시작 가이드

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/stock_ai_system.git
cd stock_ai_system
```

### 2. 환경 설정

```bash
# .env 파일 편집
nano .env
```

### 3. 컨테이너 실행

```bash
# Docker Compose로 서비스 시작
docker compose up -d
```

### 4. 접속 방법

- **웹 UI**: http://localhost:3000
- **API 문서**: http://localhost:8000/docs
- **Neo4j 브라우저**: http://localhost:7474 (기본 사용자: neo4j, 비밀번호: password)

## 로컬 개발 환경 설정

### 백엔드

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상 환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
python run.py
```

### 프론트엔드

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

## API 키 설정

이 시스템은 다양한 AI 서비스와 연동할 수 있습니다:

1. **OpenAI API**: [OpenAI 웹사이트](https://platform.openai.com/)에서 API 키 발급
2. **Mistral API**: [Mistral 웹사이트](https://mistral.ai/)에서 API 키 발급
3. **Gemini API**: [Google AI Studio](https://makersuite.google.com/)에서 API 키 발급
4. **로컬 AI**: Ollama, LM Studio 등의 로컬 AI 서버 엔드포인트 설정

발급받은 API 키는 웹 UI의 설정 페이지 또는 .env 파일에 설정할 수 있습니다.

## 사용 방법

### 웹 UI 사용법

1. 웹 브라우저에서 http://localhost:80 접속
2. 설정 페이지에서 API 키 및 기본 설정 구성
3. 대시보드에서 시장 개요 및 추천 종목 확인
4. 모의 투자 페이지에서 AI 기반 투자 결정 및 성과 추적





## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 면책 조항

이 프로젝트는 교육 목적으로만 제공됩니다. 실제 투자 결정에 사용하지 마세요. 모든 투자에는 위험이 따르며, 과거의 성과가 미래의 결과를 보장하지 않습니다.


