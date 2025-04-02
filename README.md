<<<<<<< Updated upstream
<<<<<<< Updated upstream
# 주식 시장 정보 수집 및 AI 분석 시스템 배포 가이드

이 문서는 주식 시장 정보 수집 및 AI 분석 시스템의 배포 방법을 설명합니다.

## 시스템 개요

이 시스템은 다음과 같은 기능을 제공합니다:

1. 한국 및 미국 주식 시장 데이터 수집
2. 텍스트 임베딩 및 RAG 기반 정보 검색
3. AI 기반 투자 결정 및 모의 투자 포트폴리오 관리
4. 텔레그램 봇을 통한 사용자 인터페이스
5. Neo4j 데이터베이스를 활용한 데이터 저장 및 검색

## 배포 방법

### 사전 요구사항

- Docker 및 Docker Compose 설치
- 인터넷 연결
- 최소 4GB RAM, 2코어 CPU, 20GB 디스크 공간

### 설치 단계

1. 이 디렉토리의 모든 파일을 서버의 작업 디렉토리에 복사합니다.

2. 환경 변수 설정을 위해 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

3. `.env` 파일을 편집하여 필요한 API 키와 설정을 입력합니다:

```
# Neo4j 설정
NEO4J_PASSWORD=your_secure_password

# API 키
OPENAI_API_KEY=your_openai_api_key
MISTRAL_API_KEY=your_mistral_api_key
GOOGLE_API_KEY=your_google_api_key

# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_USER_IDS=your_telegram_user_id

# 주식 심볼 설정
US_STOCK_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,META
KR_STOCK_SYMBOLS=005930,000660,035420,051910,035720
```

4. 필요한 디렉토리 구조를 생성합니다:

```bash
mkdir -p app data
```

5. Docker 컨테이너를 빌드하고 시작합니다:

```bash
docker-compose build
docker-compose up -d
```

6. 로그를 확인하여 모든 서비스가 정상적으로 시작되었는지 확인합니다:

```bash
docker-compose logs -f
```

## 서비스 접근

- Neo4j 데이터베이스: http://your_server_ip:7474 (기본 사용자: neo4j, 비밀번호: `.env`에 설정한 값)
- API 서비스: http://your_server_ip:8000
- 텔레그램 봇: 텔레그램 앱에서 봇 토큰으로 생성된 봇을 검색하여 시작

## 문제 해결

### 모듈을 찾을 수 없는 오류

이 배포 솔루션은 Python 모듈 검색 경로 문제를 해결하기 위해 다음과 같은 방법을 사용합니다:

1. `PYTHONPATH=/app` 환경 변수 설정
2. `python -m` 접두사를 사용하여 모듈 실행
3. 볼륨 마운트 설정 최적화

### Neo4j 메모리 설정 오류

Neo4j 5.13.0 버전에서는 메모리 설정 환경 변수 이름이 변경되었습니다. 이 솔루션에서는 다음과 같이 올바른 형식을 사용합니다:

```
NEO4J_server_memory_heap_initial__size=1G
NEO4J_server_memory_heap_max__size=2G
```

### 기타 문제

문제가 발생하면 다음 명령어로 각 서비스의 로그를 확인하세요:

```bash
docker-compose logs app
docker-compose logs neo4j
docker-compose logs celery_worker
docker-compose logs telegram_bot
```

## 시스템 관리

### 서비스 재시작

```bash
docker-compose restart
```

### 서비스 중지

```bash
docker-compose down
```

### 데이터 백업

Neo4j 데이터를 백업하려면:

```bash
docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/data/backups/neo4j-backup.dump
```

## 추가 정보

더 자세한 정보는 프로젝트 문서를 참조하세요.
=======
=======
>>>>>>> Stashed changes
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
git clone https://github.com/yourusername/stock-market-ai.git
cd stock-market-ai
```

### 2. 환경 설정

```bash
# 환경 설정 스크립트 실행
chmod +x docker/setup.sh
./docker/setup.sh setup

# .env 파일 편집
nano docker/.env
```

### 3. 컨테이너 실행

```bash
# Docker 네트워크 생성
chmod +x docker/network.sh
./docker/network.sh create

# Docker Compose로 서비스 시작
cd docker
docker compose up -d
```

### 4. 접속 방법

- **웹 UI**: http://localhost:80 (또는 .env 파일에서 설정한 포트)
- **API 문서**: http://localhost:8000/docs
- **Neo4j 브라우저**: http://localhost:7474 (기본 사용자: neo4j, 비밀번호: .env 파일에서 설정)
- **텔레그램 봇**: .env 파일에 설정한 봇 토큰으로 텔레그램에서 접속

## 상세 설치 및 설정 가이드

자세한 설치 및 설정 방법은 [설치 가이드](docs/installation.md)를 참조하세요.

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

### 텔레그램 봇 사용법

1. 텔레그램에서 봇 검색 (봇 이름은 .env 파일에 설정한 토큰에 따라 다름)
2. `/start` 명령어로 봇 시작
3. `/help` 명령어로 사용 가능한 명령어 목록 확인
4. `/summary`, `/portfolio`, `/daily` 등의 명령어로 정보 요청

## 개발자 가이드

개발 환경 설정 및 코드 기여 방법은 [개발자 가이드](docs/developer-guide.md)를 참조하세요.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 면책 조항

이 프로젝트는 교육 목적으로만 제공됩니다. 실제 투자 결정에 사용하지 마세요. 모든 투자에는 위험이 따르며, 과거의 성과가 미래의 결과를 보장하지 않습니다.

## 제작자

이 프로젝트는 [Manus.ai](https://manus.ai/)에 의해 개발되었으며, 사용자에 의해 검증되거나 테스트되지 않았습니다. 모든 내용은 교육 목적으로만 제공됩니다.
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
