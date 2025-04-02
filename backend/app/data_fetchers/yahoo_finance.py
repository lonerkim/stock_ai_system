"""
Yahoo Finance API를 사용하여 주식 시장 데이터를 수집하는 모듈
"""
import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

sys.path.append('/opt/.manus/.sandbox-runtime')
try:
    from data_api import ApiClient
except ImportError:
    # 개발 환경에서 테스트할 때 사용할 모의 클라이언트
    class ApiClient:
        def call_api(self, api_name, query):
            logging.warning(f"모의 API 호출: {api_name}, 쿼리: {query}")
            return {"mock": "data"}

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """
    Yahoo Finance API를 사용하여 주식 데이터를 가져오는 클라이언트
    """
    
    def __init__(self):
        """
        Yahoo Finance API 클라이언트 초기화
        """
        self.client = ApiClient()
        logger.info("Yahoo Finance 클라이언트가 초기화되었습니다.")
    
    def get_stock_chart(
        self, 
        symbol: str, 
        region: str = "US", 
        interval: str = "1d", 
        range_period: str = "1mo",
        include_adjusted_close: bool = True
    ) -> Dict[str, Any]:
        """
        주식 차트 데이터를 가져옵니다.
        
        Args:
            symbol: 주식 심볼 (예: AAPL, 005930.KS)
            region: 지역 코드 (US, KR 등)
            interval: 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range_period: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            include_adjusted_close: 수정 종가 포함 여부
            
        Returns:
            주식 차트 데이터
        """
        try:
            logger.info(f"{symbol} 주식의 차트 데이터를 가져오는 중...")
            
            response = self.client.call_api(
                'YahooFinance/get_stock_chart', 
                query={
                    'symbol': symbol,
                    'region': region,
                    'interval': interval,
                    'range': range_period,
                    'includeAdjustedClose': include_adjusted_close
                }
            )
            
            logger.info(f"{symbol} 주식의 차트 데이터를 성공적으로 가져왔습니다.")
            return response
        except Exception as e:
            logger.error(f"{symbol} 주식의 차트 데이터를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def get_stock_holders(
        self, 
        symbol: str, 
        region: str = "US", 
        lang: str = "en-US"
    ) -> Dict[str, Any]:
        """
        주식 보유자 정보를 가져옵니다.
        
        Args:
            symbol: 주식 심볼 (예: AAPL, 005930.KS)
            region: 지역 코드 (US, KR 등)
            lang: 언어 코드
            
        Returns:
            주식 보유자 정보
        """
        try:
            logger.info(f"{symbol} 주식의 보유자 정보를 가져오는 중...")
            
            response = self.client.call_api(
                'YahooFinance/get_stock_holders', 
                query={
                    'symbol': symbol,
                    'region': region,
                    'lang': lang
                }
            )
            
            logger.info(f"{symbol} 주식의 보유자 정보를 성공적으로 가져왔습니다.")
            return response
        except Exception as e:
            logger.error(f"{symbol} 주식의 보유자 정보를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def get_stock_insights(self, symbol: str) -> Dict[str, Any]:
        """
        주식 인사이트 정보를 가져옵니다.
        
        Args:
            symbol: 주식 심볼 (예: AAPL, 005930.KS)
            
        Returns:
            주식 인사이트 정보
        """
        try:
            logger.info(f"{symbol} 주식의 인사이트 정보를 가져오는 중...")
            
            response = self.client.call_api(
                'YahooFinance/get_stock_insights', 
                query={
                    'symbol': symbol
                }
            )
            
            logger.info(f"{symbol} 주식의 인사이트 정보를 성공적으로 가져왔습니다.")
            return response
        except Exception as e:
            logger.error(f"{symbol} 주식의 인사이트 정보를 가져오는 중 오류 발생: {str(e)}")
            raise
