# 개발 환경 설정 계획

## 로컬 개발 환경
개발자가 로컬에서 개발할 때 필요한 환경 설정입니다.

### 필수 소프트웨어
- Python 3.10+
- Node.js 16+
- Docker 및 Docker Compose v2
- Git

### Python 가상 환경 설정
```bash
# 가상 환경 생성
python -m venv venv
# 가상 환경 활성화 (Linux/Mac)
source venv/bin/activate
# 가상 환경 활성화 (Windows)
venv\Scripts\activate
```

### 백엔드 의존성
```
fastapi==0.104.1
uvicorn==0.23.2
pydantic==2.4.2
python-dotenv==1.0.0
httpx==0.25.0
pandas==2.1.1
numpy==1.26.0
sentence-transformers==2.2.2
transformers==4.34.1
openai==1.2.0
neo4j==5.14.0
redis==5.0.1
celery==5.3.4
python-telegram-bot==20.6
```

### 프론트엔드 의존성
```
react==18.2.0
react-dom==18.2.0
redux==4.2.1
react-redux==8.1.3
@mui/material==5.14.18
chart.js==4.4.0
axios==1.6.0
```

## Docker 개발 환경
Docker를 사용한 개발 환경 설정입니다.

### 서비스 구성
- Backend API 서비스
- Frontend 서비스
- Neo4j 데이터베이스
- Redis 캐시
- RabbitMQ 메시지 브로커
- Celery 워커
- Telegram Bot 서비스

### 네트워크 구성
- 백엔드 네트워크: 백엔드, Neo4j, Redis, RabbitMQ, Celery 워커 연결
- 프론트엔드 네트워크: 프론트엔드, 백엔드 연결
- 외부 네트워크: 텔레그램 봇, 백엔드 연결

## 배포 환경
Debian Bookworm 기반 LXC 컨테이너에 배포하기 위한 환경 설정입니다.

### 필수 패키지
```bash
# 시스템 업데이트
apt-get update && apt-get upgrade -y

# 기본 도구 설치
apt-get install -y curl wget git build-essential

# Docker 설치 준비
apt-get install -y apt-transport-https ca-certificates gnupg lsb-release

# Docker GPG 키 추가
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker 저장소 추가
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker 설치
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Docker 사용자 그룹 설정
usermod -aG docker $USER
```

### 환경 변수 설정
배포 환경에서 필요한 환경 변수를 `.env` 파일로 관리합니다.

```
# 기본 설정
ENV=production
DEBUG=false
LOG_LEVEL=info

# API 키 설정
OPENAI_API_KEY=your_openai_api_key
MISTRAL_API_KEY=your_mistral_api_key
GEMINI_API_KEY=your_gemini_api_key

# 데이터베이스 설정
NEO4J_URI=neo4j://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# Redis 설정
REDIS_HOST=redis
REDIS_PORT=6379

# RabbitMQ 설정
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# 웹 서비스 설정
BACKEND_URL=http://backend:8000
FRONTEND_URL=http://frontend:3000
```

## CI/CD 파이프라인 (선택 사항)
지속적 통합 및 배포를 위한 파이프라인 설정입니다.

### GitHub Actions 워크플로우
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Test with pytest
        run: |
          pytest --cov=./ --cov-report=xml
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker images
        uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          tags: stock-market-ai:latest
```

## 모니터링 및 로깅 (선택 사항)
시스템 모니터링 및 로깅을 위한 설정입니다.

### ELK 스택 설정
```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.17.0
    depends_on:
      - elasticsearch
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline

  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    depends_on:
      - elasticsearch
    ports:
      - "5601:5601"

volumes:
  elasticsearch-data:
```
