"""
검색 및 요약 기능 모듈

이 모듈은 주식 시장 데이터에 대한 검색 및 요약 기능을 제공합니다.
RAG 파이프라인과 AI 모델을 활용하여 사용자 쿼리에 대한 응답을 생성합니다.
"""
import os
import logging
import json
import requests
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime

from .rag_pipeline import StockMarketRAG

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIModelInterface:
    """
    AI 모델 인터페이스 추상 클래스
    """
    
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 응답
        """
        raise NotImplementedError("이 메서드는 하위 클래스에서 구현해야 합니다.")


class OpenAIModel(AIModelInterface):
    """
    OpenAI API 기반 모델
    """
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        """
        OpenAI 모델 초기화
        
        Args:
            api_key: OpenAI API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        logger.info(f"OpenAI 모델 '{model_name}'이(가) 초기화되었습니다.")
    
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 응답
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "당신은 주식 시장 분석 전문가입니다. 제공된 정보를 바탕으로 정확하고 유용한 분석과 통찰을 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"OpenAI 응답 생성 중 오류 발생: {str(e)}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"


class MistralModel(AIModelInterface):
    """
    Mistral AI API 기반 모델
    """
    
    def __init__(self, api_key: str, model_name: str = "mistral-medium"):
        """
        Mistral 모델 초기화
        
        Args:
            api_key: Mistral AI API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        
        logger.info(f"Mistral 모델 '{model_name}'이(가) 초기화되었습니다.")
    
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 응답
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "당신은 주식 시장 분석 전문가입니다. 제공된 정보를 바탕으로 정확하고 유용한 분석과 통찰을 제공해주세요."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"Mistral 응답 생성 중 오류 발생: {str(e)}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"


class GeminiModel(AIModelInterface):
    """
    Google Gemini API 기반 모델
    """
    
    def __init__(self, api_key: str, model_name: str = "models/gemini-pro"):
        """
        Gemini 모델 초기화
        
        Args:
            api_key: Google API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1/{model_name}:generateContent"
        
        logger.info(f"Gemini 모델 '{model_name}'이(가) 초기화되었습니다.")
    
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 응답
        """
        try:
            params = {
                "key": self.api_key
            }
            
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": "당신은 주식 시장 분석 전문가입니다. 제공된 정보를 바탕으로 정확하고 유용한 분석과 통찰을 제공해주세요.\n\n" + prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(self.api_url, params=params, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        except Exception as e:
            logger.error(f"Gemini 응답 생성 중 오류 발생: {str(e)}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"


class LocalAIModel(AIModelInterface):
    """
    로컬 AI API 기반 모델
    """
    
    def __init__(self, api_url: str):
        """
        로컬 AI 모델 초기화
        
        Args:
            api_url: 로컬 AI API URL
        """
        self.api_url = api_url
        
        logger.info(f"로컬 AI 모델이 초기화되었습니다. API URL: {api_url}")
    
    def generate_response(self, prompt: str) -> str:
        """
        프롬프트에 대한 응답을 생성합니다.
        
        Args:
            prompt: 입력 프롬프트
            
        Returns:
            생성된 응답
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "prompt": "당신은 주식 시장 분석 전문가입니다. 제공된 정보를 바탕으로 정확하고 유용한 분석과 통찰을 제공해주세요.\n\n" + prompt,
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # 응답 형식은 로컬 API에 따라 다를 수 있음
            if "text" in result:
                return result["text"]
            elif "response" in result:
                return result["response"]
            elif "output" in result:
                return result["output"]
            else:
                return str(result)
        
        except Exception as e:
            logger.error(f"로컬 AI 응답 생성 중 오류 발생: {str(e)}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"


class AIModelFactory:
    """
    AI 모델 팩토리 클래스
    """
    
    @staticmethod
    def create_ai_model(model_type: str, **kwargs) -> AIModelInterface:
        """
        AI 모델을 생성합니다.
        
        Args:
            model_type: 모델 유형 ('openai', 'mistral', 'gemini', 'local')
            **kwargs: 모델별 추가 매개변수
            
        Returns:
            AI 모델 인스턴스
        """
        if model_type == "openai":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("OpenAI 모델에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "gpt-3.5-turbo")
            return OpenAIModel(api_key=api_key, model_name=model_name)
        
        elif model_type == "mistral":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Mistral 모델에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "mistral-medium")
            return MistralModel(api_key=api_key, model_name=model_name)
        
        elif model_type == "gemini":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Gemini 모델에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "models/gemini-pro")
            return GeminiModel(api_key=api_key, model_name=model_name)
        
        elif model_type == "local":
            api_url = kwargs.get("api_url")
            if not api_url:
                raise ValueError("로컬 AI 모델에는 API URL이 필요합니다.")
            
            return LocalAIModel(api_url=api_url)
        
        else:
            raise ValueError(f"지원되지 않는 모델 유형: {model_type}")


class StockMarketSearchEngine:
    """
    주식 시장 검색 엔진
    """
    
    def __init__(self, rag_system: StockMarketRAG, ai_model: AIModelInterface):
        """
        주식 시장 검색 엔진 초기화
        
        Args:
            rag_system: RAG 시스템
            ai_model: AI 모델
        """
        self.rag_system = rag_system
        self.ai_model = ai_model
        
        logger.info("주식 시장 검색 엔진이 초기화되었습니다.")
    
    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        쿼리에 대한 검색을 수행합니다.
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과
        """
        try:
            logger.info(f"쿼리 '{query}'에 대한 검색 시작...")
            
            # RAG 시스템을 통한 검색
            search_results = self.rag_system.retrieve(query, top_k=top_k)
            
            # 컨텍스트 생성
            context = self.rag_system.generate_context(search_results)
            
            # 검색 결과 반환
            return {
                "query": query,
                "results": search_results,
                "context": context
            }
        
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {str(e)}")
            raise
    
    def summarize(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        쿼리에 대한 검색 및 요약을 수행합니다.
        
        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            
        Returns:
            요약 결과
        """
        try:
            logger.info(f"쿼리 '{query}'에 대한 검색 및 요약 시작...")
            
            # 검색 수행
            search_result = self.search(query, top_k=top_k)
            context = search_result["context"]
            
            # RAG 프롬프트 생성
            prompt = self.rag_system.format_rag_prompt(query, context)
            
            # AI 모델을 통한 응답 생성
            response = self.ai_model.generate_response(prompt)
            
            # 요약 결과 반환
            return {
                "query": query,
                "context": context,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"요약 중 오류 발생: {str(e)}")
            raise
    
    def analyze_market_trend(self, market_type: str = "all") -> Dict[str, Any]:
        """
        시장 동향을 분석합니다.
        
        Args:
            market_type: 시장 유형 ('all', 'korean', 'us')
            
        Returns:
            분석 결과
        """
        try:
            logger.info(f"{market_type} 시장 동향 분석 시작...")
            
            # 시장 유형에 따른 쿼리 생성
            if market_type == "korean":
                query = "한국 주식 시장의 최근 동향과 주요 지수 및 블루칩 주식의 현황을 분석해주세요."
            elif market_type == "us":
                query = "미국 주식 시장의 최근 동향과 주요 지수 및 블루칩 주식의 현황을 분석해주세요."
            else:  # 'all'
                query = "한국과 미국 주식 시장의 최근 동향과 주요 지수 및 블루칩 주식의 현황을 비교 분석해주세요."
            
            # 요약 수행
            result = self.summarize(query, top_k=10)
            
            # 분석 결과 반환
            return {
                "market_type": market_type,
                "analysis": result["response"],
                "timestamp": result["timestamp"]
            }
        
        except Exception as e:
            logger.error(f"시장 동향 분석 중 오류 발생: {str(e)}")
            raise
    
    def recommend_stocks(self, market_type: str = "all", count: int = 5) -> Dict[str, Any]:
        """
        투자 가치가 있는 주식을 추천합니다.
        
        Args:
            market_type: 시장 유형 ('all', 'korean', 'us')
            count: 추천할 주식 수
            
        Returns:
            추천 결과
        """
        try:
            logger.info(f"{market_type} 시장에서 {count}개의 주식 추천 시작...")
            
            # 시장 유형에 따른 쿼리 생성
            if market_type == "korean":
                query = f"한국 주식 시장에서 현재 투자 가치가 높은 블루칩 주식 {count}개를 추천하고 그 이유를 설명해주세요."
            elif market_type == "us":
                query = f"미국 주식 시장에서 현재 투자 가치가 높은 블루칩 주식 {count}개를 추천하고 그 이유를 설명해주세요."
            else:  # 'all'
                query = f"한국과 미국 주식 시장에서 현재 투자 가치가 높은 블루칩 주식 {count}개를 추천하고 그 이유를 설명해주세요."
            
            # 요약 수행
            result = self.summarize(query, top_k=10)
            
            # 추천 결과 반환
            return {
                "market_type": market_type,
                "recommendations": result["response"],
                "timestamp": result["timestamp"]
            }
        
        except Exception as e:
            logger.error(f"주식 추천 중 오류 발생: {str(e)}")
            raise


class SearchEngineFactory:
    """
    검색 엔진 팩토리 클래스
    """
    
    @staticmethod
    def create_stock_market_search_engine(
        embedding_model_type: str,
        vector_store_type: str,
        ai_model_type: str,
        embedding_model_params: Dict[str, Any] = None,
        vector_store_params: Dict[str, Any] = None,
        ai_model_params: Dict[str, Any] = None
    ) -> StockMarketSearchEngine:
        """
        주식 시장 검색 엔진을 생성합니다.
        
        Args:
            embedding_model_type: 임베딩 모델 유형
            vector_store_type: 벡터 저장소 유형
            ai_model_type: AI 모델 유형
            embedding_model_params: 임베딩 모델 매개변수
            vector_store_params: 벡터 저장소 매개변수
            ai_model_params: AI 모델 매개변수
            
        Returns:
            주식 시장 검색 엔진 인스턴스
        """
        from .rag_pipeline import RAGFactory
        
        if embedding_model_params is None:
            embedding_model_params = {}
        
        if vector_store_params is None:
            vector_store_params = {}
        
        if ai_model_params is None:
            ai_model_params = {}
        
        # RAG 시스템 생성
        rag_system = RAGFactory.create_stock_market_rag(
            embedding_model_type=embedding_model_type,
            vector_store_type=vector_store_type,
            embedding_model_params=embedding_model_params,
            vector_store_params=vector_store_params
        )
        
        # AI 모델 생성
        ai_model = AIModelFactory.create_ai_model(
            model_type=ai_model_type,
            **ai_model_params
        )
        
        # 검색 엔진 생성
        return StockMarketSearchEngine(
            rag_system=rag_system,
            ai_model=ai_model
        )
