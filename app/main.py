"""
FastAPI 메인 애플리케이션 모듈
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Stock AI System",
    description="한국 및 미국 주식 시장 데이터 수집 및 AI 분석 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 상태 확인 엔드포인트
@app.get("/")
async def root():
    return {"status": "online", "message": "Stock AI System is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# API 버전 엔드포인트
@app.get("/version")
async def version():
    return {"version": "1.0.0"}

# 시작 이벤트
@app.on_event("startup")
async def startup_event():
    logger.info("Stock AI System 시작")
    # 여기에 시작 시 필요한 초기화 코드 추가

# 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stock AI System 종료")
    # 여기에 종료 시 필요한 정리 코드 추가

# 메인 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
