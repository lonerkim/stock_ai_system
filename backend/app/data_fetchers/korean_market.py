"""
한국 주식 시장 데이터를 수집하는 모듈
"""
import sys
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from .yahoo_finance import YahooFinanceClient

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KoreanStockMarketFetcher:
    """
    한국 주식 시장 데이터를 수집하는 클래스
    """
    
    def __init__(self):
        """
        한국 주식 시장 데이터 수집기 초기화
        """
        self.yahoo_client = YahooFinanceClient()
        self.kospi_symbol = "^KS11"  # KOSPI 지수
        self.kosdaq_symbol = "^KQ11"  # KOSDAQ 지수
        
        # 주요 한국 블루칩 주식 목록 (심볼은 .KS 또는 .KQ 접미사 포함)
        self.bluechip_stocks = [
            "005930.KS",  # 삼성전자
            "000660.KS",  # SK하이닉스
            "035420.KS",  # NAVER
            "035720.KS",  # 카카오
            "051910.KS",  # LG화학
            "005380.KS",  # 현대자동차
            "000270.KS",  # 기아
            "068270.KS",  # 셀트리온
            "207940.KS",  # 삼성바이오로직스
            "006400.KS",  # 삼성SDI
        ]
        
        logger.info("한국 주식 시장 데이터 수집기가 초기화되었습니다.")
    
    def get_market_indices(self, interval: str = "1d", range_period: str = "1mo") -> Dict[str, Any]:
        """
        한국 주요 시장 지수 데이터를 가져옵니다.
        
        Args:
            interval: 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range_period: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            KOSPI 및 KOSDAQ 지수 데이터
        """
        try:
            logger.info("한국 주요 시장 지수 데이터를 가져오는 중...")
            
            kospi_data = self.yahoo_client.get_stock_chart(
                symbol=self.kospi_symbol,
                region="US",  # 국제 지수는 US 리전으로 조회
                interval=interval,
                range_period=range_period
            )
            
            kosdaq_data = self.yahoo_client.get_stock_chart(
                symbol=self.kosdaq_symbol,
                region="US",  # 국제 지수는 US 리전으로 조회
                interval=interval,
                range_period=range_period
            )
            
            logger.info("한국 주요 시장 지수 데이터를 성공적으로 가져왔습니다.")
            
            return {
                "kospi": kospi_data,
                "kosdaq": kosdaq_data
            }
        except Exception as e:
            logger.error(f"한국 주요 시장 지수 데이터를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def get_bluechip_stocks_data(self, interval: str = "1d", range_period: str = "1mo") -> Dict[str, Any]:
        """
        한국 블루칩 주식 데이터를 가져옵니다.
        
        Args:
            interval: 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range_period: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            블루칩 주식 데이터
        """
        try:
            logger.info("한국 블루칩 주식 데이터를 가져오는 중...")
            
            results = {}
            for symbol in self.bluechip_stocks:
                stock_data = self.yahoo_client.get_stock_chart(
                    symbol=symbol,
                    region="KR",
                    interval=interval,
                    range_period=range_period
                )
                
                # 심볼에서 .KS 또는 .KQ 접미사 제거
                clean_symbol = symbol.split('.')[0]
                results[clean_symbol] = stock_data
                
                # API 호출 간 짧은 지연 추가 (선택 사항)
                # time.sleep(0.5)
            
            logger.info("한국 블루칩 주식 데이터를 성공적으로 가져왔습니다.")
            return results
        except Exception as e:
            logger.error(f"한국 블루칩 주식 데이터를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def get_stock_insights(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        한국 주식 인사이트 정보를 가져옵니다.
        
        Args:
            symbols: 주식 심볼 목록 (제공되지 않으면 기본 블루칩 목록 사용)
            
        Returns:
            주식 인사이트 정보
        """
        try:
            if symbols is None:
                symbols = self.bluechip_stocks
                
            logger.info("한국 주식 인사이트 정보를 가져오는 중...")
            
            results = {}
            for symbol in symbols:
                try:
                    insights = self.yahoo_client.get_stock_insights(symbol=symbol)
                    
                    # 심볼에서 .KS 또는 .KQ 접미사 제거
                    clean_symbol = symbol.split('.')[0]
                    results[clean_symbol] = insights
                    
                    # API 호출 간 짧은 지연 추가 (선택 사항)
                    # time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"{symbol} 주식의 인사이트 정보를 가져오는 중 오류 발생: {str(e)}")
                    continue
            
            logger.info("한국 주식 인사이트 정보를 성공적으로 가져왔습니다.")
            return results
        except Exception as e:
            logger.error(f"한국 주식 인사이트 정보를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def fetch_all_market_data(self, interval: str = "1d", range_period: str = "1mo") -> Dict[str, Any]:
        """
        모든 한국 시장 데이터를 한 번에 가져옵니다.
        
        Args:
            interval: 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range_period: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            모든 한국 시장 데이터
        """
        try:
            logger.info("모든 한국 시장 데이터를 가져오는 중...")
            
            # 시장 지수 데이터 가져오기
            indices_data = self.get_market_indices(interval=interval, range_period=range_period)
            
            # 블루칩 주식 데이터 가져오기
            stocks_data = self.get_bluechip_stocks_data(interval=interval, range_period=range_period)
            
            # 주식 인사이트 정보 가져오기
            insights_data = self.get_stock_insights()
            
            logger.info("모든 한국 시장 데이터를 성공적으로 가져왔습니다.")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "indices": indices_data,
                "stocks": stocks_data,
                "insights": insights_data
            }
        except Exception as e:
            logger.error(f"모든 한국 시장 데이터를 가져오는 중 오류 발생: {str(e)}")
            raise
