FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 필요한 Python 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app /app/app
RUN mkdir -p /app/data

# 환경 변수 설정
ENV PYTHONPATH=/app

# 디버깅을 위한 추가 설정
RUN echo "Python path:" && python -c "import sys; print(sys.path)"
RUN echo "Directory structure:" && find /app -type f | sort

# 포트 노출
EXPOSE 8000

# 기본 명령어 설정
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
