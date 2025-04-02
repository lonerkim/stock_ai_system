"""
주식 시장 데이터 정제 및 전처리 모듈
"""
import sys
import os
import json
import logging
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

class StockDataProcessor:
    """
    주식 시장 데이터를 정제하고 전처리하는 클래스
    """
    
    def __init__(self):
        """
        데이터 처리기 초기화
        """
        logger.info("주식 데이터 처리기가 초기화되었습니다.")
    
    def extract_time_series(self, stock_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Yahoo Finance API 응답에서 시계열 데이터를 추출하여 DataFrame으로 변환합니다.
        
        Args:
            stock_data: Yahoo Finance API 응답 데이터
            
        Returns:
            시계열 데이터가 포함된 DataFrame
        """
        try:
            logger.info("시계열 데이터 추출 중...")
            
            # API 응답 구조 확인
            if 'chart' not in stock_data or 'result' not in stock_data['chart']:
                raise ValueError("유효하지 않은 주식 데이터 형식입니다.")
            
            result = stock_data['chart']['result'][0]
            
            # 타임스탬프 추출
            timestamps = result.get('timestamp', [])
            
            # 가격 데이터 추출
            indicators = result.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            
            # 시가, 고가, 저가, 종가, 거래량 추출
            opens = quote.get('open', [])
            highs = quote.get('high', [])
            lows = quote.get('low', [])
            closes = quote.get('close', [])
            volumes = quote.get('volume', [])
            
            # 수정 종가 추출 (있는 경우)
            adjclose = []
            if 'adjclose' in indicators:
                adjclose = indicators['adjclose'][0].get('adjclose', [])
            
            # 메타 정보 추출
            meta = result.get('meta', {})
            symbol = meta.get('symbol', 'UNKNOWN')
            
            # DataFrame 생성
            data = {
                'timestamp': [datetime.fromtimestamp(ts) for ts in timestamps],
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'volume': volumes
            }
            
            if adjclose:
                data['adjclose'] = adjclose
            
            df = pd.DataFrame(data)
            df['symbol'] = symbol
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"{symbol} 주식의 시계열 데이터 추출 완료: {len(df)} 행")
            return df
        
        except Exception as e:
            logger.error(f"시계열 데이터 추출 중 오류 발생: {str(e)}")
            raise
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        주식 시계열 데이터에 기술적 지표를 추가합니다.
        
        Args:
            df: 주식 시계열 데이터가 포함된 DataFrame
            
        Returns:
            기술적 지표가 추가된 DataFrame
        """
        try:
            logger.info("기술적 지표 계산 중...")
            
            # 데이터 복사본 생성
            result_df = df.copy()
            
            # 이동평균선 (Moving Average)
            result_df['MA5'] = result_df['close'].rolling(window=5).mean()
            result_df['MA20'] = result_df['close'].rolling(window=20).mean()
            result_df['MA60'] = result_df['close'].rolling(window=60).mean()
            
            # 상대강도지수 (Relative Strength Index, RSI)
            delta = result_df['close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            
            rs = avg_gain / avg_loss
            result_df['RSI'] = 100 - (100 / (1 + rs))
            
            # 볼린저 밴드 (Bollinger Bands)
            result_df['BB_middle'] = result_df['close'].rolling(window=20).mean()
            result_df['BB_std'] = result_df['close'].rolling(window=20).std()
            result_df['BB_upper'] = result_df['BB_middle'] + (result_df['BB_std'] * 2)
            result_df['BB_lower'] = result_df['BB_middle'] - (result_df['BB_std'] * 2)
            
            # MACD (Moving Average Convergence Divergence)
            result_df['EMA12'] = result_df['close'].ewm(span=12, adjust=False).mean()
            result_df['EMA26'] = result_df['close'].ewm(span=26, adjust=False).mean()
            result_df['MACD'] = result_df['EMA12'] - result_df['EMA26']
            result_df['MACD_signal'] = result_df['MACD'].ewm(span=9, adjust=False).mean()
            result_df['MACD_hist'] = result_df['MACD'] - result_df['MACD_signal']
            
            # 일일 수익률 (Daily Returns)
            result_df['daily_return'] = result_df['close'].pct_change() * 100
            
            # 변동성 (Volatility) - 20일 표준편차
            result_df['volatility_20d'] = result_df['daily_return'].rolling(window=20).std()
            
            logger.info("기술적 지표 계산 완료")
            return result_df
        
        except Exception as e:
            logger.error(f"기술적 지표 계산 중 오류 발생: {str(e)}")
            raise
    
    def extract_market_summary(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 데이터에서 요약 정보를 추출합니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            시장 요약 정보
        """
        try:
            logger.info("시장 요약 정보 추출 중...")
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "indices": {},
                "top_gainers": [],
                "top_losers": [],
                "most_active": []
            }
            
            # 지수 정보 추출
            if 'indices' in market_data:
                for index_name, index_data in market_data['indices'].items():
                    if 'chart' in index_data and 'result' in index_data['chart']:
                        result = index_data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        # 최신 종가 가져오기
                        indicators = result.get('indicators', {})
                        quote = indicators.get('quote', [{}])[0]
                        closes = quote.get('close', [])
                        
                        if closes:
                            latest_close = closes[-1]
                            prev_close = meta.get('chartPreviousClose', 0)
                            change = latest_close - prev_close if prev_close else 0
                            change_percent = (change / prev_close * 100) if prev_close else 0
                            
                            summary['indices'][index_name] = {
                                "latest_close": latest_close,
                                "change": change,
                                "change_percent": change_percent,
                                "name": meta.get('shortName', index_name)
                            }
            
            # 주식 정보 처리
            if 'stocks' in market_data:
                stocks_data = []
                
                for symbol, stock_data in market_data['stocks'].items():
                    if 'chart' in stock_data and 'result' in stock_data['chart']:
                        result = stock_data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        # 최신 종가 가져오기
                        indicators = result.get('indicators', {})
                        quote = indicators.get('quote', [{}])[0]
                        closes = quote.get('close', [])
                        volumes = quote.get('volume', [])
                        
                        if closes and volumes:
                            latest_close = closes[-1]
                            latest_volume = volumes[-1]
                            prev_close = meta.get('chartPreviousClose', 0)
                            change = latest_close - prev_close if prev_close else 0
                            change_percent = (change / prev_close * 100) if prev_close else 0
                            
                            stock_info = {
                                "symbol": symbol,
                                "name": meta.get('shortName', symbol),
                                "latest_close": latest_close,
                                "change": change,
                                "change_percent": change_percent,
                                "volume": latest_volume
                            }
                            
                            stocks_data.append(stock_info)
                
                # 상승률 상위 종목
                top_gainers = sorted(stocks_data, key=lambda x: x['change_percent'], reverse=True)[:5]
                summary['top_gainers'] = top_gainers
                
                # 하락률 상위 종목
                top_losers = sorted(stocks_data, key=lambda x: x['change_percent'])[:5]
                summary['top_losers'] = top_losers
                
                # 거래량 상위 종목
                most_active = sorted(stocks_data, key=lambda x: x['volume'], reverse=True)[:5]
                summary['most_active'] = most_active
            
            logger.info("시장 요약 정보 추출 완료")
            return summary
        
        except Exception as e:
            logger.error(f"시장 요약 정보 추출 중 오류 발생: {str(e)}")
            raise
    
    def generate_market_text(self, market_summary: Dict[str, Any]) -> str:
        """
        시장 요약 정보를 텍스트로 변환합니다.
        
        Args:
            market_summary: 시장 요약 정보
            
        Returns:
            시장 요약 텍스트
        """
        try:
            logger.info("시장 요약 텍스트 생성 중...")
            
            text_parts = []
            
            # 타임스탬프
            timestamp = datetime.fromisoformat(market_summary['timestamp'])
            text_parts.append(f"시장 요약 (기준 시간: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            text_parts.append("")
            
            # 지수 정보
            text_parts.append("주요 지수:")
            for index_name, index_info in market_summary.get('indices', {}).items():
                change_sign = "+" if index_info['change'] >= 0 else ""
                text_parts.append(f"- {index_info['name']}: {index_info['latest_close']:.2f} ({change_sign}{index_info['change']:.2f}, {change_sign}{index_info['change_percent']:.2f}%)")
            text_parts.append("")
            
            # 상승률 상위 종목
            text_parts.append("상승률 상위 종목:")
            for stock in market_summary.get('top_gainers', []):
                text_parts.append(f"- {stock['name']} ({stock['symbol']}): {stock['latest_close']:.2f} (+{stock['change']:.2f}, +{stock['change_percent']:.2f}%)")
            text_parts.append("")
            
            # 하락률 상위 종목
            text_parts.append("하락률 상위 종목:")
            for stock in market_summary.get('top_losers', []):
                text_parts.append(f"- {stock['name']} ({stock['symbol']}): {stock['latest_close']:.2f} ({stock['change']:.2f}, {stock['change_percent']:.2f}%)")
            text_parts.append("")
            
            # 거래량 상위 종목
            text_parts.append("거래량 상위 종목:")
            for stock in market_summary.get('most_active', []):
                change_sign = "+" if stock['change'] >= 0 else ""
                text_parts.append(f"- {stock['name']} ({stock['symbol']}): {stock['latest_close']:.2f} ({change_sign}{stock['change']:.2f}, {change_sign}{stock['change_percent']:.2f}%), 거래량: {stock['volume']:,}")
            
            logger.info("시장 요약 텍스트 생성 완료")
            return "\n".join(text_parts)
        
        except Exception as e:
            logger.error(f"시장 요약 텍스트 생성 중 오류 발생: {str(e)}")
            raise
    
    def process_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        시장 데이터를 처리하여 분석에 필요한 형태로 변환합니다.
        
        Args:
            market_data: 원본 시장 데이터
            
        Returns:
            처리된 시장 데이터
        """
        try:
            logger.info("시장 데이터 처리 중...")
            
            processed_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": self.extract_market_summary(market_data),
                "indices": {},
                "stocks": {},
                "insights": market_data.get('insights', {}),
                "holders": market_data.get('holders', {})
            }
            
            # 지수 데이터 처리
            for index_name, index_data in market_data.get('indices', {}).items():
                try:
                    df = self.extract_time_series(index_data)
                    df_with_indicators = self.calculate_technical_indicators(df)
                    processed_data['indices'][index_name] = {
                        "dataframe": df_with_indicators,
                        "last_update": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.warning(f"{index_name} 지수 데이터 처리 중 오류 발생: {str(e)}")
                    continue
            
            # 주식 데이터 처리
            for symbol, stock_data in market_data.get('stocks', {}).items():
                try:
                    df = self.extract_time_series(stock_data)
                    df_with_indicators = self.calculate_technical_indicators(df)
                    processed_data['stocks'][symbol] = {
                        "dataframe": df_with_indicators,
                        "last_update": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.warning(f"{symbol} 주식 데이터 처리 중 오류 발생: {str(e)}")
                    continue
            
            # 시장 요약 텍스트 생성
            processed_data['summary_text'] = self.generate_market_text(processed_data['summary'])
            
            logger.info("시장 데이터 처리 완료")
            return processed_data
        
        except Exception as e:
            logger.error(f"시장 데이터 처리 중 오류 발생: {str(e)}")
            raise
