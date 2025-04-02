"""
AI API 통합 인터페이스 모듈

이 모듈은 다양한 AI 서비스(OpenAI, Mistral, Gemini)와의 통합 인터페이스를 제공합니다.
사용자가 선택한 AI 서비스를 통해 주식 시장 분석 및 투자 결정을 수행할 수 있습니다.
"""
import os
import logging
import json
import requests
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseAIProvider(ABC):
    """
    AI 제공자의 기본 추상 클래스
    """
    
    @abstractmethod
    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 데이터를 분석합니다.
        
        Args:
            market_data: 분석할 시장 데이터
            
        Returns:
            분석 결과
        """
        pass
    
    @abstractmethod
    def recommend_stocks(self, market_data: Dict[str, Any], count: int = 5) -> Dict[str, Any]:
        """
        투자할 주식을 추천합니다.
        
        Args:
            market_data: 분석할 시장 데이터
            count: 추천할 주식 수
            
        Returns:
            추천 결과
        """
        pass
    
    @abstractmethod
    def make_investment_decision(self, market_data: Dict[str, Any], available_funds: float) -> Dict[str, Any]:
        """
        투자 결정을 내립니다.
        
        Args:
            market_data: 분석할 시장 데이터
            available_funds: 사용 가능한 자금
            
        Returns:
            투자 결정
        """
        pass


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI API 기반 AI 제공자
    """
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        """
        OpenAI 제공자 초기화
        
        Args:
            api_key: OpenAI API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        logger.info(f"OpenAI 제공자가 초기화되었습니다. 모델: {model_name}")
    
    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        OpenAI API를 호출합니다.
        
        Args:
            messages: 메시지 목록
            temperature: 온도 (창의성 조절)
            max_tokens: 최대 토큰 수
            
        Returns:
            API 응답 텍스트
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"OpenAI API 호출 중 오류 발생: {str(e)}")
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
            
            # 시스템 메시지 및 사용자 메시지 생성
            messages = [
                {
                    "role": "system",
                    "content": "당신은 주식 시장 분석 전문가입니다. 제공된 시장 데이터를 분석하여 현재 시장 상황, 주요 지수 동향, 주목할 만한 섹터 및 주식에 대한 통찰력 있는 분석을 제공해주세요."
                },
                {
                    "role": "user",
                    "content": f"다음 시장 데이터를 분석해주세요:\n\n{summary_text}\n\n현재 시장 상황에 대한 종합적인 분석과 향후 전망을 제공해주세요."
                }
            ]
            
            # API 호출
            analysis = self._call_api(messages)
            
            return {
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "provider": "OpenAI",
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
            
            # 시스템 메시지 및 사용자 메시지 생성
            messages = [
                {
                    "role": "system",
                    "content": "당신은 주식 투자 전문가입니다. 제공된 시장 데이터를 분석하여 현재 투자 가치가 높은 블루칩 주식을 추천해주세요."
                },
                {
                    "role": "user",
                    "content": f"다음 시장 데이터를 기반으로 투자 가치가 높은 블루칩 주식 {count}개를 추천해주세요:\n\n{summary_text}\n\n각 추천 주식에 대해 심볼, 회사명, 현재 가격, 추천 이유를 포함해주세요."
                }
            ]
            
            # API 호출
            recommendations = self._call_api(messages)
            
            return {
                "recommendations": recommendations,
                "count": count,
                "timestamp": datetime.now().isoformat(),
                "provider": "OpenAI",
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
            
            # 시스템 메시지 및 사용자 메시지 생성
            messages = [
                {
                    "role": "system",
                    "content": "당신은 주식 투자 전문가입니다. 제공된 시장 데이터를 분석하여 최적의 투자 결정을 내려주세요. 결과는 JSON 형식으로 제공해주세요."
                },
                {
                    "role": "user",
                    "content": f"다음 시장 데이터를 기반으로 ${available_funds:.2f}의 자금을 어떻게 투자할지 결정해주세요:\n\n{summary_text}\n\n다음 JSON 형식으로 응답해주세요:\n```json\n{{\n  \"investments\": [\n    {{\n      \"symbol\": \"AAPL\",\n      \"company\": \"Apple Inc.\",\n      \"amount\": 50.00,\n      \"reason\": \"투자 이유\"\n    }},\n    ...\n  ],\n  \"cash_reserve\": 10.00,\n  \"strategy\": \"전반적인 투자 전략 설명\"\n}}\n```"
                }
            ]
            
            # API 호출
            decision_text = self._call_api(messages)
            
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
            decision["provider"] = "OpenAI"
            decision["model"] = self.model_name
            decision["available_funds"] = available_funds
            
            return decision
        
        except Exception as e:
            logger.error(f"투자 결정 중 오류 발생: {str(e)}")
            raise


class MistralProvider(BaseAIProvider):
    """
    Mistral AI API 기반 AI 제공자
    """
    
    def __init__(self, api_key: str, model_name: str = "mistral-medium"):
        """
        Mistral 제공자 초기화
        
        Args:
            api_key: Mistral AI API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        
        logger.info(f"Mistral 제공자가 초기화되었습니다. 모델: {model_name}")
    
    def _call_api(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        Mistral API를 호출합니다.
        
        Args:
            messages: 메시지 목록
            temperature: 온도 (창의성 조절)
            max_tokens: 최대 토큰 수
            
        Returns:
            API 응답 텍스트
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        except Exception as e:
            logger.error(f"Mistral API 호출 중 오류 발생: {str(e)}")
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
            
            # 시스템 메시지 및 사용자 메시지 생성
            messages = [
                {
                    "role": "system",
                    "content": "당신은 주식 시장 분석 전문가입니다. 제공된 시장 데이터를 분석하여 현재 시장 상황, 주요 지수 동향, 주목할 만한 섹터 및 주식에 대한 통찰력 있는 분석을 제공해주세요."
                },
                {
                    "role": "user",
                    "content": f"다음 시장 데이터를 분석해주세요:\n\n{summary_text}\n\n현재 시장 상황에 대한 종합적인 분석과 향후 전망을 제공해주세요."
                }
            ]
            
            # API 호출
            analysis = self._call_api(messages)
            
            return {
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "provider": "Mistral",
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
            
            # 시스템 메시지 및 사용자 메시지 생성
            messages = [
                {
                    "role": "system",
                    "content": "당신은 주식 투자 전문가입니다. 제공된 시장 데이터를 분석하여 현재 투자 가치가 높은 블루칩 주식을 추천해주세요."
                },
                {
                    "role": "user",
                    "content": f"다음 시장 데이터를 기반으로 투자 가치가 높은 블루칩 주식 {count}개를 추천해주세요:\n\n{summary_text}\n\n각 추천 주식에 대해 심볼, 회사명, 현재 가격, 추천 이유를 포함해주세요."
                }
            ]
            
            # API 호출
            recommendations = self._call_api(messages)
            
            return {
                "recommendations": recommendations,
                "count": count,
                "timestamp": datetime.now().isoformat(),
                "provider": "Mistral",
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
            
            # 시스템 메시지 및 사용자 메시지 생성
            messages = [
                {
                    "role": "system",
                    "content": "당신은 주식 투자 전문가입니다. 제공된 시장 데이터를 분석하여 최적의 투자 결정을 내려주세요. 결과는 JSON 형식으로 제공해주세요."
                },
                {
                    "role": "user",
                    "content": f"다음 시장 데이터를 기반으로 ${available_funds:.2f}의 자금을 어떻게 투자할지 결정해주세요:\n\n{summary_text}\n\n다음 JSON 형식으로 응답해주세요:\n```json\n{{\n  \"investments\": [\n    {{\n      \"symbol\": \"AAPL\",\n      \"company\": \"Apple Inc.\",\n      \"amount\": 50.00,\n      \"reason\": \"투자 이유\"\n    }},\n    ...\n  ],\n  \"cash_reserve\": 10.00,\n  \"strategy\": \"전반적인 투자 전략 설명\"\n}}\n```"
                }
            ]
            
            # API 호출
            decision_text = self._call_api(messages)
            
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
            decision["provider"] = "Mistral"
            decision["model"] = self.model_name
            decision["available_funds"] = available_funds
            
            return decision
        
        except Exception as e:
            logger.error(f"투자 결정 중 오류 발생: {str(e)}")
            raise


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini API 기반 AI 제공자
    """
    
    def __init__(self, api_key: str, model_name: str = "models/gemini-pro"):
        """
        Gemini 제공자 초기화
        
        Args:
            api_key: Google API 키
            model_name: 사용할 모델 이름
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://generativelanguage.googleapis.com/v1/{model_name}:generateContent"
        
        logger.info(f"Gemini 제공자가 초기화되었습니다. 모델: {model_name}")
    
    def _call_api(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        Gemini API를 호출합니다.
        
        Args:
            prompt: 프롬프트 텍스트
            temperature: 온도 (창의성 조절)
            max_tokens: 최대 토큰 수
            
        Returns:
            API 응답 텍스트
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
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
            
            response = requests.post(self.api_url, params=params, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        
        except Exception as e:
            logger.error(f"Gemini API 호출 중 오류 발생: {str(e)}")
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
                "provider": "Gemini",
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
                "provider": "Gemini",
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
            decision["provider"] = "Gemini"
            decision["model"] = self.model_name
            decision["available_funds"] = available_funds
            
            return decision
        
        except Exception as e:
            logger.error(f"투자 결정 중 오류 발생: {str(e)}")
            raise


class LocalAIProvider(BaseAIProvider):
    """
    로컬 AI API 기반 AI 제공자
    """
    
    def __init__(self, api_url: str):
        """
        로컬 AI 제공자 초기화
        
        Args:
            api_url: 로컬 AI API URL
        """
        self.api_url = api_url
        
        logger.info(f"로컬 AI 제공자가 초기화되었습니다. API URL: {api_url}")
    
    def _call_api(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000) -> str:
        """
        로컬 AI API를 호출합니다.
        
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
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
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
            logger.error(f"로컬 AI API 호출 중 오류 발생: {str(e)}")
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
                "provider": "LocalAI",
                "api_url": self.api_url
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
                "provider": "LocalAI",
                "api_url": self.api_url
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
            decision["provider"] = "LocalAI"
            decision["api_url"] = self.api_url
            decision["available_funds"] = available_funds
            
            return decision
        
        except Exception as e:
            logger.error(f"투자 결정 중 오류 발생: {str(e)}")
            raise


class AIProviderFactory:
    """
    AI 제공자 팩토리 클래스
    """
    
    @staticmethod
    def create_ai_provider(provider_type: str, **kwargs) -> BaseAIProvider:
        """
        AI 제공자를 생성합니다.
        
        Args:
            provider_type: 제공자 유형 ('openai', 'mistral', 'gemini', 'local')
            **kwargs: 제공자별 추가 매개변수
            
        Returns:
            AI 제공자 인스턴스
        """
        if provider_type == "openai":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("OpenAI 제공자에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "gpt-3.5-turbo")
            return OpenAIProvider(api_key=api_key, model_name=model_name)
        
        elif provider_type == "mistral":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Mistral 제공자에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "mistral-medium")
            return MistralProvider(api_key=api_key, model_name=model_name)
        
        elif provider_type == "gemini":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("Gemini 제공자에는 API 키가 필요합니다.")
            
            model_name = kwargs.get("model_name", "models/gemini-pro")
            return GeminiProvider(api_key=api_key, model_name=model_name)
        
        elif provider_type == "local":
            api_url = kwargs.get("api_url")
            if not api_url:
                raise ValueError("로컬 AI 제공자에는 API URL이 필요합니다.")
            
            return LocalAIProvider(api_url=api_url)
        
        else:
            raise ValueError(f"지원되지 않는 제공자 유형: {provider_type}")
