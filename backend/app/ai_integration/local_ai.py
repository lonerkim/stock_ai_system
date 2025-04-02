"""
로컬 AI 연동 모듈

이 모듈은 로컬에서 실행되는 AI 모델과의 연동 기능을 제공합니다.
Ollama, LM Studio, LocalAI 등 다양한 로컬 AI 서비스를 지원합니다.
"""
import os
import logging
import json
import requests
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
import socket
import time

from .ai_provider import BaseAIProvider, LocalAIProvider

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalAIConnector:
    """
    로컬 AI 서비스 연결 관리자
    """
    
    def __init__(self, service_type: str = "ollama", host: str = "localhost", port: int = 11434):
        """
        로컬 AI 연결 관리자 초기화
        
        Args:
            service_type: 로컬 AI 서비스 유형 ('ollama', 'lmstudio', 'localai')
            host: 호스트 주소
            port: 포트 번호
        """
        self.service_type = service_type
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
        # 서비스 유형별 API 엔드포인트 설정
        if service_type == "ollama":
            self.api_endpoint = f"{self.base_url}/api/generate"
            self.models_endpoint = f"{self.base_url}/api/tags"
        elif service_type == "lmstudio":
            self.api_endpoint = f"{self.base_url}/v1/completions"
            self.models_endpoint = f"{self.base_url}/v1/models"
        elif service_type == "localai":
            self.api_endpoint = f"{self.base_url}/v1/completions"
            self.models_endpoint = f"{self.base_url}/v1/models"
        else:
            raise ValueError(f"지원되지 않는 로컬 AI 서비스 유형: {service_type}")
        
        logger.info(f"로컬 AI 연결 관리자가 초기화되었습니다. 서비스: {service_type}, URL: {self.base_url}")
    
    def check_connection(self, timeout: int = 5) -> bool:
        """
        로컬 AI 서비스 연결을 확인합니다.
        
        Args:
            timeout: 연결 타임아웃 (초)
            
        Returns:
            연결 성공 여부
        """
        try:
            # 소켓 연결 시도
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                # HTTP 요청 시도
                try:
                    response = requests.get(self.base_url, timeout=timeout)
                    logger.info(f"로컬 AI 서비스 연결 성공: {self.base_url}")
                    return True
                except requests.RequestException:
                    # 기본 엔드포인트가 없는 경우 모델 목록 엔드포인트 시도
                    try:
                        response = requests.get(self.models_endpoint, timeout=timeout)
                        logger.info(f"로컬 AI 서비스 연결 성공: {self.models_endpoint}")
                        return True
                    except requests.RequestException as e:
                        logger.warning(f"로컬 AI 서비스 HTTP 연결 실패: {str(e)}")
                        return False
            else:
                logger.warning(f"로컬 AI 서비스 소켓 연결 실패: {self.host}:{self.port}")
                return False
        
        except Exception as e:
            logger.error(f"로컬 AI 서비스 연결 확인 중 오류 발생: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        사용 가능한 모델 목록을 가져옵니다.
        
        Returns:
            모델 이름 목록
        """
        try:
            response = requests.get(self.models_endpoint)
            response.raise_for_status()
            
            result = response.json()
            
            # 서비스 유형별 응답 파싱
            if self.service_type == "ollama":
                # Ollama 응답 형식: {"models": [{"name": "llama2", ...}, ...]}
                return [model["name"] for model in result.get("models", [])]
            elif self.service_type in ["lmstudio", "localai"]:
                # LM Studio / LocalAI 응답 형식: {"data": [{"id": "llama2", ...}, ...]}
                return [model["id"] for model in result.get("data", [])]
            else:
                return []
        
        except Exception as e:
            logger.error(f"모델 목록 가져오기 중 오류 발생: {str(e)}")
            return []
    
    def create_provider(self, model_name: str = None) -> BaseAIProvider:
        """
        로컬 AI 제공자를 생성합니다.
        
        Args:
            model_name: 사용할 모델 이름 (없으면 기본 모델 사용)
            
        Returns:
            로컬 AI 제공자 인스턴스
        """
        # 모델 이름이 없으면 사용 가능한 첫 번째 모델 사용
        if not model_name:
            available_models = self.get_available_models()
            if available_models:
                model_name = available_models[0]
            else:
                # 기본 모델 이름 설정
                if self.service_type == "ollama":
                    model_name = "llama2"
                else:
                    model_name = "gpt2"
        
        # 서비스 유형별 API URL 생성
        if self.service_type == "ollama":
            api_url = f"{self.base_url}/api/generate"
            # Ollama 제공자 생성
            return OllamaProvider(api_url=api_url, model_name=model_name)
        elif self.service_type in ["lmstudio", "localai"]:
            api_url = f"{self.base_url}/v1/completions"
            # LM Studio / LocalAI 제공자 생성
            return LocalAIProvider(api_url=api_url)
        else:
            raise ValueError(f"지원되지 않는 로컬 AI 서비스 유형: {self.service_type}")


class OllamaProvider(BaseAIProvider):
    """
    Ollama API 기반 AI 제공자
    """
    
    def __init__(self, api_url: str, model_name: str = "llama2"):
        """
        Ollama 제공자 초기화
        
        Args:
            api_url: Ollama API URL
            model_name: 사용할 모델 이름
        """
        self.api_url = api_url
        self.model_name = model_name
        
        logger.info(f"Ollama 제공자가 초기화되었습니다. API URL: {api_url}, 모델: {model_name}")
    
    def _call_api(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        Ollama API를 호출합니다.
        
        Args:
            prompt: 프롬프트 텍스트
            temperature: 온도 (창의성 조절)
            max_tokens: 최대 토큰 수
            
        Returns:
            API 응답 텍스트
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Ollama 응답 형식: {"response": "생성된 텍스트", ...}
            return result.get("response", "")
        
        except Exception as e:
            logger.error(f"Ollama API 호출 중 오류 발생: {str(e)}")
            raise
    
    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 데이터를 분석합니다.
        
        Args:
            market_data: 분석할 시장 데이터
            
        Returns:
            분석 결과
        """
        try:
            # 시장 데이터에서 요약 텍스트 추출
            summary_text = market_data.get("summary_text", "")
            
            # 프롬프트 생성
            prompt = f"""당신은 주식 시장 분석 전문가입니다. 제공된 시장 데이터를 분석하여 현재 시장 상황, 주요 지수 동향, 주목할 만한 섹터 및 주식에 대한 통찰력 있는 분석을 제공해주세요.

다음 시장 데이터를 분석해주세요:

{summary_text}

현재 시장 상황에 대한 종합적인 분석과 향후 전망을 제공해주세요."""
            
            # API 호출
            analysis = self._call_api(prompt)
            
            return {
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "provider": "Ollama",
                "model": self.model_name
            }
        
        except Exception as e:
            logger.error(f"시장 분석 중 오류 발생: {str(e)}")
            raise
    
    def recommend_stocks(self, market_data: Dict[str, Any], count: int = 5) -> Dict[str, Any]:
        """
        투자할 주식을 추천합니다.
        
        Args:
            market_data: 분석할 시장 데이터
            count: 추천할 주식 수
            
        Returns:
            추천 결과
        """
        try:
            # 시장 데이터에서 요약 텍스트 추출
            summary_text = market_data.get("summary_text", "")
            
            # 프롬프트 생성
            prompt = f"""당신은 주식 투자 전문가입니다. 제공된 시장 데이터를 분석하여 현재 투자 가치가 높은 블루칩 주식을 추천해주세요.

다음 시장 데이터를 기반으로 투자 가치가 높은 블루칩 주식 {count}개를 추천해주세요:

{summary_text}

각 추천 주식에 대해 심볼, 회사명, 현재 가격, 추천 이유를 포함해주세요."""
            
            # API 호출
            recommendations = self._call_api(prompt)
            
            return {
                "recommendations": recommendations,
                "count": count,
                "timestamp": datetime.now().isoformat(),
                "provider": "Ollama",
                "model": self.model_name
            }
        
        except Exception as e:
            logger.error(f"주식 추천 중 오류 발생: {str(e)}")
            raise
    
    def make_investment_decision(self, market_data: Dict[str, Any], available_funds: float) -> Dict[str, Any]:
        """
        투자 결정을 내립니다.
        
        Args:
            market_data: 분석할 시장 데이터
            available_funds: 사용 가능한 자금
            
        Returns:
            투자 결정
        """
        try:
            # 시장 데이터에서 요약 텍스트 추출
            summary_text = market_data.get("summary_text", "")
            
            # 프롬프트 생성
            prompt = f"""당신은 주식 투자 전문가입니다. 제공된 시장 데이터를 분석하여 최적의 투자 결정을 내려주세요. 결과는 JSON 형식으로 제공해주세요.

다음 시장 데이터를 기반으로 ${available_funds:.2f}의 자금을 어떻게 투자할지 결정해주세요:

{summary_text}

다음 JSON 형식으로 응답해주세요:
```json
{{
  "investments": [
    {{
      "symbol": "AAPL",
      "company": "Apple Inc.",
      "amount": 50.00,
      "reason": "투자 이유"
    }},
    ...
  ],
  "cash_reserve": 10.00,
  "strategy": "전반적인 투자 전략 설명"
}}
```"""
            
            # API 호출
            decision_text = self._call_api(prompt)
            
            # JSON 추출
            try:
                # JSON 부분 추출
                json_start = decision_text.find("{")
                json_end = decision_text.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = decision_text[json_start:json_end]
                    decision = json.loads(json_str)
                else:
                    # JSON 형식이 아닌 경우 파싱 시도
                    decision = {
                        "investments": [],
                        "cash_reserve": available_funds,
                        "strategy": "투자 결정을 파싱할 수 없습니다.",
                        "raw_response": decision_text
                    }
            except Exception as e:
                logger.warning(f"투자 결정 파싱 중 오류 발생: {str(e)}")
                decision = {
                    "investments": [],
                    "cash_reserve": available_funds,
                    "strategy": "투자 결정을 파싱할 수 없습니다.",
                    "raw_response": decision_text
                }
            
            # 메타데이터 추가
            decision["timestamp"] = datetime.now().isoformat()
            decision["provider"] = "Ollama"
            decision["model"] = self.model_name
            decision["available_funds"] = available_funds
            
            return decision
        
        except Exception as e:
            logger.error(f"투자 결정 중 오류 발생: {str(e)}")
            raise


class LocalAIDetector:
    """
    로컬 AI 서비스 자동 감지 도구
    """
    
    @staticmethod
    def detect_local_services(timeout: int = 2) -> List[Dict[str, Any]]:
        """
        로컬에서 실행 중인 AI 서비스를 감지합니다.
        
        Args:
            timeout: 연결 타임아웃 (초)
            
        Returns:
            감지된 서비스 목록
        """
        # 일반적인 로컬 AI 서비스 포트
        service_ports = {
            "ollama": 11434,
            "lmstudio": 1234,
            "localai": 8080
        }
        
        detected_services = []
        
        for service_name, port in service_ports.items():
            try:
                # 소켓 연결 시도
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex(("localhost", port))
                sock.close()
                
                if result == 0:
                    logger.info(f"로컬 AI 서비스 감지: {service_name} (포트: {port})")
                    
                    # 서비스 정보 생성
                    service_info = {
                        "name": service_name,
                        "host": "localhost",
                        "port": port,
                        "url": f"http://localhost:{port}"
                    }
                    
                    # 연결 관리자 생성 및 모델 목록 가져오기
                    try:
                        connector = LocalAIConnector(service_type=service_name, host="localhost", port=port)
                        models = connector.get_available_models()
                        service_info["available_models"] = models
                    except Exception as e:
                        logger.warning(f"모델 목록 가져오기 실패: {str(e)}")
                        service_info["available_models"] = []
                    
                    detected_services.append(service_info)
            
            except Exception as e:
                logger.debug(f"{service_name} 서비스 감지 중 오류 발생: {str(e)}")
        
        return detected_services
