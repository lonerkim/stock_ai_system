"""
Celery 애플리케이션 설정 모듈

이 모듈은 Celery 애플리케이션을 정의하고 설정합니다.
"""
from celery import Celery
import os

# Redis 연결 설정
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'

# Celery 앱 생성
app = Celery(
    'stock_ai',
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=['app.worker.tasks']
)

# Celery 설정
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_hijack_root_logger=False,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
)

# 주기적 작업 스케줄 설정
app.conf.beat_schedule = {
    'update-stock-data-every-hour': {
        'task': 'app.worker.tasks.update_stock_data',
        'schedule': 3600.0,  # 1시간마다
    },
    'update-portfolio-every-10-minutes': {
        'task': 'app.worker.tasks.update_portfolio',
        'schedule': 600.0,  # 10분마다
    },
    'send-daily-summary': {
        'task': 'app.worker.tasks.send_daily_summary',
        'schedule': 86400.0,  # 24시간마다
        'kwargs': {'hour': 9},  # 오전 9시에 실행
    },
}

if __name__ == '__main__':
    app.start()
