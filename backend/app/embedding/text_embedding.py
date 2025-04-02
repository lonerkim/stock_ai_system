"""
텍스트 임베딩 모듈

이 모듈은 주식 시장 데이터를 텍스트 임베딩으로 변환하는 기능을 제공합니다.
다양한 임베딩 모델을 지원하며, 로컬 모델과 API 기반 모델을 모두 사용할 수 있습니다.
"""
import os
import logging
import numpy as np
from typing import List, Dict, Any, Union, Optional
import json
import requests
from abc import ABC, abstractmethod

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseEmbeddingModel(ABC):
    """
    임베딩 모델의 기본 추상 클래스
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> np.ndarray:
        """
        텍스트를 임베딩 벡터로 변환합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        텍스트 배치를 임베딩 벡터로 변환합니다.
        
        Args:
            texts: 임베딩할 텍스트 목록
            
        Returns:
            임베딩 벡터 목록
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        임베딩 벡터의 차원을 반환합니다.
        
        Returns:
            임베딩 차원
        """
        pass


class SentenceTransformerModel(BaseEmbeddingModel):
    """
    Sentence Transformers 기반 임베딩 모델
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Sentence Transformers 모델 초기화
        
        Args:
            model_name: 사용할 모델 이름
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self._dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Sentence Transformers 모델 '{model_name}'이(가) 로드되었습니다.")
        except ImportError:
            logger.error("sentence-transformers 패키지가 설치되어 있지 않습니다. 'pip install sentence-transformers'를 실행하세요.")
            raise
        except Exception as e:
            logger.error(f"Sentence Transformers 모델 로드 중 오류 발생: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        텍스트를 임베딩 벡터로 변환합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            return self.model.encode(text, convert_to_numpy=True)
        except Exception as e:
            logger.error(f"텍스트 임베딩 중 오류 발생: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        텍스트 배치를 임베딩 벡터로 변환합니다.
        
        Args:
            texts: 임베딩할 텍스트 목록
            
        Returns:
            임베딩 벡터 목록
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [embedding for embedding in embeddings]
        except Exception as e:
            logger.error(f"텍스트 배치 임베딩 중 오류 발생: {str(e)}")
            raise
    
    @property
    def dimension(self) -> int:
        """
        임베딩 벡터의 차원을 반환합니다.
        
        Returns:
            임베딩 차원
        """
        return self._dimension


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    """
    OpenAI API 기반 임베딩 모델
    """
    
    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        """
        OpenAI 임베딩 모델 초기화
        
        Args:
            api_key: OpenAI API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.openai.com/v1/embeddings"
        
        # 모델별 차원 매핑
        self.model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        
        if model_name not in self.model_dimensions:
            logger.warning(f"알 수 없는 모델 '{model_name}'. 기본 차원 1536을 사용합니다.")
            self._dimension = 1536
        else:
            self._dimension = self.model_dimensions[model_name]
        
        logger.info(f"OpenAI 임베딩 모델 '{model_name}'이(가) 초기화되었습니다.")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        텍스트를 임베딩 벡터로 변환합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "input": text,
                "model": self.model_name
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            logger.error(f"OpenAI 텍스트 임베딩 중 오류 발생: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[np.ndarray]:
        """
        텍스트 배치를 임베딩 벡터로 변환합니다.
        
        Args:
            texts: 임베딩할 텍스트 목록
            batch_size: API 호출당 처리할 텍스트 수
            
        Returns:
            임베딩 벡터 목록
        """
        try:
            all_embeddings = []
            
            # 배치 단위로 처리
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                payload = {
                    "input": batch,
                    "model": self.model_name
                }
                
                response = requests.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                batch_embeddings = [np.array(item["embedding"], dtype=np.float32) for item in result["data"]]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
        except Exception as e:
            logger.error(f"OpenAI 텍스트 배치 임베딩 중 오류 발생: {str(e)}")
            raise
    
    @property
    def dimension(self) -> int:
        """
        임베딩 벡터의 차원을 반환합니다.
        
        Returns:
            임베딩 차원
        """
        return self._dimension


class MistralEmbeddingModel(BaseEmbeddingModel):
    """
    Mistral AI API 기반 임베딩 모델
    """
    
    def __init__(self, api_key: str, model_name: str = "mistral-embed"):
        """
        Mistral 임베딩 모델 초기화
        
        Args:
            api_key: Mistral AI API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.mistral.ai/v1/embeddings"
        
        # 모델별 차원 매핑
        self.model_dimensions = {
            "mistral-embed": 1024,
            "mistral-embed-v2": 1536
        }
        
        if model_name not in self.model_dimensions:
            logger.warning(f"알 수 없는 모델 '{model_name}'. 기본 차원 1024를 사용합니다.")
            self._dimension = 1024
        else:
            self._dimension = self.model_dimensions[model_name]
        
        logger.info(f"Mistral 임베딩 모델 '{model_name}'이(가) 초기화되었습니다.")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        텍스트를 임베딩 벡터로 변환합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "input": text,
                "model": self.model_name
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            logger.error(f"Mistral 텍스트 임베딩 중 오류 발생: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[np.ndarray]:
        """
        텍스트 배치를 임베딩 벡터로 변환합니다.
        
        Args:
            texts: 임베딩할 텍스트 목록
            batch_size: API 호출당 처리할 텍스트 수
            
        Returns:
            임베딩 벡터 목록
        """
        try:
            all_embeddings = []
            
            # 배치 단위로 처리
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                payload = {
                    "input": batch,
                    "model": self.model_name
                }
                
                response = requests.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                batch_embeddings = [np.array(item["embedding"], dtype=np.float32) for item in result["data"]]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
        except Exception as e:
            logger.error(f"Mistral 텍스트 배치 임베딩 중 오류 발생: {str(e)}")
            raise
    
    @property
    def dimension(self) -> int:
        """
        임베딩 벡터의 차원을 반환합니다.
        
        Returns:
            임베딩 차원
        """
        return self._dimension


class GeminiEmbeddingModel(BaseEmbeddingModel):
    """
    Google Gemini API 기반 임베딩 모델
    """
    
    def __init__(self, api_key: str, model_name: str = "models/embedding-001"):
        """
        Gemini 임베딩 모델 초기화
        
        Args:
            api_key: Google API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1/{model_name}:embedText"
        
        # 모델별 차원 매핑
        self.model_dimensions = {
            "models/embedding-001": 768
        }
        
        if model_name not in self.model_dimensions:
            logger.warning(f"알 수 없는 모델 '{model_name}'. 기본 차원 768을 사용합니다.")
            self._dimension = 768
        else:
            self._dimension = self.model_dimensions[model_name]
        
        logger.info(f"Gemini 임베딩 모델 '{model_name}'이(가) 초기화되었습니다.")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        텍스트를 임베딩 벡터로 변환합니다.
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터
        """
        try:
            params = {
                "key": self.api_key
            }
            
            payload = {
                "text": text
            }
            
            response = requests.post(self.api_url, params=params, json=payload)
            response.raise_for_status()
            
            result = response.json()
            embedding = result["embedding"]["values"]
            
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            logger.error(f"Gemini 텍스트 임베딩 중 오류 발생: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        텍스트 배치를 임베딩 벡터로 변환합니다.
        
        Args:
            texts: 임베딩할 텍스트 목록
            
        Returns:
            임베딩 벡터 목록
        """
        try:
            # Gemini API는 현재 배치 처리를 지원하지 않으므로 개별 처리
            return [self.embed_text(text) for text in texts]
        except Exception as e:
            logger.error(f"Gemini 텍스트 배치 임베딩 중 오류 발생: {str(e)}")
            raise
    
    @property
    def dimension(self) -> int:
        """
        임베딩 벡터의 차원을 반환합니다.
        
        Returns:
            임베딩 차원
        """
        return self._dimension


class EmbeddingFactory:
    """
    임베딩 모델 팩토리 클래스
    """
    
    @staticmethod
    def create_embedding_model(model_type: str, **kwargs) -> BaseEmbeddingModel:
        """
        임베딩 모델을 생성합니다.
        
        Args:
            model_type: 모델 유형 ('sentence_transformer', 'openai', 'mistral', 'gemini')
            **kwargs: 모델별 추가 매개변수
            
        Returns:
            임베딩 모델 인스턴스
        """
        if model_type == "sentence_transformer":
            model_name = kwargs.get("model_name", "all-MiniLM-L6-v2")
            return SentenceTransformerModel(model_name=model_name)
        
        elif model_type == "openai":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("OpenAI 임베딩 모델에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "text-embedding-3-small")
            return OpenAIEmbeddingModel(api_key=api_key, model_name=model_name)
        
        elif model_type == "mistral":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Mistral 임베딩 모델에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "mistral-embed")
            return MistralEmbeddingModel(api_key=api_key, model_name=model_name)
        
        elif model_type == "gemini":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Gemini 임베딩 모델에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "models/embedding-001")
            return GeminiEmbeddingModel(api_key=api_key, model_name=model_name)
        
        else:
            raise ValueError(f"지원되지 않는 모델 유형: {model_type}")
