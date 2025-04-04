"""
Yahoo Finance API를 사용하여 주식 시장 데이터를 수집하는 모듈
"""
import sys
import os
import json
import logging
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

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

            # yfinance를 사용하여 실제 데이터 가져오기
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=range_period, interval=interval)

            # 데이터 형식 변환
            result = {
                "meta": {
                    "symbol": symbol,
                    "region": region,
                    "interval": interval,
                    "range": range_period,
                    "currency": ticker.info.get('currency', 'USD'),
                    "exchangeName": ticker.info.get('exchange', 'Unknown'),
                    "instrumentType": "EQUITY",
                    "firstTradeDate": int(hist.index[0].timestamp()) if not hist.empty else None,
                    "regularMarketTime": int(datetime.now().timestamp()),
                    "chartPreviousClose": hist['Close'].iloc[-2] if len(hist) > 1 else None,
                    "previousClose": hist['Close'].iloc[-2] if len(hist) > 1 else None,
                    "scale": 0,
                    "priceHint": 2
                },
                "timestamp": [int(date.timestamp()) for date in hist.index],
                "indicators": {
                    "quote": [{
                        "open": hist['Open'].tolist(),
                        "high": hist['High'].tolist(),
                        "low": hist['Low'].tolist(),
                        "close": hist['Close'].tolist(),
                        "volume": hist['Volume'].tolist()
                    }]
                }
            }

            # 수정 종가 포함 여부 확인
            if include_adjusted_close and 'Adj Close' in hist.columns:
                result["indicators"]["adjclose"] = [{
                    "adjclose": hist['Adj Close'].tolist()
                }]

            logger.info(f"{symbol} 주식의 차트 데이터를 성공적으로 가져왔습니다.")
            return result
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

            # yfinance를 사용하여 실제 데이터 가져오기
            ticker = yf.Ticker(symbol)

            # 결과 데이터 구성
            result = {
                "majorHolders": [],
                "institutionOwnership": [],
                "fundOwnership": []
            }

            # 주요 주주 정보 가져오기
            try:
                major_holders = ticker.major_holders
                if not major_holders.empty:
                    for i, row in major_holders.iterrows():
                        result["majorHolders"].append({
                            "percentage": row[0] if len(row) > 0 else "",
                            "description": row[1] if len(row) > 1 else ""
                        })
            except Exception as e:
                logger.warning(f"{symbol} 주요 주주 정보 가져오기 실패: {str(e)}")

            # 기관 소유 정보 가져오기
            try:
                institutional_holders = ticker.institutional_holders
                if not institutional_holders.empty:
                    for i, row in institutional_holders.iterrows():
                        result["institutionOwnership"].append({
                            "organization": row.get('Holder', ''),
                            "pctHeld": row.get('% Out', 0),
                            "position": row.get('Shares', 0),
                            "value": row.get('Value', 0),
                            "reportDate": row.get('Date Reported', '').strftime('%Y-%m-%d') if hasattr(row.get('Date Reported', ''), 'strftime') else ''
                        })
            except Exception as e:
                logger.warning(f"{symbol} 기관 소유 정보 가져오기 실패: {str(e)}")

            logger.info(f"{symbol} 주식의 보유자 정보를 성공적으로 가져왔습니다.")
            return result
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

            # yfinance를 사용하여 실제 데이터 가져오기
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # 결과 데이터 구성
            result = {
                "symbol": symbol,
                "instrumentInfo": {
                    "technicalEvents": {
                        "shortTerm": info.get('recommendationKey', 'NONE'),
                        "midTerm": info.get('recommendationKey', 'NONE'),
                        "longTerm": info.get('recommendationKey', 'NONE')
                    },
                    "recommendation": {
                        "targetPrice": info.get('targetMeanPrice', 0),
                        "rating": info.get('recommendationMean', 0),
                        "numberOfAnalysts": info.get('numberOfAnalystOpinions', 0)
                    },
                    "keyTechnicals": {
                        "beta": info.get('beta', 0),
                        "peRatio": info.get('trailingPE', 0),
                        "pegRatio": info.get('pegRatio', 0),
                        "forwardPE": info.get('forwardPE', 0),
                        "priceToBook": info.get('priceToBook', 0),
                        "dividendYield": info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
                    },
                    "valuation": {
                        "marketCap": info.get('marketCap', 0),
                        "enterpriseValue": info.get('enterpriseValue', 0),
                        "enterpriseToRevenue": info.get('enterpriseToRevenue', 0),
                        "enterpriseToEbitda": info.get('enterpriseToEbitda', 0)
                    }
                },
                "companySnapshot": {
                    "sectorInfo": {
                        "sector": info.get('sector', ''),
                        "industry": info.get('industry', '')
                    },
                    "company": {
                        "description": info.get('longBusinessSummary', ''),
                        "website": info.get('website', ''),
                        "fullTimeEmployees": info.get('fullTimeEmployees', 0)
                    }
                }
            }

            logger.info(f"{symbol} 주식의 인사이트 정보를 성공적으로 가져왔습니다.")
            return result
        except Exception as e:
            logger.error(f"{symbol} 주식의 인사이트 정보를 가져오는 중 오류 발생: {str(e)}")
            raise
