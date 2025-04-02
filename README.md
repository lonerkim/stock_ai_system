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
