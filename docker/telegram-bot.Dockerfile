# 텔레그램 봇 서비스 Dockerfile
FROM node:20-alpine

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY telegram-bot/package.json telegram-bot/package-lock.json* ./
RUN npm ci

# 애플리케이션 코드 복사
COPY telegram-bot/src ./src

# 로그 디렉토리 생성
RUN mkdir -p logs

# 환경 변수 설정
ENV NODE_ENV=production
ENV API_BASE_URL=http://backend:8000

# 포트 노출 (필요한 경우)
# EXPOSE 3000

# 애플리케이션 실행
CMD ["node", "src/index.js"]
