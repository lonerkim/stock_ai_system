"""
RAG 시스템과 Neo4j 통합 모듈

이 모듈은 RAG(Retrieval-Augmented Generation) 시스템과 Neo4j 데이터베이스를 통합합니다.
임베딩 검색, 관련 데이터 조회, 컨텍스트 생성 등의 기능을 제공합니다.
"""
import os
import logging
import json
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
import numpy as np

from ..embedding.text_embedding import TextEmbedding
from ..embedding.vector_store import VectorStore
from ..embedding.rag_pipeline import RAGPipeline
from ..embedding.search_engine import SearchEngine
from .repository import Neo4jRepository

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Neo4jRAGIntegration:
    """
    Neo4j와 RAG 시스템 통합 클래스
    """
    
    def __init__(
        self, 
        neo4j_repo: Neo4jRepository,
        text_embedding: TextEmbedding,
        vector_store: VectorStore,
        rag_pipeline: RAGPipeline
    ):
        """
        Neo4j RAG 통합 초기화
        
        Args:
            neo4j_repo: Neo4j 저장소
            text_embedding: 텍스트 임베딩 모듈
            vector_store: 벡터 저장소
            rag_pipeline: RAG 파이프라인
        """
        self.neo4j_repo = neo4j_repo
        self.text_embedding = text_embedding
        self.vector_store = vector_store
        self.rag_pipeline = rag_pipeline
        
        logger.info("Neo4j RAG 통합이 초기화되었습니다.")
    
    def index_market_summaries(self, market: str, limit: int = 10) -> int:
        """
        시장 요약 정보를 인덱싱합니다.
        
        Args:
            market: 시장 이름
            limit: 인덱싱할 요약 수
            
        Returns:
            인덱싱된 요약 수
        """
        try:
            # 시장 요약 정보 조회
            summaries = self.neo4j_repo.get_market_summaries(market, limit)
            
            indexed_count = 0
            
            for summary in summaries:
                # 임베딩 생성
                text = summary.get("summary_text", "")
                if not text:
                    continue
                
                embedding = self.text_embedding.embed_text(text)
                
                # 임베딩 저장 (Neo4j)
                embedding_data = {
                    "source": "market_summary",
                    "source_type": "market_summary",
                    "source_id": summary.get("id"),
                    "vector": embedding.tolist(),
                    "text": text,
                    "model": self.text_embedding.model_name
                }
                
                success = self.neo4j_repo.save_embedding(embedding_data)
                
                if success:
                    # 벡터 저장소에도 저장
                    self.vector_store.add_vector(
                        vector=embedding,
                        metadata={
                            "id": summary.get("id"),
                            "source": "market_summary",
                            "market": summary.get("market"),
                            "date": summary.get("date"),
                            "text": text
                        }
                    )
                    
                    indexed_count += 1
            
            logger.info(f"{indexed_count}개의 시장 요약 정보가 인덱싱되었습니다.")
            return indexed_count
        
        except Exception as e:
            logger.error(f"시장 요약 정보 인덱싱 중 오류 발생: {str(e)}")
            return 0
    
    def index_ai_analyses(self, analysis_type: str = None, limit: int = 10) -> int:
        """
        AI 분석 결과를 인덱싱합니다.
        
        Args:
            analysis_type: 분석 유형 (없으면 모든 유형)
            limit: 인덱싱할 분석 수
            
        Returns:
            인덱싱된 분석 수
        """
        try:
            # AI 분석 결과 조회
            analyses = self.neo4j_repo.get_ai_analyses(analysis_type, limit)
            
            indexed_count = 0
            
            for analysis in analyses:
                # 임베딩 생성
                text = analysis.get("analysis_text", "")
                if not text:
                    continue
                
                embedding = self.text_embedding.embed_text(text)
                
                # 임베딩 저장 (Neo4j)
                embedding_data = {
                    "source": "ai_analysis",
                    "source_type": "ai_analysis",
                    "source_id": analysis.get("id"),
                    "vector": embedding.tolist(),
                    "text": text,
                    "model": self.text_embedding.model_name
                }
                
                success = self.neo4j_repo.save_embedding(embedding_data)
                
                if success:
                    # 벡터 저장소에도 저장
                    self.vector_store.add_vector(
                        vector=embedding,
                        metadata={
                            "id": analysis.get("id"),
                            "source": "ai_analysis",
                            "analysis_type": analysis.get("analysis_type"),
                            "provider": analysis.get("provider"),
                            "timestamp": analysis.get("timestamp"),
                            "text": text
                        }
                    )
                    
                    indexed_count += 1
            
            logger.info(f"{indexed_count}개의 AI 분석 결과가 인덱싱되었습니다.")
            return indexed_count
        
        except Exception as e:
            logger.error(f"AI 분석 결과 인덱싱 중 오류 발생: {str(e)}")
            return 0
    
    def search_similar_content(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        유사한 콘텐츠를 검색합니다.
        
        Args:
            query: 검색 쿼리
            limit: 결과 제한 수
            
        Returns:
            유사한 콘텐츠 목록
        """
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.text_embedding.embed_text(query)
            
            # 벡터 저장소에서 검색
            results = self.vector_store.search(
                query_vector=query_embedding,
                limit=limit
            )
            
            # Neo4j에서도 검색
            neo4j_results = self.neo4j_repo.find_similar_embeddings(
                vector=query_embedding.tolist(),
                limit=limit
            )
            
            # 결과 병합 및 중복 제거
            combined_results = []
            seen_ids = set()
            
            # 벡터 저장소 결과 추가
            for result in results:
                result_id = result.get("metadata", {}).get("id")
                if result_id and result_id not in seen_ids:
                    seen_ids.add(result_id)
                    combined_results.append({
                        "id": result_id,
                        "source": result.get("metadata", {}).get("source"),
                        "text": result.get("metadata", {}).get("text"),
                        "similarity": result.get("score"),
                        "metadata": result.get("metadata", {})
                    })
            
            # Neo4j 결과 추가
            for result in neo4j_results:
                result_id = result.get("id")
                if result_id and result_id not in seen_ids:
                    seen_ids.add(result_id)
                    combined_results.append({
                        "id": result_id,
                        "source": result.get("source"),
                        "text": result.get("text"),
                        "similarity": result.get("similarity"),
                        "metadata": {
                            "source": result.get("source"),
                            "source_type": result.get("source_type"),
                            "model": result.get("model")
                        }
                    })
            
            # 유사도 기준 정렬
            combined_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
            
            # 결과 제한
            combined_results = combined_results[:limit]
            
            logger.info(f"유사한 콘텐츠 검색 성공: {len(combined_results)}개 결과")
            return combined_results
        
        except Exception as e:
            logger.error(f"유사한 콘텐츠 검색 중 오류 발생: {str(e)}")
            return []
    
    def generate_context(self, query: str, limit: int = 5) -> str:
        """
        RAG를 위한 컨텍스트를 생성합니다.
        
        Args:
            query: 쿼리
            limit: 결과 제한 수
            
        Returns:
            생성된 컨텍스트
        """
        try:
            # 유사한 콘텐츠 검색
            similar_contents = self.search_similar_content(query, limit)
            
            # 컨텍스트 생성
            context_parts = []
            
            for i, content in enumerate(similar_contents):
                text = content.get("text", "")
                source = content.get("source", "unknown")
                similarity = content.get("similarity", 0)
                
                context_part = f"[{i+1}] Source: {source}, Relevance: {similarity:.2f}\n{text}\n"
                context_parts.append(context_part)
            
            context = "\n".join(context_parts)
            
            logger.info(f"컨텍스트 생성 성공: {len(similar_contents)}개 콘텐츠")
            return context
        
        except Exception as e:
            logger.error(f"컨텍스트 생성 중 오류 발생: {str(e)}")
            return ""
    
    def rag_query(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        RAG 쿼리를 실행합니다.
        
        Args:
            query: 쿼리
            limit: 결과 제한 수
            
        Returns:
            RAG 쿼리 결과
        """
        try:
            # 컨텍스트 생성
            context = self.generate_context(query, limit)
            
            # RAG 파이프라인 실행
            result = self.rag_pipeline.run(query, context)
            
            logger.info(f"RAG 쿼리 실행 성공: {query}")
            return result
        
        except Exception as e:
            logger.error(f"RAG 쿼리 실행 중 오류 발생: {str(e)}")
            return {
                "query": query,
                "answer": f"오류가 발생했습니다: {str(e)}",
                "context": "",
                "sources": []
            }
    
    def analyze_market_with_rag(self, market: str, query: str = None) -> Dict[str, Any]:
        """
        RAG를 사용하여 시장을 분석합니다.
        
        Args:
            market: 시장 이름
            query: 분석 쿼리 (없으면 기본 쿼리 사용)
            
        Returns:
            분석 결과
        """
        try:
            # 기본 쿼리 설정
            if not query:
                query = f"{market} 시장의 현재 상황을 분석하고 주요 동향을 요약해주세요."
            
            # 최신 시장 요약 정보 조회
            summaries = self.neo4j_repo.get_market_summaries(market, 3)
            
            # 컨텍스트 생성
            context_parts = []
            
            for i, summary in enumerate(summaries):
                text = summary.get("summary_text", "")
                date = summary.get("date", "")
                
                context_part = f"[{i+1}] Date: {date}\n{text}\n"
                context_parts.append(context_part)
            
            context = "\n".join(context_parts)
            
            # RAG 파이프라인 실행
            result = self.rag_pipeline.run(query, context)
            
            # 분석 결과 저장
            analysis_data = {
                "timestamp": datetime.now().isoformat(),
                "provider": "RAG",
                "model": self.rag_pipeline.model_name,
                "analysis_type": "market_analysis",
                "analysis_text": result.get("answer", ""),
                "source_type": "market_summary",
                "source_id": summaries[0].get("id") if summaries else None
            }
            
            self.neo4j_repo.save_ai_analysis(analysis_data)
            
            logger.info(f"RAG를 사용한 시장 분석 성공: {market}")
            return result
        
        except Exception as e:
            logger.error(f"RAG를 사용한 시장 분석 중 오류 발생: {str(e)}")
            return {
                "query": query,
                "answer": f"오류가 발생했습니다: {str(e)}",
                "context": "",
                "sources": []
            }
    
    def recommend_stocks_with_rag(self, market: str, count: int = 5) -> Dict[str, Any]:
        """
        RAG를 사용하여 주식을 추천합니다.
        
        Args:
            market: 시장 이름
            count: 추천할 주식 수
            
        Returns:
            추천 결과
        """
        try:
            # 쿼리 설정
            query = f"{market} 시장에서 현재 투자 가치가 높은 블루칩 주식 {count}개를 추천해주세요."
            
            # 최신 시장 요약 정보 조회
            summaries = self.neo4j_repo.get_market_summaries(market, 3)
            
            # 최신 AI 분석 결과 조회
            analyses = self.neo4j_repo.get_ai_analyses("market_analysis", 2)
            
            # 컨텍스트 생성
            context_parts = []
            
            # 시장 요약 정보 추가
            for i, summary in enumerate(summaries):
                text = summary.get("summary_text", "")
                date = summary.get("date", "")
                
                context_part = f"[시장 요약 {i+1}] Date: {date}\n{text}\n"
                context_parts.append(context_part)
            
            # AI 분석 결과 추가
            for i, analysis in enumerate(analyses):
                text = analysis.get("analysis_text", "")
                timestamp = analysis.get("timestamp", "")
                
                context_part = f"[시장 분석 {i+1}] Timestamp: {timestamp}\n{text}\n"
                context_parts.append(context_part)
            
            context = "\n".join(context_parts)
            
            # RAG 파이프라인 실행
            result = self.rag_pipeline.run(query, context)
            
            # 분석 결과 저장
            analysis_data = {
                "timestamp": datetime.now().isoformat(),
                "provider": "RAG",
                "model": self.rag_pipeline.model_name,
                "analysis_type": "stock_recommendation",
                "analysis_text": result.get("answer", ""),
                "source_type": "market_summary",
                "source_id": summaries[0].get("id") if summaries else None
            }
            
            self.neo4j_repo.save_ai_analysis(analysis_data)
            
            logger.info(f"RAG를 사용한 주식 추천 성공: {market}")
            return result
        
        except Exception as e:
            logger.error(f"RAG를 사용한 주식 추천 중 오류 발생: {str(e)}")
            return {
                "query": query,
                "answer": f"오류가 발생했습니다: {str(e)}",
                "context": "",
                "sources": []
            }
    
    def make_investment_decision_with_rag(self, market: str, available_funds: float) -> Dict[str, Any]:
        """
        RAG를 사용하여 투자 결정을 내립니다.
        
        Args:
            market: 시장 이름
            available_funds: 사용 가능한 자금
            
        Returns:
            투자 결정
        """
        try:
            # 쿼리 설정
            query = f"{market} 시장에서 ${available_funds:.2f}의 자금을 어떻게 투자할지 결정해주세요. JSON 형식으로 응답해주세요."
            
            # 최신 시장 요약 정보 조회
            summaries = self.neo4j_repo.get_market_summaries(market, 2)
            
            # 최신 AI 분석 결과 조회
            analyses = self.neo4j_repo.get_ai_analyses("market_analysis", 1)
            
            # 최신 주식 추천 결과 조회
            recommendations = self.neo4j_repo.get_ai_analyses("stock_recommendation", 1)
            
            # 컨텍스트 생성
            context_parts = []
            
            # 시장 요약 정보 추가
            for i, summary in enumerate(summaries):
                text = summary.get("summary_text", "")
                date = summary.get("date", "")
                
                context_part = f"[시장 요약] Date: {date}\n{text}\n"
                context_parts.append(context_part)
            
            # AI 분석 결과 추가
            for analysis in analyses:
                text = analysis.get("analysis_text", "")
                context_part = f"[시장 분석]\n{text}\n"
                context_parts.append(context_part)
            
            # 주식 추천 결과 추가
            for recommendation in recommendations:
                text = recommendation.get("analysis_text", "")
                context_part = f"[주식 추천]\n{text}\n"
                context_parts.append(context_part)
            
            context = "\n".join(context_parts)
            
            # RAG 파이프라인 실행
            result = self.rag_pipeline.run(query, context)
            
            # 응답에서 JSON 추출
            answer = result.get("answer", "")
            
            try:
                # JSON 부분 추출
                json_start = answer.find("{")
                json_end = answer.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = answer[json_start:json_end]
                    decision = json.loads(json_str)
                else:
                    # JSON 형식이 아닌 경우
                    decision = {
                        "investments": [],
                        "cash_reserve": available_funds,
                        "strategy": "투자 결정을 파싱할 수 없습니다.",
                        "raw_response": answer
                    }
            except Exception as e:
                logger.warning(f"투자 결정 파싱 중 오류 발생: {str(e)}")
                decision = {
                    "investments": [],
                    "cash_reserve": available_funds,
                    "strategy": "투자 결정을 파싱할 수 없습니다.",
                    "raw_response": answer
                }
            
            # 메타데이터 추가
            decision["timestamp"] = datetime.now().isoformat()
            decision["provider"] = "RAG"
            decision["model"] = self.rag_pipeline.model_name
            decision["available_funds"] = available_funds
            
            # 분석 결과 저장
            analysis_data = {
                "timestamp": datetime.now().isoformat(),
                "provider": "RAG",
                "model": self.rag_pipeline.model_name,
                "analysis_type": "investment_decision",
                "analysis_text": answer,
                "source_type": "market_summary",
                "source_id": summaries[0].get("id") if summaries else None
            }
            
            analysis_id = str(datetime.now().timestamp())
            analysis_data["id"] = analysis_id
            
            self.neo4j_repo.save_ai_analysis(analysis_data)
            
            # 투자 결정 저장
            decision_data = {
                "timestamp": datetime.now().isoformat(),
                "provider": "RAG",
                "model": self.rag_pipeline.model_name,
                "available_funds": available_funds,
                "strategy": decision.get("strategy", ""),
                "analysis_id": analysis_id,
                "investments": decision.get("investments", [])
            }
            
            self.neo4j_repo.save_investment_decision(decision_data)
            
            logger.info(f"RAG를 사용한 투자 결정 성공: {market}")
            return decision
        
        except Exception as e:
            logger.error(f"RAG를 사용한 투자 결정 중 오류 발생: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "provider": "RAG",
                "model": self.rag_pipeline.model_name,
                "available_funds": available_funds,
                "investments": [],
                "cash_reserve": available_funds,
                "strategy": f"오류가 발생했습니다: {str(e)}",
                "error": str(e)
            }
