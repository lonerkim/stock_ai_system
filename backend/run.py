"""
주식 시장 AI 분석 시스템 백엔드 실행 스크립트
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
