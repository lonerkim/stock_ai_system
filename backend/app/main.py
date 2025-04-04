"""
주식 시장 AI 분석 시스템 백엔드 애플리케이션

이 모듈은 FastAPI 기반 백엔드 서비스의 진입점입니다.
API 라우트, 미들웨어, 의존성 주입 등을 설정합니다.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 내부 모듈 임포트
from app.database.repository import Neo4jRepository
from app.database.schema import Neo4jSchema
from app.embedding.text_embedding import EmbeddingFactory
from app.embedding.vector_store import VectorStoreFactory
from app.embedding.rag_pipeline import RAGPipeline
from app.embedding.search_engine import SearchEngine
from app.ai_integration.ai_provider import AIProviderFactory
from app.ai_integration.mock_investment_adapter import MockInvestmentManager, PerformanceTracker
from app.data_fetchers.KoreanMarketDataFetcher import KoreanMarketDataFetcher
from app.data_fetchers.USMarketDataFetcher import USMarketDataFetcher
from app.data_fetchers.data_cache import DataCache
from app.data_fetchers.data_processor import DataProcessor

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="주식 시장 AI 분석 시스템 API",
    description="한국과 미국 주식 시장 데이터를 수집하고 임베딩하여 RAG 기반 분석 및 투자 추천을 제공하는 API",
    version="0.1.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 오리진으로 제한해야 함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터베이스 연결 설정
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# AI API 키 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LOCAL_AI_ENDPOINT = os.getenv("LOCAL_AI_ENDPOINT", "http://localhost:11434")

# 글로벌 객체
neo4j_repo = Neo4jRepository(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
neo4j_schema = Neo4jSchema(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
data_cache = DataCache()
data_processor = DataProcessor()
korean_market = KoreanMarketDataFetcher(data_cache)
us_market = USMarketDataFetcher(data_cache)
mock_investment = MockInvestmentManager(neo4j_repo)
performance_tracker = PerformanceTracker(neo4j_repo)

# 임베딩 및 RAG 설정
embedding_model = EmbeddingFactory.create_embedding_model(
    provider_type="openai" if OPENAI_API_KEY else "local",
    api_key=OPENAI_API_KEY,
    api_url=LOCAL_AI_ENDPOINT if not OPENAI_API_KEY else None
)

vector_store = VectorStoreFactory.create_vector_store(
    store_type="neo4j",
    uri=NEO4J_URI,
    username=NEO4J_USER,
    password=NEO4J_PASSWORD,
    dimension=1536  # OpenAI 임베딩 차원
)

rag_pipeline = RAGPipeline(embedding_model, vector_store)
search_engine = SearchEngine(rag_pipeline)

# 의존성 주입 함수
def get_neo4j_repo():
    try:
        neo4j_repo.connect()
        yield neo4j_repo
    finally:
        neo4j_repo.close()

def get_ai_provider(provider_type: str = "openai"):
    """
    AI 제공자를 가져옵니다.

    Args:
        provider_type: AI 제공자 유형 ('openai', 'mistral', 'gemini', 'local')

    Returns:
        AI 제공자 인스턴스
    """
    try:
        if provider_type == "openai" and OPENAI_API_KEY:
            return AIProviderFactory.create_ai_provider(
                provider_type="openai",
                api_key=OPENAI_API_KEY
            )
        elif provider_type == "mistral" and MISTRAL_API_KEY:
            return AIProviderFactory.create_ai_provider(
                provider_type="mistral",
                api_key=MISTRAL_API_KEY
            )
        elif provider_type == "gemini" and GEMINI_API_KEY:
            return AIProviderFactory.create_ai_provider(
                provider_type="gemini",
                api_key=GEMINI_API_KEY
            )
        elif provider_type == "local":
            return AIProviderFactory.create_ai_provider(
                provider_type="local",
                api_url=LOCAL_AI_ENDPOINT
            )
        else:
            # 기본값으로 OpenAI 사용
            return AIProviderFactory.create_ai_provider(
                provider_type="openai",
                api_key=OPENAI_API_KEY
            )
    except Exception as e:
        logger.error(f"AI 제공자 생성 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 제공자 생성 중 오류 발생: {str(e)}"
        )

# 모델 정의
class MarketDataRequest(BaseModel):
    market: str = Field(..., description="시장 유형 ('korean' 또는 'us')")
    symbol: Optional[str] = Field(None, description="주식 심볼 (선택 사항)")
    start_date: Optional[str] = Field(None, description="시작 날짜 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="종료 날짜 (YYYY-MM-DD)")

class AIAnalysisRequest(BaseModel):
    market_data: Dict[str, Any] = Field(..., description="분석할 시장 데이터")
    provider_type: str = Field("openai", description="AI 제공자 유형 ('openai', 'mistral', 'gemini', 'local')")

class StockRecommendationRequest(BaseModel):
    market_data: Dict[str, Any] = Field(..., description="분석할 시장 데이터")
    count: int = Field(5, description="추천할 주식 수")
    provider_type: str = Field("openai", description="AI 제공자 유형 ('openai', 'mistral', 'gemini', 'local')")

class InvestmentDecisionRequest(BaseModel):
    market_data: Dict[str, Any] = Field(..., description="분석할 시장 데이터")
    available_funds: float = Field(..., description="사용 가능한 자금")
    provider_type: str = Field("openai", description="AI 제공자 유형 ('openai', 'mistral', 'gemini', 'local')")

class SearchRequest(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    limit: int = Field(10, description="결과 제한")

# 라우트 정의
@app.get("/")
async def root():
    """
    API 루트 엔드포인트
    """
    return {
        "message": "주식 시장 AI 분석 시스템 API에 오신 것을 환영합니다.",
        "version": "0.1.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """
    API 상태 확인 엔드포인트
    """
    # 데이터베이스 연결 확인
    db_connected = neo4j_repo.connect()
    neo4j_repo.close()

    # AI API 키 확인
    ai_providers = []
    if OPENAI_API_KEY:
        ai_providers.append("openai")
    if MISTRAL_API_KEY:
        ai_providers.append("mistral")
    if GEMINI_API_KEY:
        ai_providers.append("gemini")
    if LOCAL_AI_ENDPOINT:
        ai_providers.append("local")

    return {
        "status": "healthy",
        "database_connected": db_connected,
        "ai_providers_available": ai_providers,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/market/data")
async def get_market_data(request: MarketDataRequest):
    """
    시장 데이터를 가져옵니다.
    """
    try:
        if request.market.lower() == "korean":
            if request.symbol:
                data = korean_market.get_stock_data(request.symbol, request.start_date, request.end_date)
            else:
                data = korean_market.get_market_overview()
        elif request.market.lower() == "us":
            if request.symbol:
                data = us_market.get_stock_data(request.symbol, request.start_date, request.end_date)
            else:
                data = us_market.get_market_overview()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원되지 않는 시장 유형: {request.market}"
            )

        # 데이터 처리
        processed_data = data_processor.process_market_data(data)

        return processed_data

    except Exception as e:
        logger.error(f"시장 데이터 가져오기 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"시장 데이터 가져오기 중 오류 발생: {str(e)}"
        )

@app.post("/api/ai/analyze")
async def analyze_market(request: AIAnalysisRequest):
    """
    시장 데이터를 분석합니다.
    """
    try:
        ai_provider = get_ai_provider(request.provider_type)
        analysis = ai_provider.analyze_market(request.market_data)
        return analysis

    except Exception as e:
        logger.error(f"시장 분석 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"시장 분석 중 오류 발생: {str(e)}"
        )

@app.post("/api/ai/recommend")
async def recommend_stocks(request: StockRecommendationRequest):
    """
    투자할 주식을 추천합니다.
    """
    try:
        ai_provider = get_ai_provider(request.provider_type)
        recommendations = ai_provider.recommend_stocks(request.market_data, request.count)
        return recommendations

    except Exception as e:
        logger.error(f"주식 추천 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"주식 추천 중 오류 발생: {str(e)}"
        )

@app.post("/api/ai/invest")
async def make_investment_decision(request: InvestmentDecisionRequest):
    """
    투자 결정을 내립니다.
    """
    try:
        ai_provider = get_ai_provider(request.provider_type)
        decision = ai_provider.make_investment_decision(request.market_data, request.available_funds)

        # 모의 투자 기록
        mock_investment.record_investment_decision(decision)

        return decision

    except Exception as e:
        logger.error(f"투자 결정 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"투자 결정 중 오류 발생: {str(e)}"
        )

@app.get("/api/investment/performance")
async def get_investment_performance(
    period: str = "daily",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    투자 성과를 가져옵니다.
    """
    try:
        performance = performance_tracker.get_performance(period, start_date, end_date)
        return performance

    except Exception as e:
        logger.error(f"투자 성과 가져오기 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"투자 성과 가져오기 중 오류 발생: {str(e)}"
        )

@app.post("/api/search")
async def search_data(request: SearchRequest):
    """
    데이터를 검색합니다.
    """
    try:
        results = search_engine.search(request.query, request.limit)
        return {
            "query": request.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"데이터 검색 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 검색 중 오류 발생: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트 핸들러
    """
    try:
        # 데이터베이스 연결
        db_connected = neo4j_repo.connect()
        if not db_connected:
            logger.warning("Neo4j 데이터베이스 연결 실패")

        # 스키마 초기화
        neo4j_schema.initialize_schema()

        logger.info("애플리케이션이 시작되었습니다.")

    except Exception as e:
        logger.error(f"애플리케이션 시작 중 오류 발생: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행되는 이벤트 핸들러
    """
    try:
        # 데이터베이스 연결 종료
        neo4j_repo.close()

        logger.info("애플리케이션이 종료되었습니다.")

    except Exception as e:
        logger.error(f"애플리케이션 종료 중 오류 발생: {str(e)}")

# 애플리케이션 실행 (직접 실행 시)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
