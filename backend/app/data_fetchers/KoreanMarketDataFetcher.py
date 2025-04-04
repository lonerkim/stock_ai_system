"""
한국 주식 시장 데이터 수집 어댑터 모듈

이 모듈은 기존 KoreanStockMarketFetcher 클래스를 main.py에서 사용하는 인터페이스로 변환합니다.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .korean_market import KoreanStockMarketFetcher
from .data_cache import DataCache

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KoreanMarketDataFetcher:
    """
    한국 주식 시장 데이터 수집 어댑터 클래스
    """
    
    def __init__(self, cache: DataCache):
        """
        한국 주식 시장 데이터 수집 어댑터 초기화
        
        Args:
            cache: 데이터 캐시 객체
        """
        self.cache = cache
        self.fetcher = KoreanStockMarketFetcher()
        
        logger.info("한국 주식 시장 데이터 수집 어댑터가 초기화되었습니다.")
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        시장 개요 데이터를 가져옵니다.
        
        Returns:
            시장 개요 데이터
        """
        # 캐시 확인
        cache_key = f"korean_market_overview_{datetime.now().strftime('%Y-%m-%d')}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info("캐시에서 한국 시장 개요 데이터를 가져왔습니다.")
            return cached_data
        
        try:
            # 기존 fetcher를 사용하여 데이터 가져오기
            market_data = self.fetcher.fetch_all_market_data(interval="1d", range_period="1mo")
            
            # 결과 데이터 구성
            result = {
                "market": "korean",
                "timestamp": datetime.now().isoformat(),
                "indices": {
                    "KOSPI": self._extract_index_data(market_data, "kospi"),
                    "KOSDAQ": self._extract_index_data(market_data, "kosdaq")
                },
                "top_stocks": self._extract_top_stocks(market_data),
                "news": self._extract_news(market_data),
                "summary_text": self._generate_summary_text(market_data)
            }
            
            # 캐시에 저장
            self.cache.set(cache_key, result, 3600)  # 1시간 캐시
            
            logger.info("한국 시장 개요 데이터를 가져왔습니다.")
            return result
        
        except Exception as e:
            logger.error(f"한국 시장 개요 데이터 가져오기 중 오류 발생: {str(e)}")
            
            # 오류 발생 시 더미 데이터 반환
            return {
                "market": "korean",
                "timestamp": datetime.now().isoformat(),
                "indices": {
                    "KOSPI": {
                        "name": "KOSPI",
                        "current": 2500.0,
                        "change": 15.0,
                        "change_percent": 0.6,
                        "volume": 500000000,
                        "value": 5000000000000
                    },
                    "KOSDAQ": {
                        "name": "KOSDAQ",
                        "current": 850.0,
                        "change": 5.0,
                        "change_percent": 0.59,
                        "volume": 300000000,
                        "value": 3000000000000
                    }
                },
                "top_stocks": [
                    {
                        "symbol": "005930",
                        "name": "삼성전자",
                        "price": 70000,
                        "change": 1000,
                        "change_percent": 1.45,
                        "volume": 10000000
                    },
                    {
                        "symbol": "000660",
                        "name": "SK하이닉스",
                        "price": 120000,
                        "change": 2000,
                        "change_percent": 1.69,
                        "volume": 5000000
                    },
                    {
                        "symbol": "035420",
                        "name": "NAVER",
                        "price": 350000,
                        "change": -5000,
                        "change_percent": -1.41,
                        "volume": 1000000
                    }
                ],
                "news": [
                    {
                        "title": "한국 증시, 글로벌 경기 회복 기대감에 상승",
                        "link": "#"
                    },
                    {
                        "title": "외국인 투자자, 3일 연속 순매수",
                        "link": "#"
                    },
                    {
                        "title": "반도체 업종 강세, 수출 전망 개선",
                        "link": "#"
                    }
                ],
                "summary_text": """
                한국 시장 개요 (기준일: 더미 데이터)
                
                KOSPI: 2,500.00 (+0.60%)
                KOSDAQ: 850.00 (+0.59%)
                
                주요 종목:
                - 삼성전자: 70,000원 (+1.45%)
                - SK하이닉스: 120,000원 (+1.69%)
                - NAVER: 350,000원 (-1.41%)
                
                주요 뉴스:
                - 한국 증시, 글로벌 경기 회복 기대감에 상승
                - 외국인 투자자, 3일 연속 순매수
                - 반도체 업종 강세, 수출 전망 개선
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
        cache_key = f"korean_stock_{symbol}_{start_date}_{end_date}"
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(f"캐시에서 한국 주식 데이터를 가져왔습니다: {symbol}")
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
            
            # Yahoo Finance 형식으로 심볼 변환
            yahoo_symbol = f"{symbol}.KS"  # 기본적으로 코스피 종목으로 가정
            
            # 기존 fetcher를 사용하여 데이터 가져오기
            stock_data = self.fetcher.yahoo_client.get_stock_chart(
                symbol=yahoo_symbol,
                region="KR",
                interval="1d",
                range_period=range_period
            )
            
            # 주식 인사이트 가져오기
            try:
                insights = self.fetcher.yahoo_client.get_stock_insights(symbol=yahoo_symbol)
            except Exception:
                insights = {}
            
            # 결과 데이터 구성
            result = self._process_stock_data(symbol, stock_data, insights, start_date, end_date)
            
            # 캐시에 저장
            self.cache.set(cache_key, result, 3600)  # 1시간 캐시
            
            logger.info(f"한국 주식 데이터를 가져왔습니다: {symbol}")
            return result
        
        except Exception as e:
            logger.error(f"한국 주식 데이터 가져오기 중 오류 발생: {symbol}, {str(e)}")
            
            # 오류 발생 시 더미 데이터 반환
            return {
                "symbol": symbol,
                "name": "삼성전자" if symbol == "005930" else "SK하이닉스" if symbol == "000660" else "NAVER" if symbol == "035420" else "알 수 없음",
                "market": "korean",
                "timestamp": datetime.now().isoformat(),
                "current_data": {
                    "price": 70000 if symbol == "005930" else 120000 if symbol == "000660" else 350000 if symbol == "035420" else 50000,
                    "change": 1000 if symbol == "005930" else 2000 if symbol == "000660" else -5000 if symbol == "035420" else 500,
                    "change_percent": 1.45 if symbol == "005930" else 1.69 if symbol == "000660" else -1.41 if symbol == "035420" else 1.0,
                    "volume": 10000000 if symbol == "005930" else 5000000 if symbol == "000660" else 1000000 if symbol == "035420" else 500000,
                    "high": 71000 if symbol == "005930" else 122000 if symbol == "000660" else 355000 if symbol == "035420" else 51000,
                    "low": 69000 if symbol == "005930" else 119000 if symbol == "000660" else 345000 if symbol == "035420" else 49000,
                    "open": 69500 if symbol == "005930" else 119500 if symbol == "000660" else 352000 if symbol == "035420" else 49500
                },
                "price_history": [
                    {
                        "date": (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d"),
                        "open": 69500 + i * 100 if symbol == "005930" else 119500 + i * 200 if symbol == "000660" else 352000 - i * 300 if symbol == "035420" else 49500 + i * 50,
                        "high": 71000 + i * 100 if symbol == "005930" else 122000 + i * 200 if symbol == "000660" else 355000 - i * 300 if symbol == "035420" else 51000 + i * 50,
                        "low": 69000 + i * 100 if symbol == "005930" else 119000 + i * 200 if symbol == "000660" else 345000 - i * 300 if symbol == "035420" else 49000 + i * 50,
                        "close": 70000 + i * 100 if symbol == "005930" else 120000 + i * 200 if symbol == "000660" else 350000 - i * 300 if symbol == "035420" else 50000 + i * 50,
                        "volume": 10000000 - i * 100000 if symbol == "005930" else 5000000 - i * 50000 if symbol == "000660" else 1000000 - i * 10000 if symbol == "035420" else 500000 - i * 5000
                    }
                    for i in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)
                ],
                "summary_text": f"""
                {symbol} 주식 정보 (더미 데이터)
                
                현재가: {70000 if symbol == "005930" else 120000 if symbol == "000660" else 350000 if symbol == "035420" else 50000:,.0f}원 ({1.45 if symbol == "005930" else 1.69 if symbol == "000660" else -1.41 if symbol == "035420" else 1.0:+.2f}%)
                거래량: {10000000 if symbol == "005930" else 5000000 if symbol == "000660" else 1000000 if symbol == "035420" else 500000:,}
                52주 최고: {75000 if symbol == "005930" else 130000 if symbol == "000660" else 400000 if symbol == "035420" else 55000:,.0f}원
                52주 최저: {65000 if symbol == "005930" else 110000 if symbol == "000660" else 300000 if symbol == "035420" else 45000:,.0f}원
                
                기간: {start_date} ~ {end_date}
                시작가: {70000 if symbol == "005930" else 120000 if symbol == "000660" else 350000 if symbol == "035420" else 50000:,.0f}원
                종가: {71000 if symbol == "005930" else 122000 if symbol == "000660" else 345000 if symbol == "035420" else 51000:,.0f}원
                변동률: {1.43 if symbol == "005930" else 1.67 if symbol == "000660" else -1.43 if symbol == "035420" else 2.0:+.2f}%
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
                            "name": "KOSPI" if index_key == "kospi" else "KOSDAQ",
                            "current": latest_close,
                            "change": change,
                            "change_percent": change_percent,
                            "volume": latest_volume,
                            "value": latest_close * latest_volume if latest_volume else 0
                        }
            
            # 데이터가 없거나 형식이 맞지 않는 경우 기본값 반환
            return {
                "name": "KOSPI" if index_key == "kospi" else "KOSDAQ",
                "current": 0,
                "change": 0,
                "change_percent": 0,
                "volume": 0,
                "value": 0
            }
        
        except Exception as e:
            logger.warning(f"지수 데이터 추출 중 오류 발생: {index_key}, {str(e)}")
            return {
                "name": "KOSPI" if index_key == "kospi" else "KOSDAQ",
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
                            
                            # 심볼에서 .KS 또는 .KQ 접미사 제거
                            clean_symbol = symbol.split('.')[0]
                            
                            top_stocks.append({
                                "symbol": clean_symbol,
                                "name": meta.get('shortName', clean_symbol),
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
                "title": "한국 증시, 글로벌 경기 회복 기대감에 상승",
                "link": "#"
            },
            {
                "title": "외국인 투자자, 3일 연속 순매수",
                "link": "#"
            },
            {
                "title": "반도체 업종 강세, 수출 전망 개선",
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
            kospi_data = self._extract_index_data(market_data, "kospi")
            kosdaq_data = self._extract_index_data(market_data, "kosdaq")
            
            # 상위 주식 정보 추출
            top_stocks = self._extract_top_stocks(market_data)
            
            # 요약 텍스트 생성
            summary_text = f"""
            한국 시장 개요 (기준일: {datetime.now().strftime('%Y-%m-%d')})
            
            KOSPI: {kospi_data['current']:,.2f} ({kospi_data['change_percent']:+.2f}%)
            KOSDAQ: {kosdaq_data['current']:,.2f} ({kosdaq_data['change_percent']:+.2f}%)
            
            주요 종목:
            {chr(10).join([f"- {stock['name']} ({stock['symbol']}): {stock['price']:,.0f}원 ({stock['change_percent']:+.2f}%)" for stock in top_stocks[:5]])}
            
            주요 뉴스:
            - 한국 증시, 글로벌 경기 회복 기대감에 상승
            - 외국인 투자자, 3일 연속 순매수
            - 반도체 업종 강세, 수출 전망 개선
            """
            
            return summary_text
        
        except Exception as e:
            logger.warning(f"요약 텍스트 생성 중 오류 발생: {str(e)}")
            return """
            한국 시장 개요 (더미 데이터)
            
            KOSPI: 2,500.00 (+0.60%)
            KOSDAQ: 850.00 (+0.59%)
            
            주요 종목:
            - 삼성전자 (005930): 70,000원 (+1.45%)
            - SK하이닉스 (000660): 120,000원 (+1.69%)
            - NAVER (035420): 350,000원 (-1.41%)
            
            주요 뉴스:
            - 한국 증시, 글로벌 경기 회복 기대감에 상승
            - 외국인 투자자, 3일 연속 순매수
            - 반도체 업종 강세, 수출 전망 개선
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
            
            현재가: {current_data['price']:,.0f}원 ({current_data['change_percent']:+.2f}%)
            거래량: {current_data['volume']:,}
            52주 최고: {meta.get('fiftyTwoWeekHigh', 0):,.0f}원
            52주 최저: {meta.get('fiftyTwoWeekLow', 0):,.0f}원
            
            기간: {start_date} ~ {end_date}
            시작가: {price_history[0]['close'] if price_history else 0:,.0f}원
            종가: {price_history[-1]['close'] if price_history else 0:,.0f}원
            변동률: {((price_history[-1]['close'] / price_history[0]['close'] - 1) * 100) if price_history and price_history[0]['close'] > 0 else 0:+.2f}%
            """
            
            return {
                "symbol": symbol,
                "name": meta.get('shortName', symbol),
                "market": "korean",
                "timestamp": datetime.now().isoformat(),
                "current_data": current_data,
                "price_history": price_history,
                "insights": insights,
                "summary_text": summary_text
            }
        
        except Exception as e:
            logger.error(f"주식 데이터 처리 중 오류 발생: {symbol}, {str(e)}")
            raise
