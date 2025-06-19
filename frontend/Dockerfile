# ----- 1. Build Stage -----
# Node.js 이미지를 사용하여 React 앱을 빌드합니다.
FROM node:18-alpine AS builder

WORKDIR /app

# 의존성 설치
COPY package.json ./
COPY package-lock.json ./
RUN npm install

# 소스 코드 복사
COPY . .

# React 앱 빌드
RUN npm run build

# ----- 2. Serve Stage -----
# 가벼운 Nginx 이미지를 사용하여 빌드된 정적 파일을 서비스합니다.
FROM nginx:stable-alpine

# builder 스테이지에서 빌드된 결과물을 Nginx의 기본 웹 루트로 복사
COPY --from=builder /app/build /usr/share/nginx/html

# CORS 문제와 API 요청을 해결하기 위한 Nginx 설정 파일 복사
# /api/로 시작하는 모든 요청을 백엔드 서버로 전달(proxy)합니다.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx가 80번 포트를 사용하도록 설정
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]