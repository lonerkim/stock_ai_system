"""
미국 주식 시장 데이터를 수집하는 모듈
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

class USStockMarketFetcher:
    """
    미국 주식 시장 데이터를 수집하는 클래스
    """
    
    def __init__(self):
        """
        미국 주식 시장 데이터 수집기 초기화
        """
        self.yahoo_client = YahooFinanceClient()
        self.sp500_symbol = "^GSPC"  # S&P 500 지수
        self.dow_symbol = "^DJI"     # 다우존스 산업평균지수
        self.nasdaq_symbol = "^IXIC"  # 나스닥 종합지수
        
        # 주요 미국 블루칩 주식 목록
        self.bluechip_stocks = [
            "AAPL",   # Apple
            "MSFT",   # Microsoft
            "AMZN",   # Amazon
            "GOOGL",  # Alphabet (Google)
            "META",   # Meta (Facebook)
            "TSLA",   # Tesla
            "NVDA",   # NVIDIA
            "JPM",    # JPMorgan Chase
            "JNJ",    # Johnson & Johnson
            "V",      # Visa
        ]
        
        logger.info("미국 주식 시장 데이터 수집기가 초기화되었습니다.")
    
    def get_market_indices(self, interval: str = "1d", range_period: str = "1mo") -> Dict[str, Any]:
        """
        미국 주요 시장 지수 데이터를 가져옵니다.
        
        Args:
            interval: 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range_period: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            S&P 500, 다우존스, 나스닥 지수 데이터
        """
        try:
            logger.info("미국 주요 시장 지수 데이터를 가져오는 중...")
            
            sp500_data = self.yahoo_client.get_stock_chart(
                symbol=self.sp500_symbol,
                region="US",
                interval=interval,
                range_period=range_period
            )
            
            dow_data = self.yahoo_client.get_stock_chart(
                symbol=self.dow_symbol,
                region="US",
                interval=interval,
                range_period=range_period
            )
            
            nasdaq_data = self.yahoo_client.get_stock_chart(
                symbol=self.nasdaq_symbol,
                region="US",
                interval=interval,
                range_period=range_period
            )
            
            logger.info("미국 주요 시장 지수 데이터를 성공적으로 가져왔습니다.")
            
            return {
                "sp500": sp500_data,
                "dow": dow_data,
                "nasdaq": nasdaq_data
            }
        except Exception as e:
            logger.error(f"미국 주요 시장 지수 데이터를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def get_bluechip_stocks_data(self, interval: str = "1d", range_period: str = "1mo") -> Dict[str, Any]:
        """
        미국 블루칩 주식 데이터를 가져옵니다.
        
        Args:
            interval: 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range_period: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            블루칩 주식 데이터
        """
        try:
            logger.info("미국 블루칩 주식 데이터를 가져오는 중...")
            
            results = {}
            for symbol in self.bluechip_stocks:
                stock_data = self.yahoo_client.get_stock_chart(
                    symbol=symbol,
                    region="US",
                    interval=interval,
                    range_period=range_period
                )
                
                results[symbol] = stock_data
                
                # API 호출 간 짧은 지연 추가 (선택 사항)
                # time.sleep(0.5)
            
            logger.info("미국 블루칩 주식 데이터를 성공적으로 가져왔습니다.")
            return results
        except Exception as e:
            logger.error(f"미국 블루칩 주식 데이터를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def get_stock_insights(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        미국 주식 인사이트 정보를 가져옵니다.
        
        Args:
            symbols: 주식 심볼 목록 (제공되지 않으면 기본 블루칩 목록 사용)
            
        Returns:
            주식 인사이트 정보
        """
        try:
            if symbols is None:
                symbols = self.bluechip_stocks
                
            logger.info("미국 주식 인사이트 정보를 가져오는 중...")
            
            results = {}
            for symbol in symbols:
                try:
                    insights = self.yahoo_client.get_stock_insights(symbol=symbol)
                    results[symbol] = insights
                    
                    # API 호출 간 짧은 지연 추가 (선택 사항)
                    # time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"{symbol} 주식의 인사이트 정보를 가져오는 중 오류 발생: {str(e)}")
                    continue
            
            logger.info("미국 주식 인사이트 정보를 성공적으로 가져왔습니다.")
            return results
        except Exception as e:
            logger.error(f"미국 주식 인사이트 정보를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def get_stock_holders(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        미국 주식 보유자 정보를 가져옵니다.
        
        Args:
            symbols: 주식 심볼 목록 (제공되지 않으면 기본 블루칩 목록 사용)
            
        Returns:
            주식 보유자 정보
        """
        try:
            if symbols is None:
                symbols = self.bluechip_stocks
                
            logger.info("미국 주식 보유자 정보를 가져오는 중...")
            
            results = {}
            for symbol in symbols:
                try:
                    holders = self.yahoo_client.get_stock_holders(
                        symbol=symbol,
                        region="US",
                        lang="en-US"
                    )
                    results[symbol] = holders
                    
                    # API 호출 간 짧은 지연 추가 (선택 사항)
                    # time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"{symbol} 주식의 보유자 정보를 가져오는 중 오류 발생: {str(e)}")
                    continue
            
            logger.info("미국 주식 보유자 정보를 성공적으로 가져왔습니다.")
            return results
        except Exception as e:
            logger.error(f"미국 주식 보유자 정보를 가져오는 중 오류 발생: {str(e)}")
            raise
    
    def fetch_all_market_data(self, interval: str = "1d", range_period: str = "1mo") -> Dict[str, Any]:
        """
        모든 미국 시장 데이터를 한 번에 가져옵니다.
        
        Args:
            interval: 데이터 간격 (1m, 2m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            range_period: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            모든 미국 시장 데이터
        """
        try:
            logger.info("모든 미국 시장 데이터를 가져오는 중...")
            
            # 시장 지수 데이터 가져오기
            indices_data = self.get_market_indices(interval=interval, range_period=range_period)
            
            # 블루칩 주식 데이터 가져오기
            stocks_data = self.get_bluechip_stocks_data(interval=interval, range_period=range_period)
            
            # 주식 인사이트 정보 가져오기
            insights_data = self.get_stock_insights()
            
            # 주식 보유자 정보 가져오기
            holders_data = self.get_stock_holders()
            
            logger.info("모든 미국 시장 데이터를 성공적으로 가져왔습니다.")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "indices": indices_data,
                "stocks": stocks_data,
                "insights": insights_data,
                "holders": holders_data
            }
        except Exception as e:
            logger.error(f"모든 미국 시장 데이터를 가져오는 중 오류 발생: {str(e)}")
            raise
