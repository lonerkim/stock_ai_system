"""
투자 성과 추적 및 분석 모듈

이 모듈은 모의 투자의 성과를 추적하고 분석하는 기능을 제공합니다.
투자 결과를 저장하고, 시각화하며, 보고서를 생성합니다.
"""
import os
import logging
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import csv
from io import StringIO

from .mock_investment import Portfolio, MockInvestmentManager, InvestmentAnalyzer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceTracker:
    """
    투자 성과 추적기
    """
    
    def __init__(
        self, 
        investment_manager: MockInvestmentManager,
        data_dir: str = "/tmp/stock_market_ai/performance"
    ):
        """
        투자 성과 추적기 초기화
        
        Args:
            investment_manager: 모의 투자 관리자
            data_dir: 데이터 저장 디렉토리
        """
        self.investment_manager = investment_manager
        self.data_dir = data_dir
        self.analyzer = InvestmentAnalyzer(investment_manager.portfolio)
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "charts"), exist_ok=True)
        
        logger.info(f"투자 성과 추적기가 초기화되었습니다. 데이터 디렉토리: {data_dir}")
    
    def track_daily_performance(self) -> Dict[str, Any]:
        """
        일일 투자 성과를 추적합니다.
        
        Returns:
            일일 성과 정보
        """
        try:
            # 포트폴리오 업데이트
            self.investment_manager.update_portfolio()
            
            # 성과 분석
            performance = self.analyzer.analyze_performance()
            
            # 일일 성과 저장
            self._save_daily_performance(performance)
            
            return performance
        
        except Exception as e:
            logger.error(f"일일 성과 추적 중 오류 발생: {str(e)}")
            raise
    
    def generate_performance_report(self, report_type: str = "daily") -> Dict[str, Any]:
        """
        투자 성과 보고서를 생성합니다.
        
        Args:
            report_type: 보고서 유형 ('daily', 'weekly', 'monthly')
            
        Returns:
            성과 보고서
        """
        try:
            # 보고서 생성
            report = self.analyzer.generate_report()
            
            # 보고서 저장
            self._save_performance_report(report, report_type)
            
            return report
        
        except Exception as e:
            logger.error(f"성과 보고서 생성 중 오류 발생: {str(e)}")
            raise
    
    def generate_performance_charts(self) -> Dict[str, str]:
        """
        투자 성과 차트를 생성합니다.
        
        Returns:
            생성된 차트 파일 경로
        """
        try:
            # 차트 데이터 가져오기
            chart_data = self.analyzer.generate_chart_data()
            
            # 차트 생성 및 저장
            chart_files = self._create_and_save_charts(chart_data)
            
            return chart_files
        
        except Exception as e:
            logger.error(f"성과 차트 생성 중 오류 발생: {str(e)}")
            raise
    
    def export_performance_data(self, format: str = "json") -> str:
        """
        투자 성과 데이터를 내보냅니다.
        
        Args:
            format: 내보내기 형식 ('json', 'csv')
            
        Returns:
            내보내기 파일 경로
        """
        try:
            # 포트폴리오 가치 내역
            portfolio_history = self.investment_manager.portfolio.get_portfolio_history()
            
            # 파일 경로 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == "json":
                file_path = os.path.join(self.data_dir, f"performance_data_{timestamp}.json")
                
                # JSON 형식으로 저장
                with open(file_path, "w") as f:
                    json.dump(portfolio_history, f, indent=2)
            
            elif format == "csv":
                file_path = os.path.join(self.data_dir, f"performance_data_{timestamp}.csv")
                
                # CSV 형식으로 변환
                df = pd.DataFrame(portfolio_history)
                
                # CSV 파일로 저장
                df.to_csv(file_path, index=False)
            
            else:
                raise ValueError(f"지원되지 않는 내보내기 형식: {format}")
            
            logger.info(f"성과 데이터가 내보내기되었습니다: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"성과 데이터 내보내기 중 오류 발생: {str(e)}")
            raise
    
    def _save_daily_performance(self, performance: Dict[str, Any]):
        """
        일일 투자 성과를 저장합니다.
        
        Args:
            performance: 성과 정보
        """
        try:
            # 파일 경로 생성
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = os.path.join(self.data_dir, f"daily_performance_{date_str}.json")
            
            # 성과 정보 저장
            with open(file_path, "w") as f:
                json.dump(performance, f, indent=2)
            
            logger.info(f"일일 성과가 저장되었습니다: {file_path}")
        
        except Exception as e:
            logger.error(f"일일 성과 저장 중 오류 발생: {str(e)}")
    
    def _save_performance_report(self, report: Dict[str, Any], report_type: str):
        """
        투자 성과 보고서를 저장합니다.
        
        Args:
            report: 성과 보고서
            report_type: 보고서 유형 ('daily', 'weekly', 'monthly')
        """
        try:
            # 파일 경로 생성
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = os.path.join(self.data_dir, "reports", f"{report_type}_report_{date_str}.json")
            
            # 보고서 저장
            with open(file_path, "w") as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"성과 보고서가 저장되었습니다: {file_path}")
        
        except Exception as e:
            logger.error(f"성과 보고서 저장 중 오류 발생: {str(e)}")
    
    def _create_and_save_charts(self, chart_data: Dict[str, Any]) -> Dict[str, str]:
        """
        투자 성과 차트를 생성하고 저장합니다.
        
        Args:
            chart_data: 차트 데이터
            
        Returns:
            생성된 차트 파일 경로
        """
        try:
            # 날짜 문자열 생성
            date_str = datetime.now().strftime("%Y%m%d")
            
            # 차트 파일 경로
            chart_files = {}
            
            # 포트폴리오 가치 차트
            portfolio_value_chart_path = os.path.join(self.data_dir, "charts", f"portfolio_value_{date_str}.png")
            self._create_portfolio_value_chart(chart_data, portfolio_value_chart_path)
            chart_files["portfolio_value"] = portfolio_value_chart_path
            
            # 수익률 차트
            roi_chart_path = os.path.join(self.data_dir, "charts", f"roi_{date_str}.png")
            self._create_roi_chart(chart_data, roi_chart_path)
            chart_files["roi"] = roi_chart_path
            
            # 자산 배분 차트
            allocation_chart_path = os.path.join(self.data_dir, "charts", f"allocation_{date_str}.png")
            self._create_allocation_chart(chart_data, allocation_chart_path)
            chart_files["allocation"] = allocation_chart_path
            
            logger.info(f"성과 차트가 생성되었습니다: {chart_files}")
            return chart_files
        
        except Exception as e:
            logger.error(f"차트 생성 및 저장 중 오류 발생: {str(e)}")
            raise
    
    def _create_portfolio_value_chart(self, chart_data: Dict[str, Any], file_path: str):
        """
        포트폴리오 가치 차트를 생성합니다.
        
        Args:
            chart_data: 차트 데이터
            file_path: 저장할 파일 경로
        """
        try:
            # 타임스탬프를 datetime으로 변환
            timestamps = [datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in chart_data["timestamps"]]
            
            # 차트 생성
            plt.figure(figsize=(12, 6))
            plt.plot(timestamps, chart_data["total_values"], label="총 가치", color="blue")
            plt.plot(timestamps, chart_data["cash_values"], label="현금", color="green")
            plt.plot(timestamps, chart_data["positions_values"], label="포지션 가치", color="orange")
            
            plt.title("포트폴리오 가치 변화")
            plt.xlabel("날짜")
            plt.ylabel("가치 ($)")
            plt.legend()
            plt.grid(True)
            
            # 차트 저장
            plt.savefig(file_path)
            plt.close()
        
        except Exception as e:
            logger.error(f"포트폴리오 가치 차트 생성 중 오류 발생: {str(e)}")
    
    def _create_roi_chart(self, chart_data: Dict[str, Any], file_path: str):
        """
        수익률 차트를 생성합니다.
        
        Args:
            chart_data: 차트 데이터
            file_path: 저장할 파일 경로
        """
        try:
            # 타임스탬프를 datetime으로 변환
            timestamps = [datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in chart_data["timestamps"]]
            
            # 차트 생성
            plt.figure(figsize=(12, 6))
            plt.plot(timestamps, chart_data["roi_values"], label="수익률 (%)", color="red")
            
            plt.title("포트폴리오 수익률 변화")
            plt.xlabel("날짜")
            plt.ylabel("수익률 (%)")
            plt.legend()
            plt.grid(True)
            
            # 0% 라인 추가
            plt.axhline(y=0, color="black", linestyle="-", alpha=0.3)
            
            # 차트 저장
            plt.savefig(file_path)
            plt.close()
        
        except Exception as e:
            logger.error(f"수익률 차트 생성 중 오류 발생: {str(e)}")
    
    def _create_allocation_chart(self, chart_data: Dict[str, Any], file_path: str):
        """
        자산 배분 차트를 생성합니다.
        
        Args:
            chart_data: 차트 데이터
            file_path: 저장할 파일 경로
        """
        try:
            # 최신 데이터 가져오기
            latest_cash = chart_data["cash_values"][-1]
            latest_positions = chart_data["positions_values"][-1]
            
            # 데이터가 0이 아닌 경우에만 차트 생성
            if latest_cash > 0 or latest_positions > 0:
                # 차트 데이터 생성
                labels = ["현금", "포지션"]
                sizes = [latest_cash, latest_positions]
                colors = ["green", "orange"]
                
                # 차트 생성
                plt.figure(figsize=(8, 8))
                plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
                plt.axis("equal")
                plt.title("자산 배분")
                
                # 차트 저장
                plt.savefig(file_path)
                plt.close()
            else:
                logger.warning("자산 배분 차트 생성 실패: 데이터가 없습니다.")
        
        except Exception as e:
            logger.error(f"자산 배분 차트 생성 중 오류 발생: {str(e)}")


class PerformanceAnalysisService:
    """
    투자 성과 분석 서비스
    """
    
    def __init__(
        self, 
        tracker: PerformanceTracker,
        data_dir: str = "/tmp/stock_market_ai/analysis"
    ):
        """
        투자 성과 분석 서비스 초기화
        
        Args:
            tracker: 투자 성과 추적기
            data_dir: 데이터 저장 디렉토리
        """
        self.tracker = tracker
        self.data_dir = data_dir
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info(f"투자 성과 분석 서비스가 초기화되었습니다. 데이터 디렉토리: {data_dir}")
    
    def analyze_daily_performance(self) -> Dict[str, Any]:
        """
        일일 투자 성과를 분석합니다.
        
        Returns:
            분석 결과
        """
        try:
            # 일일 성과 추적
            performance = self.tracker.track_daily_performance()
            
            # 일일 보고서 생성
            report = self.tracker.generate_performance_report(report_type="daily")
            
            # 차트 생성
            charts = self.tracker.generate_performance_charts()
            
            # 분석 결과 생성
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "performance": performance,
                "report": report,
                "charts": charts
            }
            
            # 분석 결과 저장
            self._save_analysis_result(analysis, "daily")
            
            return analysis
        
        except Exception as e:
            logger.error(f"일일 성과 분석 중 오류 발생: {str(e)}")
            raise
    
    def analyze_weekly_performance(self) -> Dict[str, Any]:
        """
        주간 투자 성과를 분석합니다.
        
        Returns:
            분석 결과
        """
        try:
            # 주간 보고서 생성
            report = self.tracker.generate_performance_report(report_type="weekly")
            
            # 차트 생성
            charts = self.tracker.generate_performance_charts()
            
            # 분석 결과 생성
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "report": report,
                "charts": charts
            }
            
            # 분석 결과 저장
            self._save_analysis_result(analysis, "weekly")
            
            return analysis
        
        except Exception as e:
            logger.error(f"주간 성과 분석 중 오류 발생: {str(e)}")
            raise
    
    def analyze_monthly_performance(self) -> Dict[str, Any]:
        """
        월간 투자 성과를 분석합니다.
        
        Returns:
            분석 결과
        """
        try:
            # 월간 보고서 생성
            report = self.tracker.generate_performance_report(report_type="monthly")
            
            # 차트 생성
            charts = self.tracker.generate_performance_charts()
            
            # 분석 결과 생성
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "report": report,
                "charts": charts
            }
            
            # 분석 결과 저장
            self._save_analysis_result(analysis, "monthly")
            
            return analysis
        
        except Exception as e:
            logger.error(f"월간 성과 분석 중 오류 발생: {str(e)}")
            raise
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        요약 보고서를 생성합니다.
        
        Returns:
            요약 보고서
        """
        try:
            # 포트폴리오 가치 내역
            portfolio_history = self.tracker.investment_manager.portfolio.get_portfolio_history()
            
            # 거래 내역
            transaction_history = self.tracker.investment_manager.portfolio.get_transaction_history()
            
            # 시작 및 현재 가치
            if portfolio_history:
                start_value = portfolio_history[0]["total_value"]
                current_value = portfolio_history[-1]["total_value"]
                total_roi = (current_value - start_value) / start_value * 100
            else:
                start_value = 0.0
                current_value = 0.0
                total_roi = 0.0
            
            # 거래 통계
            if transaction_history:
                total_trades = len(transaction_history)
                buy_trades = sum(1 for t in transaction_history if t["type"] == "buy")
                sell_trades = sum(1 for t in transaction_history if t["type"] == "sell")
            else:
                total_trades = 0
                buy_trades = 0
                sell_trades = 0
            
            # 요약 보고서 생성
            summary = {
                "timestamp": datetime.now().isoformat(),
                "start_date": portfolio_history[0]["timestamp"] if portfolio_history else datetime.now().isoformat(),
                "end_date": datetime.now().isoformat(),
                "start_value": start_value,
                "current_value": current_value,
                "total_roi": total_roi,
                "trade_statistics": {
                    "total_trades": total_trades,
                    "buy_trades": buy_trades,
                    "sell_trades": sell_trades
                }
            }
            
            # 요약 보고서 저장
            self._save_summary_report(summary)
            
            return summary
        
        except Exception as e:
            logger.error(f"요약 보고서 생성 중 오류 발생: {str(e)}")
            raise
    
    def _save_analysis_result(self, analysis: Dict[str, Any], analysis_type: str):
        """
        분석 결과를 저장합니다.
        
        Args:
            analysis: 분석 결과
            analysis_type: 분석 유형 ('daily', 'weekly', 'monthly')
        """
        try:
            # 파일 경로 생성
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = os.path.join(self.data_dir, f"{analysis_type}_analysis_{date_str}.json")
            
            # 분석 결과에서 차트 파일 경로만 저장
            analysis_copy = analysis.copy()
            if "charts" in analysis_copy:
                analysis_copy["charts"] = {k: os.path.basename(v) for k, v in analysis_copy["charts"].items()}
            
            # 분석 결과 저장
            with open(file_path, "w") as f:
                json.dump(analysis_copy, f, indent=2)
            
            logger.info(f"분석 결과가 저장되었습니다: {file_path}")
        
        except Exception as e:
            logger.error(f"분석 결과 저장 중 오류 발생: {str(e)}")
    
    def _save_summary_report(self, summary: Dict[str, Any]):
        """
        요약 보고서를 저장합니다.
        
        Args:
            summary: 요약 보고서
        """
        try:
            # 파일 경로 생성
            date_str = datetime.now().strftime("%Y%m%d")
            file_path = os.path.join(self.data_dir, f"summary_report_{date_str}.json")
            
            # 요약 보고서 저장
            with open(file_path, "w") as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"요약 보고서가 저장되었습니다: {file_path}")
        
        except Exception as e:
            logger.error(f"요약 보고서 저장 중 오류 발생: {str(e)}")
