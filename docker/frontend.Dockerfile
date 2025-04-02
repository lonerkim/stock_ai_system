# 프론트엔드 서비스 Dockerfile
FROM node:20-alpine as build

WORKDIR /app

# 의존성 파일 복사 및 설치
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# 애플리케이션 코드 복사
COPY frontend/src ./src
COPY frontend/public ./public

# 환경 변수 설정
ENV NODE_ENV=production
ENV REACT_APP_API_URL=http://backend:8000

# 애플리케이션 빌드
RUN npm run build

# 프로덕션 환경을 위한 Nginx 설정
FROM nginx:alpine

# Nginx 설정 파일 복사
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일 복사
COPY --from=build /app/build /usr/share/nginx/html

# 포트 노출
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
