"""
데이터 캐싱 및 업데이트 메커니즘 모듈
"""
import sys
import os
import json
import logging
import pickle
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import threading
import time
import schedule

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCache:
    """
    주식 시장 데이터 캐싱 및 업데이트 메커니즘을 제공하는 클래스
    """
    
    def __init__(self, cache_dir: str = "/tmp/stock_market_cache", use_redis: bool = False, redis_host: str = "localhost", redis_port: int = 6379):
        """
        데이터 캐시 초기화
        
        Args:
            cache_dir: 로컬 캐시 디렉토리 경로
            use_redis: Redis 캐시 사용 여부
            redis_host: Redis 호스트
            redis_port: Redis 포트
        """
        self.cache_dir = cache_dir
        self.use_redis = use_redis
        self.redis_client = None
        
        # 로컬 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        # Redis 연결 설정 (사용하는 경우)
        if use_redis:
            try:
                self.redis_client = redis.Redis(host=redis_host, port=redis_port)
                self.redis_client.ping()  # 연결 테스트
                logger.info(f"Redis 캐시 서버에 연결되었습니다: {redis_host}:{redis_port}")
            except Exception as e:
                logger.warning(f"Redis 연결 실패, 로컬 캐시만 사용합니다: {str(e)}")
                self.use_redis = False
        
        logger.info("데이터 캐시가 초기화되었습니다.")
    
    def get_cache_key(self, data_type: str, identifier: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        캐시 키를 생성합니다.
        
        Args:
            data_type: 데이터 유형 (예: 'korean_market', 'us_market', 'stock')
            identifier: 데이터 식별자 (예: 'all', 'AAPL', 'KOSPI')
            params: 추가 매개변수 (예: {'interval': '1d', 'range': '1mo'})
            
        Returns:
            캐시 키
        """
        key_parts = [data_type, identifier]
        
        if params:
            # 매개변수를 정렬하여 일관된 키 생성
            param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
            key_parts.append(param_str)
        
        return ":".join(key_parts)
    
    def get_cache_path(self, cache_key: str) -> str:
        """
        캐시 키에 해당하는 로컬 파일 경로를 반환합니다.
        
        Args:
            cache_key: 캐시 키
            
        Returns:
            로컬 캐시 파일 경로
        """
        # 파일 시스템에 안전한 이름으로 변환
        safe_key = cache_key.replace(":", "_").replace("/", "_")
        return os.path.join(self.cache_dir, f"{safe_key}.pickle")
    
    def get(self, data_type: str, identifier: str, params: Optional[Dict[str, Any]] = None, max_age: Optional[int] = None) -> Optional[Any]:
        """
        캐시에서 데이터를 가져옵니다.
        
        Args:
            data_type: 데이터 유형
            identifier: 데이터 식별자
            params: 추가 매개변수
            max_age: 최대 캐시 유효 기간 (초)
            
        Returns:
            캐시된 데이터 또는 None (캐시 미스)
        """
        cache_key = self.get_cache_key(data_type, identifier, params)
        
        # Redis 캐시 확인 (사용하는 경우)
        if self.use_redis and self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    # 타임스탬프와 데이터 언패킹
                    timestamp, data = pickle.loads(cached_data)
                    
                    # 캐시 유효성 검사
                    if max_age is None or (datetime.now() - timestamp).total_seconds() < max_age:
                        logger.info(f"Redis 캐시 히트: {cache_key}")
                        return data
                    else:
                        logger.info(f"Redis 캐시 만료: {cache_key}")
            except Exception as e:
                logger.warning(f"Redis 캐시 조회 중 오류 발생: {str(e)}")
        
        # 로컬 파일 캐시 확인
        cache_path = self.get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    # 타임스탬프와 데이터 언패킹
                    timestamp, data = pickle.load(f)
                    
                    # 캐시 유효성 검사
                    if max_age is None or (datetime.now() - timestamp).total_seconds() < max_age:
                        logger.info(f"로컬 캐시 히트: {cache_key}")
                        return data
                    else:
                        logger.info(f"로컬 캐시 만료: {cache_key}")
            except Exception as e:
                logger.warning(f"로컬 캐시 파일 읽기 중 오류 발생: {str(e)}")
        
        logger.info(f"캐시 미스: {cache_key}")
        return None
    
    def set(self, data_type: str, identifier: str, data: Any, params: Optional[Dict[str, Any]] = None, ttl: Optional[int] = None) -> bool:
        """
        데이터를 캐시에 저장합니다.
        
        Args:
            data_type: 데이터 유형
            identifier: 데이터 식별자
            data: 저장할 데이터
            params: 추가 매개변수
            ttl: Redis 캐시 TTL (초)
            
        Returns:
            성공 여부
        """
        cache_key = self.get_cache_key(data_type, identifier, params)
        
        # 타임스탬프와 함께 데이터 패킹
        packed_data = pickle.dumps((datetime.now(), data))
        
        success = True
        
        # Redis 캐시에 저장 (사용하는 경우)
        if self.use_redis and self.redis_client:
            try:
                if ttl:
                    self.redis_client.setex(cache_key, ttl, packed_data)
                else:
                    self.redis_client.set(cache_key, packed_data)
                logger.info(f"Redis 캐시에 저장됨: {cache_key}")
            except Exception as e:
                logger.warning(f"Redis 캐시 저장 중 오류 발생: {str(e)}")
                success = False
        
        # 로컬 파일 캐시에 저장
        cache_path = self.get_cache_path(cache_key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump((datetime.now(), data), f)
            logger.info(f"로컬 캐시에 저장됨: {cache_path}")
        except Exception as e:
            logger.warning(f"로컬 캐시 파일 저장 중 오류 발생: {str(e)}")
            success = False
        
        return success
    
    def invalidate(self, data_type: str, identifier: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        캐시 항목을 무효화합니다.
        
        Args:
            data_type: 데이터 유형
            identifier: 데이터 식별자
            params: 추가 매개변수
            
        Returns:
            성공 여부
        """
        cache_key = self.get_cache_key(data_type, identifier, params)
        
        success = True
        
        # Redis 캐시 항목 삭제 (사용하는 경우)
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete(cache_key)
                logger.info(f"Redis 캐시 항목 삭제됨: {cache_key}")
            except Exception as e:
                logger.warning(f"Redis 캐시 항목 삭제 중 오류 발생: {str(e)}")
                success = False
        
        # 로컬 파일 캐시 항목 삭제
        cache_path = self.get_cache_path(cache_key)
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                logger.info(f"로컬 캐시 파일 삭제됨: {cache_path}")
            except Exception as e:
                logger.warning(f"로컬 캐시 파일 삭제 중 오류 발생: {str(e)}")
                success = False
        
        return success
    
    def clear_all(self) -> bool:
        """
        모든 캐시를 지웁니다.
        
        Returns:
            성공 여부
        """
        success = True
        
        # Redis 캐시 비우기 (사용하는 경우)
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.flushdb()
                logger.info("Redis 캐시가 모두 지워졌습니다.")
            except Exception as e:
                logger.warning(f"Redis 캐시 비우기 중 오류 발생: {str(e)}")
                success = False
        
        # 로컬 파일 캐시 비우기
        try:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path) and filename.endswith('.pickle'):
                    os.remove(file_path)
            logger.info("로컬 캐시 파일이 모두 지워졌습니다.")
        except Exception as e:
            logger.warning(f"로컬 캐시 파일 비우기 중 오류 발생: {str(e)}")
            success = False
        
        return success


class DataUpdateScheduler:
    """
    주식 시장 데이터 업데이트 스케줄러
    """
    
    def __init__(self, korean_market_fetcher, us_market_fetcher, data_processor, data_cache):
        """
        데이터 업데이트 스케줄러 초기화
        
        Args:
            korean_market_fetcher: 한국 시장 데이터 수집기
            us_market_fetcher: 미국 시장 데이터 수집기
            data_processor: 데이터 처리기
            data_cache: 데이터 캐시
        """
        self.korean_market_fetcher = korean_market_fetcher
        self.us_market_fetcher = us_market_fetcher
        self.data_processor = data_processor
        self.data_cache = data_cache
        self.scheduler_thread = None
        self.running = False
        
        logger.info("데이터 업데이트 스케줄러가 초기화되었습니다.")
    
    def update_korean_market_data(self):
        """
        한국 시장 데이터를 업데이트합니다.
        """
        try:
            logger.info("한국 시장 데이터 업데이트 작업 시작...")
            
            # 데이터 수집
            market_data = self.korean_market_fetcher.fetch_all_market_data(interval="1d", range_period="1mo")
            
            # 데이터 처리
            processed_data = self.data_processor.process_market_data(market_data)
            
            # 캐시에 저장
            self.data_cache.set("korean_market", "all", processed_data, ttl=86400)  # 24시간 TTL
            
            logger.info("한국 시장 데이터 업데이트 작업 완료")
        except Exception as e:
            logger.error(f"한국 시장 데이터 업데이트 중 오류 발생: {str(e)}")
    
    def update_us_market_data(self):
        """
        미국 시장 데이터를 업데이트합니다.
        """
        try:
            logger.info("미국 시장 데이터 업데이트 작업 시작...")
            
            # 데이터 수집
            market_data = self.us_market_fetcher.fetch_all_market_data(interval="1d", range_period="1mo")
            
            # 데이터 처리
            processed_data = self.data_processor.process_market_data(market_data)
            
            # 캐시에 저장
            self.data_cache.set("us_market", "all", processed_data, ttl=86400)  # 24시간 TTL
            
            logger.info("미국 시장 데이터 업데이트 작업 완료")
        except Exception as e:
            logger.error(f"미국 시장 데이터 업데이트 중 오류 발생: {str(e)}")
    
    def update_all_market_data(self):
        """
        모든 시장 데이터를 업데이트합니다.
        """
        self.update_korean_market_data()
        self.update_us_market_data()
    
    def _scheduler_loop(self):
        """
        스케줄러 루프
        """
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start(self):
        """
        스케줄러를 시작합니다.
        """
        if self.running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return
        
        self.running = True
        
        # 스케줄 설정
        
        # 한국 시장 데이터 업데이트 (한국 시간 오전 9시, 오후 3시 30분)
        schedule.every().day.at("00:00").do(self.update_korean_market_data)  # UTC 00:00 = KST 09:00
        schedule.every().day.at("06:30").do(self.update_korean_market_data)  # UTC 06:30 = KST 15:30
        
        # 미국 시장 데이터 업데이트 (미국 동부 시간 오전 9시 30분, 오후 4시)
        schedule.every().day.at("13:30").do(self.update_us_market_data)  # UTC 13:30 = EST 09:30
        schedule.every().day.at("20:00").do(self.update_us_market_data)  # UTC 20:00 = EST 16:00
        
        # 초기 데이터 로드
        self.update_all_market_data()
        
        # 스케줄러 스레드 시작
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("데이터 업데이트 스케줄러가 시작되었습니다.")
    
    def stop(self):
        """
        스케줄러를 중지합니다.
        """
        if not self.running:
            logger.warning("스케줄러가 실행 중이 아닙니다.")
            return
        
        self.running = False
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # 모든 스케줄 제거
        schedule.clear()
        
        logger.info("데이터 업데이트 스케줄러가 중지되었습니다.")
