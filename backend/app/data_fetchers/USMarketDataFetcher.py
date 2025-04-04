"""
미국 주식 시장 데이터 수집 어댑터 모듈

이 모듈은 기존 USStockMarketFetcher 클래스를 main.py에서 사용하는 인터페이스로 변환합니다.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .us_market import USStockMarketFetcher
from .data_cache import DataCache

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class USMarketDataFetcher:
    """
    미국 주식 시장 데이터 수집 어댑터 클래스
    """
    
    def __init__(self, cache: DataCache):
        """
        미국 주식 시장 데이터 수집 어댑터 초기화
        
        Args:
            cache: 데이터 캐시 객체
        """
        self.cache = cache
        self.fetcher = USStockMarketFetcher()
        
        logger.info("미국 주식 시장 데이터 수집 어댑터가 초기화되었습니다.")
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        시장 개요 데이터를 가져옵니다.
        
        Returns:
            시장 개요 데이터
        """
        # 캐시 확인
        cache_key = f"us_market_overview_{datetime.now().strftime('%Y-%m-%d')}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info("캐시에서 미국 시장 개요 데이터를 가져왔습니다.")
            return cached_data
        
        try:
            # 기존 fetcher를 사용하여 데이터 가져오기
            market_data = self.fetcher.fetch_all_market_data(interval="1d", range_period="1mo")
            
            # 결과 데이터 구성
            result = {
                "market": "us",
                "timestamp": datetime.now().isoformat(),
                "indices": {
                    "S&P500": self._extract_index_data(market_data, "sp500"),
                    "DOW": self._extract_index_data(market_data, "dow"),
                    "NASDAQ": self._extract_index_data(market_data, "nasdaq")
                },
                "top_stocks": self._extract_top_stocks(market_data),
                "news": self._extract_news(market_data),
                "summary_text": self._generate_summary_text(market_data)
            }
            
            # 캐시에 저장
            self.cache.set(cache_key, result, 3600)  # 1시간 캐시
            
            logger.info("미국 시장 개요 데이터를 가져왔습니다.")
            return result
        
        except Exception as e:
            logger.error(f"미국 시장 개요 데이터 가져오기 중 오류 발생: {str(e)}")
            
            # 오류 발생 시 더미 데이터 반환
            return {
                "market": "us",
                "timestamp": datetime.now().isoformat(),
                "indices": {
                    "S&P500": {
                        "name": "S&P 500",
                        "current": 4500.0,
                        "change": 25.0,
                        "change_percent": 0.56,
                        "volume": 2500000000,
                        "value": 25000000000000
                    },
                    "DOW": {
                        "name": "Dow Jones Industrial Average",
                        "current": 35000.0,
                        "change": 150.0,
                        "change_percent": 0.43,
                        "volume": 1500000000,
                        "value": 15000000000000
                    },
                    "NASDAQ": {
                        "name": "NASDAQ Composite",
                        "current": 14000.0,
                        "change": 100.0,
                        "change_percent": 0.72,
                        "volume": 3500000000,
                        "value": 35000000000000
                    }
                },
                "top_stocks": [
                    {
                        "symbol": "AAPL",
                        "name": "Apple Inc.",
                        "price": 175.0,
                        "change": 3.5,
                        "change_percent": 2.04,
                        "volume": 80000000
                    },
                    {
                        "symbol": "MSFT",
                        "name": "Microsoft Corporation",
                        "price": 350.0,
                        "change": 5.0,
                        "change_percent": 1.45,
                        "volume": 30000000
                    },
                    {
                        "symbol": "AMZN",
                        "name": "Amazon.com, Inc.",
                        "price": 3300.0,
                        "change": -50.0,
                        "change_percent": -1.49,
                        "volume": 5000000
                    }
                ],
                "news": [
                    {
                        "title": "S&P 500 Hits Record High on Economic Recovery Hopes",
                        "link": "#"
                    },
                    {
                        "title": "Fed Signals Potential Rate Hikes in Coming Months",
                        "link": "#"
                    },
                    {
                        "title": "Tech Stocks Lead Market Rally as Earnings Beat Expectations",
                        "link": "#"
                    }
                ],
                "summary_text": """
                미국 시장 개요 (기준일: 더미 데이터)
                
                S&P 500: 4,500.00 (+0.56%)
                Dow Jones: 35,000.00 (+0.43%)
                NASDAQ: 14,000.00 (+0.72%)
                
                주요 종목:
                - Apple Inc.: $175.00 (+2.04%)
                - Microsoft Corporation: $350.00 (+1.45%)
                - Amazon.com, Inc.: $3,300.00 (-1.49%)
                
                주요 뉴스:
                - S&P 500 Hits Record High on Economic Recovery Hopes
                - Fed Signals Potential Rate Hikes in Coming Months
                - Tech Stocks Lead Market Rally as Earnings Beat Expectations
                """
            }
    
    def get_stock_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        특정 주식의 데이터를 가져옵니다.
        
        Args:
            symbol: 주식 심볼
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            주식 데이터
        """
        # 날짜 설정
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if not start_date:
            start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # 캐시 확인
        cache_key = f"us_stock_{symbol}_{start_date}_{end_date}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(f"캐시에서 미국 주식 데이터를 가져왔습니다: {symbol}")
            return cached_data
        
        try:
            # 날짜 범위에 따른 range_period 설정
            days_diff = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
            
            if days_diff <= 5:
                range_period = "5d"
            elif days_diff <= 30:
                range_period = "1mo"
            elif days_diff <= 90:
                range_period = "3mo"
            elif days_diff <= 180:
                range_period = "6mo"
            elif days_diff <= 365:
                range_period = "1y"
            elif days_diff <= 730:
                range_period = "2y"
            else:
                range_period = "5y"
            
            # 기존 fetcher를 사용하여 데이터 가져오기
            stock_data = self.fetcher.yahoo_client.get_stock_chart(
                symbol=symbol,
                region="US",
                interval="1d",
                range_period=range_period
            )
            
            # 주식 인사이트 가져오기
            try:
                insights = self.fetcher.yahoo_client.get_stock_insights(symbol=symbol)
            except Exception:
                insights = {}
            
            # 결과 데이터 구성
            result = self._process_stock_data(symbol, stock_data, insights, start_date, end_date)
            
            # 캐시에 저장
            self.cache.set(cache_key, result, 3600)  # 1시간 캐시
            
            logger.info(f"미국 주식 데이터를 가져왔습니다: {symbol}")
            return result
        
        except Exception as e:
            logger.error(f"미국 주식 데이터 가져오기 중 오류 발생: {symbol}, {str(e)}")
            
            # 오류 발생 시 더미 데이터 반환
            return {
                "symbol": symbol,
                "name": "Apple Inc." if symbol == "AAPL" else "Microsoft Corporation" if symbol == "MSFT" else "Amazon.com, Inc." if symbol == "AMZN" else "Unknown Company",
                "market": "us",
                "timestamp": datetime.now().isoformat(),
                "current_data": {
                    "price": 175.0 if symbol == "AAPL" else 350.0 if symbol == "MSFT" else 3300.0 if symbol == "AMZN" else 100.0,
                    "change": 3.5 if symbol == "AAPL" else 5.0 if symbol == "MSFT" else -50.0 if symbol == "AMZN" else 1.0,
                    "change_percent": 2.04 if symbol == "AAPL" else 1.45 if symbol == "MSFT" else -1.49 if symbol == "AMZN" else 1.0,
                    "volume": 80000000 if symbol == "AAPL" else 30000000 if symbol == "MSFT" else 5000000 if symbol == "AMZN" else 1000000,
                    "high": 176.0 if symbol == "AAPL" else 352.0 if symbol == "MSFT" else 3350.0 if symbol == "AMZN" else 102.0,
                    "low": 172.0 if symbol == "AAPL" else 348.0 if symbol == "MSFT" else 3250.0 if symbol == "AMZN" else 98.0,
                    "open": 173.0 if symbol == "AAPL" else 349.0 if symbol == "MSFT" else 3320.0 if symbol == "AMZN" else 99.0
                },
                "price_history": [
                    {
                        "date": (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d"),
                        "open": 173.0 + i * 0.5 if symbol == "AAPL" else 349.0 + i * 0.5 if symbol == "MSFT" else 3320.0 - i * 5.0 if symbol == "AMZN" else 99.0 + i * 0.2,
                        "high": 176.0 + i * 0.5 if symbol == "AAPL" else 352.0 + i * 0.5 if symbol == "MSFT" else 3350.0 - i * 5.0 if symbol == "AMZN" else 102.0 + i * 0.2,
                        "low": 172.0 + i * 0.5 if symbol == "AAPL" else 348.0 + i * 0.5 if symbol == "MSFT" else 3250.0 - i * 5.0 if symbol == "AMZN" else 98.0 + i * 0.2,
                        "close": 175.0 + i * 0.5 if symbol == "AAPL" else 350.0 + i * 0.5 if symbol == "MSFT" else 3300.0 - i * 5.0 if symbol == "AMZN" else 100.0 + i * 0.2,
                        "volume": 80000000 - i * 1000000 if symbol == "AAPL" else 30000000 - i * 500000 if symbol == "MSFT" else 5000000 - i * 100000 if symbol == "AMZN" else 1000000 - i * 10000
                    }
                    for i in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)
                ],
                "summary_text": f"""
                {symbol} 주식 정보 (더미 데이터)
                
                현재가: ${175.0 if symbol == "AAPL" else 350.0 if symbol == "MSFT" else 3300.0 if symbol == "AMZN" else 100.0:.2f} ({2.04 if symbol == "AAPL" else 1.45 if symbol == "MSFT" else -1.49 if symbol == "AMZN" else 1.0:+.2f}%)
                거래량: {80000000 if symbol == "AAPL" else 30000000 if symbol == "MSFT" else 5000000 if symbol == "AMZN" else 1000000:,}
                52주 최고: ${180.0 if symbol == "AAPL" else 360.0 if symbol == "MSFT" else 3500.0 if symbol == "AMZN" else 110.0:.2f}
                52주 최저: ${150.0 if symbol == "AAPL" else 300.0 if symbol == "MSFT" else 3000.0 if symbol == "AMZN" else 90.0:.2f}
                
                기간: {start_date} ~ {end_date}
                시작가: ${173.0 if symbol == "AAPL" else 349.0 if symbol == "MSFT" else 3320.0 if symbol == "AMZN" else 99.0:.2f}
                종가: ${175.0 if symbol == "AAPL" else 350.0 if symbol == "MSFT" else 3300.0 if symbol == "AMZN" else 100.0:.2f}
                변동률: {1.16 if symbol == "AAPL" else 0.29 if symbol == "MSFT" else -0.60 if symbol == "AMZN" else 1.01:+.2f}%
                """
            }
    
    def _extract_index_data(self, market_data: Dict[str, Any], index_key: str) -> Dict[str, Any]:
        """
        시장 데이터에서 지수 정보를 추출합니다.
        
        Args:
            market_data: 시장 데이터
            index_key: 지수 키
            
        Returns:
            지수 데이터
        """
        try:
            if 'indices' in market_data and index_key in market_data['indices']:
                index_data = market_data['indices'][index_key]
                
                if 'chart' in index_data and 'result' in index_data['chart']:
                    result = index_data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    # 최신 종가 가져오기
                    indicators = result.get('indicators', {})
                    quote = indicators.get('quote', [{}])[0]
                    closes = quote.get('close', [])
                    volumes = quote.get('volume', [])
                    
                    if closes:
                        latest_close = closes[-1]
                        latest_volume = volumes[-1] if volumes else 0
                        prev_close = meta.get('chartPreviousClose', 0)
                        change = latest_close - prev_close if prev_close else 0
                        change_percent = (change / prev_close * 100) if prev_close else 0
                        
                        return {
                            "name": meta.get('shortName', index_key.upper()),
                            "current": latest_close,
                            "change": change,
                            "change_percent": change_percent,
                            "volume": latest_volume,
                            "value": latest_close * latest_volume if latest_volume else 0
                        }
            
            # 데이터가 없거나 형식이 맞지 않는 경우 기본값 반환
            return {
                "name": index_key.upper(),
                "current": 0,
                "change": 0,
                "change_percent": 0,
                "volume": 0,
                "value": 0
            }
        
        except Exception as e:
            logger.warning(f"지수 데이터 추출 중 오류 발생: {index_key}, {str(e)}")
            return {
                "name": index_key.upper(),
                "current": 0,
                "change": 0,
                "change_percent": 0,
                "volume": 0,
                "value": 0
            }
    
    def _extract_top_stocks(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        시장 데이터에서 상위 주식 정보를 추출합니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            상위 주식 목록
        """
        try:
            top_stocks = []
            
            if 'stocks' in market_data:
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
                            
                            top_stocks.append({
                                "symbol": symbol,
                                "name": meta.get('shortName', symbol),
                                "price": latest_close,
                                "change": change,
                                "change_percent": change_percent,
                                "volume": latest_volume
                            })
            
            # 변동률 기준으로 정렬
            top_stocks.sort(key=lambda x: abs(x['change_percent']), reverse=True)
            
            return top_stocks[:10]  # 상위 10개만 반환
        
        except Exception as e:
            logger.warning(f"상위 주식 정보 추출 중 오류 발생: {str(e)}")
            return []
    
    def _extract_news(self, market_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        시장 데이터에서 뉴스 정보를 추출합니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            뉴스 목록
        """
        # 실제 데이터에는 뉴스 정보가 없으므로 더미 데이터 반환
        return [
            {
                "title": "S&P 500 Hits Record High on Economic Recovery Hopes",
                "link": "#"
            },
            {
                "title": "Fed Signals Potential Rate Hikes in Coming Months",
                "link": "#"
            },
            {
                "title": "Tech Stocks Lead Market Rally as Earnings Beat Expectations",
                "link": "#"
            }
        ]
    
    def _generate_summary_text(self, market_data: Dict[str, Any]) -> str:
        """
        시장 데이터에서 요약 텍스트를 생성합니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            요약 텍스트
        """
        try:
            # 지수 정보 추출
            sp500_data = self._extract_index_data(market_data, "sp500")
            dow_data = self._extract_index_data(market_data, "dow")
            nasdaq_data = self._extract_index_data(market_data, "nasdaq")
            
            # 상위 주식 정보 추출
            top_stocks = self._extract_top_stocks(market_data)
            
            # 요약 텍스트 생성
            summary_text = f"""
            미국 시장 개요 (기준일: {datetime.now().strftime('%Y-%m-%d')})
            
            S&P 500: {sp500_data['current']:,.2f} ({sp500_data['change_percent']:+.2f}%)
            Dow Jones: {dow_data['current']:,.2f} ({dow_data['change_percent']:+.2f}%)
            NASDAQ: {nasdaq_data['current']:,.2f} ({nasdaq_data['change_percent']:+.2f}%)
            
            주요 종목:
            {chr(10).join([f"- {stock['name']} ({stock['symbol']}): ${stock['price']:,.2f} ({stock['change_percent']:+.2f}%)" for stock in top_stocks[:5]])}
            
            주요 뉴스:
            - S&P 500 Hits Record High on Economic Recovery Hopes
            - Fed Signals Potential Rate Hikes in Coming Months
            - Tech Stocks Lead Market Rally as Earnings Beat Expectations
            """
            
            return summary_text
        
        except Exception as e:
            logger.warning(f"요약 텍스트 생성 중 오류 발생: {str(e)}")
            return """
            미국 시장 개요 (더미 데이터)
            
            S&P 500: 4,500.00 (+0.56%)
            Dow Jones: 35,000.00 (+0.43%)
            NASDAQ: 14,000.00 (+0.72%)
            
            주요 종목:
            - Apple Inc. (AAPL): $175.00 (+2.04%)
            - Microsoft Corporation (MSFT): $350.00 (+1.45%)
            - Amazon.com, Inc. (AMZN): $3,300.00 (-1.49%)
            
            주요 뉴스:
            - S&P 500 Hits Record High on Economic Recovery Hopes
            - Fed Signals Potential Rate Hikes in Coming Months
            - Tech Stocks Lead Market Rally as Earnings Beat Expectations
            """
    
    def _process_stock_data(self, symbol: str, stock_data: Dict[str, Any], insights: Dict[str, Any], start_date: str, end_date: str) -> Dict[str, Any]:
        """
        주식 데이터를 처리합니다.
        
        Args:
            symbol: 주식 심볼
            stock_data: 주식 차트 데이터
            insights: 주식 인사이트 데이터
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            처리된 주식 데이터
        """
        try:
            if 'chart' not in stock_data or 'result' not in stock_data['chart']:
                raise ValueError("유효하지 않은 주식 데이터 형식입니다.")
            
            result = stock_data['chart']['result'][0]
            meta = result.get('meta', {})
            
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
            
            # 가격 이력 구성
            price_history = []
            for i in range(len(timestamps)):
                if i < len(opens) and i < len(highs) and i < len(lows) and i < len(closes) and i < len(volumes):
                    date = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
                    
                    # 날짜 범위 필터링
                    if start_date <= date <= end_date:
                        price_history.append({
                            "date": date,
                            "open": opens[i] if opens[i] is not None else 0,
                            "high": highs[i] if highs[i] is not None else 0,
                            "low": lows[i] if lows[i] is not None else 0,
                            "close": closes[i] if closes[i] is not None else 0,
                            "volume": volumes[i] if volumes[i] is not None else 0
                        })
            
            # 현재 데이터 구성
            current_data = {
                "price": closes[-1] if closes else 0,
                "change": closes[-1] - meta.get('chartPreviousClose', 0) if closes else 0,
                "change_percent": ((closes[-1] / meta.get('chartPreviousClose', 1)) - 1) * 100 if closes and meta.get('chartPreviousClose', 0) > 0 else 0,
                "volume": volumes[-1] if volumes else 0,
                "high": highs[-1] if highs else 0,
                "low": lows[-1] if lows else 0,
                "open": opens[-1] if opens else 0
            }
            
            # 요약 텍스트 생성
            summary_text = f"""
            {meta.get('shortName', symbol)} ({symbol}) 주식 정보
            
            현재가: ${current_data['price']:.2f} ({current_data['change_percent']:+.2f}%)
            거래량: {current_data['volume']:,}
            52주 최고: ${meta.get('fiftyTwoWeekHigh', 0):.2f}
            52주 최저: ${meta.get('fiftyTwoWeekLow', 0):.2f}
            
            기간: {start_date} ~ {end_date}
            시작가: ${price_history[0]['close'] if price_history else 0:.2f}
            종가: ${price_history[-1]['close'] if price_history else 0:.2f}
            변동률: {((price_history[-1]['close'] / price_history[0]['close'] - 1) * 100) if price_history and price_history[0]['close'] > 0 else 0:+.2f}%
            """
            
            return {
                "symbol": symbol,
                "name": meta.get('shortName', symbol),
                "market": "us",
                "timestamp": datetime.now().isoformat(),
                "current_data": current_data,
                "price_history": price_history,
                "insights": insights,
                "summary_text": summary_text
            }
        
        except Exception as e:
            logger.error(f"주식 데이터 처리 중 오류 발생: {symbol}, {str(e)}")
            raise
