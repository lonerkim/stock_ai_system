FROM node:20-alpine

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY package.json package-lock.json* ./
RUN npm ci

# 애플리케이션 코드 복사
COPY src ./src
COPY .env ./.env

# 로그 디렉토리 생성
RUN mkdir -p logs

# 환경 변수 설정
ENV NODE_ENV=production

# 애플리케이션 실행
CMD ["node", "src/index.js"]
