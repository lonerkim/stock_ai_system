"""
모의 투자 관리자 어댑터 모듈

이 모듈은 기존 MockInvestmentManager 클래스를 main.py에서 사용하는 인터페이스로 변환합니다.
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockInvestmentManager:
    """
    모의 투자 관리자 어댑터 클래스
    """
    
    def __init__(self, neo4j_repo, data_dir: str = "/tmp/stock_market_ai/investments"):
        """
        모의 투자 관리자 어댑터 초기화
        
        Args:
            neo4j_repo: Neo4j 저장소
            data_dir: 데이터 저장 디렉토리
        """
        self.neo4j_repo = neo4j_repo
        self.data_dir = data_dir
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info("모의 투자 관리자 어댑터가 초기화되었습니다.")
    
    def record_investment_decision(self, decision: Dict[str, Any]) -> bool:
        """
        투자 결정을 기록합니다.
        
        Args:
            decision: 투자 결정
            
        Returns:
            기록 성공 여부
        """
        try:
            # 투자 결정 ID 생성
            decision_id = str(uuid.uuid4())
            
            # 타임스탬프 확인
            if "timestamp" not in decision:
                decision["timestamp"] = datetime.now().isoformat()
            
            # Neo4j에 투자 결정 저장
            self.neo4j_repo.save_investment_decision(decision_id, decision)
            
            # 로컬 파일에도 저장
            self._save_to_file(decision)
            
            logger.info(f"투자 결정이 기록되었습니다: {decision_id}")
            return True
        
        except Exception as e:
            logger.error(f"투자 결정 기록 중 오류 발생: {str(e)}")
            return False
    
    def get_investment_decisions(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        투자 결정 목록을 가져옵니다.
        
        Args:
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            투자 결정 목록
        """
        try:
            # 날짜 설정
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            if not start_date:
                start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Neo4j에서 투자 결정 조회
            decisions = self.neo4j_repo.get_investment_decisions(start_date, end_date)
            
            return decisions
        
        except Exception as e:
            logger.error(f"투자 결정 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_latest_investment_decision(self) -> Optional[Dict[str, Any]]:
        """
        최신 투자 결정을 가져옵니다.
        
        Returns:
            최신 투자 결정 또는 None
        """
        try:
            # Neo4j에서 최신 투자 결정 조회
            decision = self.neo4j_repo.get_latest_investment_decision()
            
            return decision
        
        except Exception as e:
            logger.error(f"최신 투자 결정 조회 중 오류 발생: {str(e)}")
            return None
    
    def _save_to_file(self, decision: Dict[str, Any]):
        """
        투자 결정을 파일로 저장합니다.
        
        Args:
            decision: 투자 결정
        """
        try:
            # 파일 경로 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.data_dir, f"decision_{timestamp}.json")
            
            # 투자 결정 저장
            with open(file_path, "w") as f:
                json.dump(decision, f, indent=2)
            
            logger.info(f"투자 결정이 파일로 저장되었습니다: {file_path}")
        
        except Exception as e:
            logger.error(f"투자 결정 파일 저장 중 오류 발생: {str(e)}")


class PerformanceTracker:
    """
    투자 성과 추적기 어댑터 클래스
    """
    
    def __init__(self, neo4j_repo):
        """
        투자 성과 추적기 어댑터 초기화
        
        Args:
            neo4j_repo: Neo4j 저장소
        """
        self.neo4j_repo = neo4j_repo
        
        logger.info("투자 성과 추적기 어댑터가 초기화되었습니다.")
    
    def get_performance(self, period: str = "daily", start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        투자 성과를 가져옵니다.
        
        Args:
            period: 기간 ('daily', 'weekly', 'monthly')
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            투자 성과 정보
        """
        try:
            # 날짜 설정
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            if not start_date:
                if period == "daily":
                    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                elif period == "weekly":
                    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
                elif period == "monthly":
                    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
                else:
                    start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Neo4j에서 투자 결정 조회
            decisions = self.neo4j_repo.get_investment_decisions(start_date, end_date)
            
            # 투자 성과 계산
            performance = self._calculate_performance(decisions, start_date, end_date)
            
            return performance
        
        except Exception as e:
            logger.error(f"투자 성과 조회 중 오류 발생: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "period": period,
                "start_date": start_date,
                "end_date": end_date,
                "decisions": [],
                "summary": {
                    "total_decisions": 0,
                    "total_investments": 0,
                    "average_investment": 0,
                    "cash_reserve": 0
                },
                "error": str(e)
            }
    
    def _calculate_performance(self, decisions: List[Dict[str, Any]], start_date: str, end_date: str) -> Dict[str, Any]:
        """
        투자 성과를 계산합니다.
        
        Args:
            decisions: 투자 결정 목록
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            투자 성과 정보
        """
        try:
            # 투자 결정이 없는 경우
            if not decisions:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "start_date": start_date,
                    "end_date": end_date,
                    "decisions": [],
                    "summary": {
                        "total_decisions": 0,
                        "total_investments": 0,
                        "average_investment": 0,
                        "cash_reserve": 0
                    }
                }
            
            # 투자 결정 분석
            total_investments = 0
            total_cash_reserve = 0
            
            for decision in decisions:
                # 투자 금액 합계
                investments = decision.get("investments", [])
                for investment in investments:
                    total_investments += investment.get("amount", 0)
                
                # 현금 보유액
                total_cash_reserve += decision.get("cash_reserve", 0)
            
            # 평균 투자 금액
            average_investment = total_investments / len(decisions) if decisions else 0
            
            # 평균 현금 보유액
            average_cash_reserve = total_cash_reserve / len(decisions) if decisions else 0
            
            return {
                "timestamp": datetime.now().isoformat(),
                "start_date": start_date,
                "end_date": end_date,
                "decisions": decisions,
                "summary": {
                    "total_decisions": len(decisions),
                    "total_investments": total_investments,
                    "average_investment": average_investment,
                    "cash_reserve": average_cash_reserve
                }
            }
        
        except Exception as e:
            logger.error(f"투자 성과 계산 중 오류 발생: {str(e)}")
            raise
