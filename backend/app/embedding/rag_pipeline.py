"""
RAG (Retrieval-Augmented Generation) 파이프라인 모듈

이 모듈은 주식 시장 데이터에 대한 RAG 파이프라인을 구현합니다.
텍스트 임베딩과 벡터 저장소를 활용하여 검색 기반 생성을 수행합니다.
"""
import os
import logging
import numpy as np
import json
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
import uuid

from .text_embedding import BaseEmbeddingModel, EmbeddingFactory
from .vector_store import BaseVectorStore, VectorStoreFactory

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockMarketRAG:
    """
    주식 시장 데이터를 위한 RAG 시스템
    """
    
    def __init__(
        self, 
        embedding_model: BaseEmbeddingModel, 
        vector_store: BaseVectorStore,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        주식 시장 RAG 시스템 초기화
        
        Args:
            embedding_model: 텍스트 임베딩 모델
            vector_store: 벡터 저장소
            chunk_size: 텍스트 청크 크기
            chunk_overlap: 텍스트 청크 간 중복 크기
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info("주식 시장 RAG 시스템이 초기화되었습니다.")
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        텍스트를 청크로 분할합니다.
        
        Args:
            text: 분할할 텍스트
            
        Returns:
            텍스트 청크 목록
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # 문장 경계에서 청크 종료
            if end < len(text):
                # 청크 크기 내에서 마지막 문장 끝 찾기
                last_period = text.rfind('.', start, end)
                if last_period > start + self.chunk_size // 2:
                    end = last_period + 1
            
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        
        return chunks
    
    def index_market_data(self, market_data: Dict[str, Any], market_type: str) -> List[str]:
        """
        시장 데이터를 인덱싱합니다.
        
        Args:
            market_data: 시장 데이터
            market_type: 시장 유형 ('korean', 'us')
            
        Returns:
            인덱싱된 벡터 ID 목록
        """
        try:
            logger.info(f"{market_type} 시장 데이터 인덱싱 시작...")
            
            all_vector_ids = []
            
            # 시장 요약 텍스트 인덱싱
            if 'summary_text' in market_data:
                summary_text = market_data['summary_text']
                summary_chunks = self._chunk_text(summary_text)
                
                for i, chunk in enumerate(summary_chunks):
                    # 임베딩 생성
                    embedding = self.embedding_model.embed_text(chunk)
                    
                    # 메타데이터 생성
                    metadata = {
                        "content_type": "summary",
                        "market": market_type,
                        "chunk_index": i,
                        "total_chunks": len(summary_chunks),
                        "timestamp": datetime.now().isoformat(),
                        "text": chunk
                    }
                    
                    # 벡터 저장소에 추가
                    vector_ids = self.vector_store.add_vectors([embedding], [metadata])
                    all_vector_ids.extend(vector_ids)
            
            # 지수 데이터 인덱싱
            if 'indices' in market_data:
                for index_name, index_data in market_data['indices'].items():
                    # 지수 설명 텍스트 생성
                    if 'dataframe' in index_data:
                        df = index_data['dataframe']
                        last_row = df.iloc[-1]
                        
                        index_text = f"{index_name} 지수 정보: "
                        index_text += f"최근 종가: {last_row.get('close', 'N/A')}, "
                        
                        if 'MA20' in last_row:
                            index_text += f"20일 이동평균: {last_row.get('MA20', 'N/A')}, "
                        
                        if 'RSI' in last_row:
                            index_text += f"RSI: {last_row.get('RSI', 'N/A')}, "
                        
                        if 'volatility_20d' in last_row:
                            index_text += f"20일 변동성: {last_row.get('volatility_20d', 'N/A')}, "
                        
                        # 임베딩 생성
                        embedding = self.embedding_model.embed_text(index_text)
                        
                        # 메타데이터 생성
                        metadata = {
                            "content_type": "index",
                            "market": market_type,
                            "index_name": index_name,
                            "timestamp": datetime.now().isoformat(),
                            "text": index_text
                        }
                        
                        # 벡터 저장소에 추가
                        vector_ids = self.vector_store.add_vectors([embedding], [metadata])
                        all_vector_ids.extend(vector_ids)
            
            # 주식 데이터 인덱싱
            if 'stocks' in market_data:
                for symbol, stock_data in market_data['stocks'].items():
                    # 주식 설명 텍스트 생성
                    if 'dataframe' in stock_data:
                        df = stock_data['dataframe']
                        last_row = df.iloc[-1]
                        
                        stock_text = f"{symbol} 주식 정보: "
                        stock_text += f"최근 종가: {last_row.get('close', 'N/A')}, "
                        
                        if 'MA20' in last_row:
                            stock_text += f"20일 이동평균: {last_row.get('MA20', 'N/A')}, "
                        
                        if 'RSI' in last_row:
                            stock_text += f"RSI: {last_row.get('RSI', 'N/A')}, "
                        
                        if 'MACD' in last_row:
                            stock_text += f"MACD: {last_row.get('MACD', 'N/A')}, "
                        
                        if 'volatility_20d' in last_row:
                            stock_text += f"20일 변동성: {last_row.get('volatility_20d', 'N/A')}, "
                        
                        # 임베딩 생성
                        embedding = self.embedding_model.embed_text(stock_text)
                        
                        # 메타데이터 생성
                        metadata = {
                            "content_type": "stock",
                            "market": market_type,
                            "symbol": symbol,
                            "timestamp": datetime.now().isoformat(),
                            "text": stock_text
                        }
                        
                        # 벡터 저장소에 추가
                        vector_ids = self.vector_store.add_vectors([embedding], [metadata])
                        all_vector_ids.extend(vector_ids)
            
            # 인사이트 데이터 인덱싱
            if 'insights' in market_data:
                for symbol, insight_data in market_data['insights'].items():
                    # 인사이트 정보 추출 및 텍스트 생성
                    insight_text = f"{symbol} 주식 인사이트: "
                    
                    # 인사이트 데이터 구조에 따라 정보 추출
                    if isinstance(insight_data, dict) and 'finance' in insight_data:
                        finance = insight_data['finance']
                        if 'result' in finance:
                            result = finance['result']
                            
                            # 기술적 이벤트 정보
                            if 'instrumentInfo' in result and 'technicalEvents' in result['instrumentInfo']:
                                tech_events = result['instrumentInfo']['technicalEvents']
                                
                                if 'shortTermOutlook' in tech_events:
                                    outlook = tech_events['shortTermOutlook']
                                    insight_text += f"단기 전망: {outlook.get('scoreDescription', 'N/A')}, "
                                
                                if 'intermediateTermOutlook' in tech_events:
                                    outlook = tech_events['intermediateTermOutlook']
                                    insight_text += f"중기 전망: {outlook.get('scoreDescription', 'N/A')}, "
                            
                            # 밸류에이션 정보
                            if 'instrumentInfo' in result and 'valuation' in result['instrumentInfo']:
                                valuation = result['instrumentInfo']['valuation']
                                insight_text += f"밸류에이션: {valuation.get('description', 'N/A')}, "
                    
                    # 임베딩 생성
                    embedding = self.embedding_model.embed_text(insight_text)
                    
                    # 메타데이터 생성
                    metadata = {
                        "content_type": "insight",
                        "market": market_type,
                        "symbol": symbol,
                        "timestamp": datetime.now().isoformat(),
                        "text": insight_text
                    }
                    
                    # 벡터 저장소에 추가
                    vector_ids = self.vector_store.add_vectors([embedding], [metadata])
                    all_vector_ids.extend(vector_ids)
            
            logger.info(f"{market_type} 시장 데이터 인덱싱 완료: {len(all_vector_ids)} 개의 벡터가 생성되었습니다.")
            return all_vector_ids
        
        except Exception as e:
            logger.error(f"시장 데이터 인덱싱 중 오류 발생: {str(e)}")
            raise
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리와 관련된 문서를 검색합니다.
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 목록
        """
        try:
            logger.info(f"쿼리 '{query}'에 대한 검색 시작...")
            
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_model.embed_text(query)
            
            # 벡터 저장소에서 유사한 벡터 검색
            search_results = self.vector_store.search(query_embedding, top_k=top_k)
            
            logger.info(f"검색 완료: {len(search_results)} 개의 결과를 찾았습니다.")
            return search_results
        
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {str(e)}")
            raise
    
    def generate_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        검색 결과에서 컨텍스트를 생성합니다.
        
        Args:
            search_results: 검색 결과 목록
            
        Returns:
            생성된 컨텍스트
        """
        try:
            context_parts = []
            
            for i, result in enumerate(search_results):
                metadata = result.get("metadata", {})
                text = metadata.get("text", "")
                score = result.get("score", 0)
                
                if text:
                    context_parts.append(f"[문서 {i+1}] (관련도: {score:.4f})")
                    context_parts.append(text)
                    context_parts.append("")
            
            return "\n".join(context_parts)
        
        except Exception as e:
            logger.error(f"컨텍스트 생성 중 오류 발생: {str(e)}")
            raise
    
    def format_rag_prompt(self, query: str, context: str) -> str:
        """
        RAG 프롬프트를 포맷팅합니다.
        
        Args:
            query: 사용자 쿼리
            context: 검색 컨텍스트
            
        Returns:
            포맷팅된 프롬프트
        """
        return f"""다음 정보를 바탕으로 질문에 답변해주세요:

### 컨텍스트:
{context}

### 질문:
{query}

### 답변:
"""


class RAGFactory:
    """
    RAG 시스템 팩토리 클래스
    """
    
    @staticmethod
    def create_stock_market_rag(
        embedding_model_type: str,
        vector_store_type: str,
        embedding_model_params: Dict[str, Any] = None,
        vector_store_params: Dict[str, Any] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> StockMarketRAG:
        """
        주식 시장 RAG 시스템을 생성합니다.
        
        Args:
            embedding_model_type: 임베딩 모델 유형
            vector_store_type: 벡터 저장소 유형
            embedding_model_params: 임베딩 모델 매개변수
            vector_store_params: 벡터 저장소 매개변수
            chunk_size: 텍스트 청크 크기
            chunk_overlap: 텍스트 청크 간 중복 크기
            
        Returns:
            주식 시장 RAG 시스템 인스턴스
        """
        if embedding_model_params is None:
            embedding_model_params = {}
        
        if vector_store_params is None:
            vector_store_params = {}
        
        # 임베딩 모델 생성
        embedding_model = EmbeddingFactory.create_embedding_model(
            model_type=embedding_model_type,
            **embedding_model_params
        )
        
        # 벡터 저장소 생성
        if 'dimension' not in vector_store_params:
            vector_store_params['dimension'] = embedding_model.dimension
        
        vector_store = VectorStoreFactory.create_vector_store(
            store_type=vector_store_type,
            **vector_store_params
        )
        
        # RAG 시스템 생성
        return StockMarketRAG(
            embedding_model=embedding_model,
            vector_store=vector_store,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
