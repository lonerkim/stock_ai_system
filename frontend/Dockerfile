# 빌드 단계
FROM node:20-alpine as build

WORKDIR /app

# 의존성 설치
COPY frontend/package.json ./
RUN npm install

# 소스 코드 복사 및 빌드
COPY frontend/src ./src
COPY frontend/public ./public

# 필요한 디렉토리 생성
RUN mkdir -p public

# package.json 파일 생성
COPY frontend/package.json ./

# 빌드 실행
RUN npm run build

# 실행 단계
FROM nginx:alpine

# 빌드된 파일을 Nginx 서버로 복사
COPY --from=build /app/build /usr/share/nginx/html

# Nginx 설정 파일 복사
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 포트 설정
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
