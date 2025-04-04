# 빌드 단계
FROM node:20-alpine as build

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

# 실행 단계
FROM nginx:alpine

# 빌드된 파일을 Nginx 서버로 복사
COPY --from=build /app/build /usr/share/nginx/html

# Nginx 설정 파일 복사 (필요한 경우)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 설정
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
