# 설치 및 배포 가이드

이 문서는 주식 시장 AI 분석 시스템의 상세한 설치 및 배포 방법을 설명합니다.

## 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [Docker 설치](#docker-설치)
3. [시스템 설치](#시스템-설치)
4. [환경 설정](#환경-설정)
5. [서비스 실행](#서비스-실행)
6. [서비스 관리](#서비스-관리)
7. [백업 및 복원](#백업-및-복원)
8. [문제 해결](#문제-해결)

## 시스템 요구사항

### 하드웨어 요구사항
- CPU: 최소 2코어 (4코어 이상 권장)
- RAM: 최소 4GB (8GB 이상 권장)
- 저장 공간: 최소 20GB (SSD 권장)

### 소프트웨어 요구사항
- Debian Bookworm 기반 LXC 또는 호환 가능한 Linux 환경
- Docker 및 Docker Compose v2
- 인터넷 연결

## Docker 설치

Debian Bookworm에 Docker를 설치하는 방법은 다음과 같습니다:

```bash
# 이전 버전의 Docker 제거 (있는 경우)
sudo apt-get remove docker docker-engine docker.io containerd runc

# 필요한 패키지 설치
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Docker 공식 GPG 키 추가
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Docker 저장소 설정
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker 서비스 시작 및 활성화
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가 (sudo 없이 Docker 사용 가능)
sudo usermod -aG docker $USER
newgrp docker
```

설치가 완료되었는지 확인:

```bash
docker --version
docker compose version
```

## 시스템 설치

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/stock-market-ai.git
cd stock-market-ai
```

### 2. 디렉토리 구조 확인

시스템은 다음과 같은 디렉토리 구조를 가집니다:

```
stock-market-ai/
├── backend/           # 백엔드 서비스 코드
├── frontend/          # 프론트엔드 코드
├── telegram-bot/      # 텔레그램 봇 코드
├── data/              # 데이터 저장 디렉토리
├── logs/              # 로그 파일 디렉토리
├── docker/            # Docker 관련 파일
│   ├── docker-compose.yml
│   ├── .env.example
│   ├── setup.sh
│   ├── network.sh
│   └── ...
└── docs/              # 문서 파일
```

## 환경 설정

### 1. 설정 스크립트 실행

```bash
# 스크립트 실행 권한 부여
chmod +x docker/setup.sh
chmod +x docker/network.sh

# 환경 설정 스크립트 실행
./docker/setup.sh setup
```

이 스크립트는 다음 작업을 수행합니다:
- `.env` 파일 생성 (`.env.example`에서 복사)
- 필요한 디렉토리 생성 (data, logs)
- 설정 파일 검증

### 2. 환경 변수 설정

`.env` 파일을 편집하여 필요한 환경 변수를 설정합니다:

```bash
nano docker/.env
```

주요 설정 항목:
- `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j 데이터베이스 접근 정보
- `OPENAI_API_KEY`, `MISTRAL_API_KEY`, `GEMINI_API_KEY`: AI 서비스 API 키
- `LOCAL_AI_ENDPOINT`: 로컬 AI 서버 엔드포인트 (선택 사항)
- `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰
- `ALLOWED_CHAT_IDS`: 텔레그램 봇 접근 허용 채팅 ID 목록

### 3. 네트워크 설정

```bash
# Docker 네트워크 생성
./docker/network.sh create

# 네트워크 설정 검증
./docker/network.sh validate
```

## 서비스 실행

### 1. Docker Compose로 서비스 시작

```bash
cd docker
docker compose up -d
```

이 명령은 다음 서비스를 시작합니다:
- 백엔드 서비스 (FastAPI)
- 프론트엔드 서비스 (React + Nginx)
- 텔레그램 봇 서비스
- Neo4j 데이터베이스

### 2. 서비스 상태 확인

```bash
docker compose ps
```

모든 서비스가 `Up` 상태인지 확인합니다.

### 3. 로그 확인

```bash
# 모든 서비스의 로그 확인
docker compose logs

# 특정 서비스의 로그 확인
docker compose logs backend
docker compose logs frontend
docker compose logs telegram-bot
docker compose logs neo4j
```

## 서비스 관리

### 서비스 중지

```bash
docker compose stop
```

### 서비스 재시작

```bash
docker compose restart
```

### 특정 서비스만 재시작

```bash
docker compose restart backend
```

### 서비스 및 컨테이너 제거 (데이터 유지)

```bash
docker compose down
```

### 서비스, 컨테이너 및 볼륨 제거 (모든 데이터 삭제)

```bash
docker compose down -v
```

## 백업 및 복원

### Neo4j 데이터베이스 백업

```bash
# 백업 디렉토리 생성
mkdir -p backups

# Neo4j 데이터 백업
docker run --rm \
  --volumes-from stock-market-ai-neo4j \
  -v $(pwd)/backups:/backups \
  ubuntu tar cvf /backups/neo4j-data-backup-$(date +%Y%m%d).tar /data
```

### Neo4j 데이터베이스 복원

```bash
# Neo4j 서비스 중지
docker compose stop neo4j

# 데이터 복원
docker run --rm \
  --volumes-from stock-market-ai-neo4j \
  -v $(pwd)/backups:/backups \
  ubuntu bash -c "cd / && tar xvf /backups/neo4j-data-backup-YYYYMMDD.tar"

# Neo4j 서비스 재시작
docker compose start neo4j
```

## 문제 해결

### 일반적인 문제

#### 서비스가 시작되지 않는 경우

1. 로그 확인:
```bash
docker compose logs [service_name]
```

2. 환경 변수 설정 확인:
```bash
docker compose config
```

3. 네트워크 설정 확인:
```bash
./docker/network.sh check
```

#### Neo4j 연결 문제

1. Neo4j 서비스 상태 확인:
```bash
docker compose ps neo4j
```

2. Neo4j 로그 확인:
```bash
docker compose logs neo4j
```

3. Neo4j 인증 정보 확인:
```bash
grep NEO4J_AUTH docker/.env
```

#### 텔레그램 봇 연결 문제

1. 텔레그램 봇 토큰 확인:
```bash
grep TELEGRAM_BOT_TOKEN docker/.env
```

2. 텔레그램 봇 로그 확인:
```bash
docker compose logs telegram-bot
```

### 고급 문제 해결

더 복잡한 문제가 발생한 경우 다음 단계를 시도해 보세요:

1. 모든 서비스 재시작:
```bash
docker compose down
docker compose up -d
```

2. Docker 시스템 정리:
```bash
docker system prune -a
```

3. 컨테이너 내부 확인:
```bash
docker compose exec [service_name] bash
```

문제가 지속되면 GitHub 이슈를 통해 보고해 주세요.
