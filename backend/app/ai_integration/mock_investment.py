"""
모의 투자 로직 모듈

이 모듈은 AI 기반 모의 투자 로직을 구현합니다.
AI 분석 결과를 바탕으로 투자 결정을 내리고, 투자 성과를 추적합니다.
"""
import os
import logging
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime, timedelta
import uuid

from ..data_fetchers.yahoo_finance import YahooFinanceAPI
from .ai_provider import BaseAIProvider

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Portfolio:
    """
    투자 포트폴리오 관리 클래스
    """
    
    def __init__(self, initial_cash: float = 100.0):
        """
        포트폴리오 초기화
        
        Args:
            initial_cash: 초기 현금
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}  # 심볼 -> 수량, 평균 매수가
        self.transactions = []  # 거래 내역
        self.history = []  # 포트폴리오 가치 변화 내역
        
        # 초기 포트폴리오 가치 기록
        self._record_portfolio_value()
        
        logger.info(f"포트폴리오가 초기화되었습니다. 초기 현금: ${initial_cash:.2f}")
    
    def buy(self, symbol: str, quantity: float, price: float, timestamp: str = None, reason: str = None) -> bool:
        """
        주식을 매수합니다.
        
        Args:
            symbol: 주식 심볼
            quantity: 매수 수량
            price: 매수 가격
            timestamp: 거래 시간 (없으면 현재 시간)
            reason: 매수 이유
            
        Returns:
            매수 성공 여부
        """
        try:
            # 매수 금액 계산
            amount = quantity * price
            
            # 현금 확인
            if amount > self.cash:
                logger.warning(f"매수 실패: 현금 부족 (필요: ${amount:.2f}, 보유: ${self.cash:.2f})")
                return False
            
            # 현금 차감
            self.cash -= amount
            
            # 포지션 업데이트
            if symbol in self.positions:
                # 기존 포지션 업데이트
                current_quantity = self.positions[symbol]["quantity"]
                current_avg_price = self.positions[symbol]["avg_price"]
                
                # 평균 매수가 계산
                new_quantity = current_quantity + quantity
                new_avg_price = (current_quantity * current_avg_price + quantity * price) / new_quantity
                
                self.positions[symbol] = {
                    "quantity": new_quantity,
                    "avg_price": new_avg_price
                }
            else:
                # 새 포지션 생성
                self.positions[symbol] = {
                    "quantity": quantity,
                    "avg_price": price
                }
            
            # 거래 내역 기록
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            transaction = {
                "id": str(uuid.uuid4()),
                "type": "buy",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "amount": amount,
                "timestamp": timestamp,
                "reason": reason
            }
            
            self.transactions.append(transaction)
            
            # 포트폴리오 가치 기록
            self._record_portfolio_value()
            
            logger.info(f"매수 성공: {symbol} {quantity}주 @ ${price:.2f} (총 ${amount:.2f})")
            return True
        
        except Exception as e:
            logger.error(f"매수 중 오류 발생: {str(e)}")
            return False
    
    def sell(self, symbol: str, quantity: float, price: float, timestamp: str = None, reason: str = None) -> bool:
        """
        주식을 매도합니다.
        
        Args:
            symbol: 주식 심볼
            quantity: 매도 수량
            price: 매도 가격
            timestamp: 거래 시간 (없으면 현재 시간)
            reason: 매도 이유
            
        Returns:
            매도 성공 여부
        """
        try:
            # 포지션 확인
            if symbol not in self.positions:
                logger.warning(f"매도 실패: 포지션 없음 ({symbol})")
                return False
            
            current_quantity = self.positions[symbol]["quantity"]
            
            # 수량 확인
            if quantity > current_quantity:
                logger.warning(f"매도 실패: 수량 부족 (요청: {quantity}, 보유: {current_quantity})")
                return False
            
            # 매도 금액 계산
            amount = quantity * price
            
            # 현금 증가
            self.cash += amount
            
            # 포지션 업데이트
            new_quantity = current_quantity - quantity
            
            if new_quantity > 0:
                # 일부 매도
                self.positions[symbol]["quantity"] = new_quantity
            else:
                # 전체 매도
                del self.positions[symbol]
            
            # 거래 내역 기록
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            transaction = {
                "id": str(uuid.uuid4()),
                "type": "sell",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "amount": amount,
                "timestamp": timestamp,
                "reason": reason
            }
            
            self.transactions.append(transaction)
            
            # 포트폴리오 가치 기록
            self._record_portfolio_value()
            
            logger.info(f"매도 성공: {symbol} {quantity}주 @ ${price:.2f} (총 ${amount:.2f})")
            return True
        
        except Exception as e:
            logger.error(f"매도 중 오류 발생: {str(e)}")
            return False
    
    def _record_portfolio_value(self, timestamp: str = None, prices: Dict[str, float] = None):
        """
        포트폴리오 가치를 기록합니다.
        
        Args:
            timestamp: 기록 시간 (없으면 현재 시간)
            prices: 주식 가격 정보 (없으면 마지막 거래 가격 사용)
        """
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            # 포지션 가치 계산
            positions_value = 0.0
            
            for symbol, position in self.positions.items():
                quantity = position["quantity"]
                
                # 가격 결정
                if prices is not None and symbol in prices:
                    price = prices[symbol]
                else:
                    price = position["avg_price"]
                
                # 포지션 가치 계산
                position_value = quantity * price
                positions_value += position_value
            
            # 총 포트폴리오 가치 계산
            total_value = self.cash + positions_value
            
            # 수익률 계산
            roi = (total_value - self.initial_cash) / self.initial_cash * 100
            
            # 포트폴리오 가치 기록
            portfolio_value = {
                "timestamp": timestamp,
                "cash": self.cash,
                "positions_value": positions_value,
                "total_value": total_value,
                "roi": roi
            }
            
            self.history.append(portfolio_value)
        
        except Exception as e:
            logger.error(f"포트폴리오 가치 기록 중 오류 발생: {str(e)}")
    
    def update_portfolio_value(self, prices: Dict[str, float], timestamp: str = None):
        """
        최신 가격으로 포트폴리오 가치를 업데이트합니다.
        
        Args:
            prices: 주식 가격 정보
            timestamp: 업데이트 시간 (없으면 현재 시간)
        """
        self._record_portfolio_value(timestamp=timestamp, prices=prices)
    
    def get_current_value(self, prices: Dict[str, float] = None) -> Dict[str, Any]:
        """
        현재 포트폴리오 가치를 반환합니다.
        
        Args:
            prices: 주식 가격 정보 (없으면 마지막 거래 가격 사용)
            
        Returns:
            포트폴리오 가치 정보
        """
        try:
            # 포지션 가치 계산
            positions_value = 0.0
            positions_detail = []
            
            for symbol, position in self.positions.items():
                quantity = position["quantity"]
                avg_price = position["avg_price"]
                
                # 가격 결정
                if prices is not None and symbol in prices:
                    current_price = prices[symbol]
                else:
                    current_price = avg_price
                
                # 포지션 가치 계산
                position_value = quantity * current_price
                positions_value += position_value
                
                # 수익률 계산
                position_roi = (current_price - avg_price) / avg_price * 100
                
                # 포지션 상세 정보
                position_detail = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "avg_price": avg_price,
                    "current_price": current_price,
                    "value": position_value,
                    "roi": position_roi
                }
                
                positions_detail.append(position_detail)
            
            # 총 포트폴리오 가치 계산
            total_value = self.cash + positions_value
            
            # 수익률 계산
            roi = (total_value - self.initial_cash) / self.initial_cash * 100
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cash": self.cash,
                "positions_value": positions_value,
                "positions_detail": positions_detail,
                "total_value": total_value,
                "initial_cash": self.initial_cash,
                "roi": roi
            }
        
        except Exception as e:
            logger.error(f"포트폴리오 가치 계산 중 오류 발생: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "cash": self.cash,
                "positions_value": 0.0,
                "positions_detail": [],
                "total_value": self.cash,
                "initial_cash": self.initial_cash,
                "roi": 0.0,
                "error": str(e)
            }
    
    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """
        거래 내역을 반환합니다.
        
        Returns:
            거래 내역 목록
        """
        return self.transactions
    
    def get_portfolio_history(self) -> List[Dict[str, Any]]:
        """
        포트폴리오 가치 변화 내역을 반환합니다.
        
        Returns:
            포트폴리오 가치 변화 내역 목록
        """
        return self.history
    
    def to_dict(self) -> Dict[str, Any]:
        """
        포트폴리오 정보를 딕셔너리로 변환합니다.
        
        Returns:
            포트폴리오 정보 딕셔너리
        """
        return {
            "initial_cash": self.initial_cash,
            "cash": self.cash,
            "positions": self.positions,
            "transactions": self.transactions,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Portfolio':
        """
        딕셔너리에서 포트폴리오를 생성합니다.
        
        Args:
            data: 포트폴리오 정보 딕셔너리
            
        Returns:
            포트폴리오 인스턴스
        """
        portfolio = cls(initial_cash=data.get("initial_cash", 100.0))
        portfolio.cash = data.get("cash", portfolio.initial_cash)
        portfolio.positions = data.get("positions", {})
        portfolio.transactions = data.get("transactions", [])
        portfolio.history = data.get("history", [])
        
        return portfolio


class MockInvestmentManager:
    """
    모의 투자 관리자
    """
    
    def __init__(
        self, 
        ai_provider: BaseAIProvider, 
        initial_cash: float = 100.0,
        data_dir: str = "/tmp/stock_market_ai/investments"
    ):
        """
        모의 투자 관리자 초기화
        
        Args:
            ai_provider: AI 제공자
            initial_cash: 초기 투자 금액
            data_dir: 데이터 저장 디렉토리
        """
        self.ai_provider = ai_provider
        self.initial_cash = initial_cash
        self.data_dir = data_dir
        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.yahoo_api = YahooFinanceAPI()
        
        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info(f"모의 투자 관리자가 초기화되었습니다. 초기 자금: ${initial_cash:.2f}")
    
    def make_investment_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        투자 결정을 내립니다.
        
        Args:
            market_data: 시장 데이터
            
        Returns:
            투자 결정 결과
        """
        try:
            # 현재 포트폴리오 가치 계산
            portfolio_value = self.portfolio.get_current_value()
            available_funds = portfolio_value["cash"]
            
            # AI 제공자를 통한 투자 결정
            decision = self.ai_provider.make_investment_decision(market_data, available_funds)
            
            # 투자 결정 저장
            self._save_investment_decision(decision)
            
            return decision
        
        except Exception as e:
            logger.error(f"투자 결정 중 오류 발생: {str(e)}")
            raise
    
    def execute_investment_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        투자 결정을 실행합니다.
        
        Args:
            decision: 투자 결정
            
        Returns:
            실행 결과
        """
        try:
            # 투자 목록 추출
            investments = decision.get("investments", [])
            
            # 현재 가격 조회
            symbols = [investment["symbol"] for investment in investments]
            prices = self._get_current_prices(symbols)
            
            # 투자 실행 결과
            execution_results = []
            
            # 투자 실행
            for investment in investments:
                symbol = investment["symbol"]
                amount = investment.get("amount", 0.0)
                reason = investment.get("reason", "AI 추천")
                
                # 현재 가격 확인
                if symbol not in prices:
                    logger.warning(f"가격 정보 없음: {symbol}")
                    execution_results.append({
                        "symbol": symbol,
                        "status": "failed",
                        "reason": "가격 정보 없음"
                    })
                    continue
                
                price = prices[symbol]
                
                # 수량 계산
                quantity = amount / price
                
                # 매수 실행
                success = self.portfolio.buy(
                    symbol=symbol,
                    quantity=quantity,
                    price=price,
                    reason=reason
                )
                
                # 실행 결과 기록
                execution_results.append({
                    "symbol": symbol,
                    "status": "success" if success else "failed",
                    "quantity": quantity if success else 0,
                    "price": price,
                    "amount": amount,
                    "reason": reason
                })
            
            # 포트폴리오 가치 업데이트
            self.portfolio.update_portfolio_value(prices)
            
            # 포트폴리오 저장
            self._save_portfolio()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "execution_results": execution_results,
                "portfolio_value": self.portfolio.get_current_value(prices)
            }
        
        except Exception as e:
            logger.error(f"투자 결정 실행 중 오류 발생: {str(e)}")
            raise
    
    def _get_current_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        현재 주식 가격을 조회합니다.
        
        Args:
            symbols: 주식 심볼 목록
            
        Returns:
            심볼별 가격 정보
        """
        prices = {}
        
        for symbol in symbols:
            try:
                # Yahoo Finance API를 통한 가격 조회
                stock_data = self.yahoo_api.get_stock_chart(
                    symbol=symbol,
                    interval="1d",
                    range="1d"
                )
                
                # 최신 종가 추출
                if "chart" in stock_data and "result" in stock_data["chart"]:
                    result = stock_data["chart"]["result"][0]
                    
                    if "meta" in result and "regularMarketPrice" in result["meta"]:
                        price = result["meta"]["regularMarketPrice"]
                        prices[symbol] = price
                    else:
                        logger.warning(f"가격 정보 없음: {symbol}")
            
            except Exception as e:
                logger.warning(f"{symbol} 가격 조회 중 오류 발생: {str(e)}")
        
        return prices
    
    def update_portfolio(self) -> Dict[str, Any]:
        """
        포트폴리오를 최신 가격으로 업데이트합니다.
        
        Returns:
            업데이트된 포트폴리오 가치
        """
        try:
            # 보유 주식 심볼 목록
            symbols = list(self.portfolio.positions.keys())
            
            # 현재 가격 조회
            prices = self._get_current_prices(symbols)
            
            # 포트폴리오 가치 업데이트
            self.portfolio.update_portfolio_value(prices)
            
            # 포트폴리오 저장
            self._save_portfolio()
            
            return self.portfolio.get_current_value(prices)
        
        except Exception as e:
            logger.error(f"포트폴리오 업데이트 중 오류 발생: {str(e)}")
            raise
    
    def get_portfolio_performance(self) -> Dict[str, Any]:
        """
        포트폴리오 성과를 반환합니다.
        
        Returns:
            포트폴리오 성과 정보
        """
        try:
            # 포트폴리오 가치 업데이트
            self.update_portfolio()
            
            # 포트폴리오 가치 및 내역
            portfolio_value = self.portfolio.get_current_value()
            portfolio_history = self.portfolio.get_portfolio_history()
            transaction_history = self.portfolio.get_transaction_history()
            
            # 성과 지표 계산
            if len(portfolio_history) > 1:
                # 시작 가치
                start_value = portfolio_history[0]["total_value"]
                
                # 현재 가치
                current_value = portfolio_value["total_value"]
                
                # 총 수익률
                total_roi = (current_value - start_value) / start_value * 100
                
                # 일일 수익률 계산
                daily_roi = []
                
                for i in range(1, len(portfolio_history)):
                    prev_value = portfolio_history[i-1]["total_value"]
                    curr_value = portfolio_history[i]["total_value"]
                    
                    daily_roi_value = (curr_value - prev_value) / prev_value * 100
                    
                    daily_roi.append({
                        "timestamp": portfolio_history[i]["timestamp"],
                        "roi": daily_roi_value
                    })
            else:
                total_roi = 0.0
                daily_roi = []
            
            return {
                "timestamp": datetime.now().isoformat(),
                "portfolio_value": portfolio_value,
                "total_roi": total_roi,
                "daily_roi": daily_roi,
                "portfolio_history": portfolio_history,
                "transaction_history": transaction_history
            }
        
        except Exception as e:
            logger.error(f"포트폴리오 성과 계산 중 오류 발생: {str(e)}")
            raise
    
    def _save_investment_decision(self, decision: Dict[str, Any]):
        """
        투자 결정을 저장합니다.
        
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
            
            logger.info(f"투자 결정이 저장되었습니다: {file_path}")
        
        except Exception as e:
            logger.error(f"투자 결정 저장 중 오류 발생: {str(e)}")
    
    def _save_portfolio(self):
        """
        포트폴리오를 저장합니다.
        """
        try:
            # 파일 경로 생성
            file_path = os.path.join(self.data_dir, "portfolio.json")
            
            # 포트폴리오 저장
            with open(file_path, "w") as f:
                json.dump(self.portfolio.to_dict(), f, indent=2)
            
            logger.info(f"포트폴리오가 저장되었습니다: {file_path}")
        
        except Exception as e:
            logger.error(f"포트폴리오 저장 중 오류 발생: {str(e)}")
    
    def load_portfolio(self) -> bool:
        """
        저장된 포트폴리오를 로드합니다.
        
        Returns:
            로드 성공 여부
        """
        try:
            # 파일 경로 생성
            file_path = os.path.join(self.data_dir, "portfolio.json")
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                logger.warning(f"포트폴리오 파일이 존재하지 않습니다: {file_path}")
                return False
            
            # 포트폴리오 로드
            with open(file_path, "r") as f:
                portfolio_data = json.load(f)
            
            # 포트폴리오 생성
            self.portfolio = Portfolio.from_dict(portfolio_data)
            
            logger.info(f"포트폴리오가 로드되었습니다: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"포트폴리오 로드 중 오류 발생: {str(e)}")
            return False


class InvestmentAnalyzer:
    """
    투자 분석기
    """
    
    def __init__(self, portfolio: Portfolio):
        """
        투자 분석기 초기화
        
        Args:
            portfolio: 포트폴리오
        """
        self.portfolio = portfolio
        
        logger.info("투자 분석기가 초기화되었습니다.")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        포트폴리오 성과를 분석합니다.
        
        Returns:
            분석 결과
        """
        try:
            # 포트폴리오 가치 및 내역
            portfolio_value = self.portfolio.get_current_value()
            portfolio_history = self.portfolio.get_portfolio_history()
            transaction_history = self.portfolio.get_transaction_history()
            
            # 분석 결과
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "current_value": portfolio_value,
                "performance_metrics": {}
            }
            
            # 성과 지표 계산
            if len(portfolio_history) > 1:
                # 시작 가치
                start_value = portfolio_history[0]["total_value"]
                
                # 현재 가치
                current_value = portfolio_value["total_value"]
                
                # 총 수익률
                total_roi = (current_value - start_value) / start_value * 100
                
                # 일일 수익률 계산
                daily_roi_values = []
                
                for i in range(1, len(portfolio_history)):
                    prev_value = portfolio_history[i-1]["total_value"]
                    curr_value = portfolio_history[i]["total_value"]
                    
                    daily_roi_value = (curr_value - prev_value) / prev_value * 100
                    daily_roi_values.append(daily_roi_value)
                
                # 평균 일일 수익률
                avg_daily_roi = sum(daily_roi_values) / len(daily_roi_values) if daily_roi_values else 0.0
                
                # 최대 일일 수익률
                max_daily_roi = max(daily_roi_values) if daily_roi_values else 0.0
                
                # 최소 일일 수익률
                min_daily_roi = min(daily_roi_values) if daily_roi_values else 0.0
                
                # 변동성 (일일 수익률의 표준 편차)
                volatility = np.std(daily_roi_values) if len(daily_roi_values) > 1 else 0.0
                
                # 성과 지표 추가
                analysis["performance_metrics"] = {
                    "total_roi": total_roi,
                    "avg_daily_roi": avg_daily_roi,
                    "max_daily_roi": max_daily_roi,
                    "min_daily_roi": min_daily_roi,
                    "volatility": volatility
                }
            
            # 거래 분석
            if transaction_history:
                # 총 거래 횟수
                total_trades = len(transaction_history)
                
                # 매수 거래 횟수
                buy_trades = sum(1 for t in transaction_history if t["type"] == "buy")
                
                # 매도 거래 횟수
                sell_trades = sum(1 for t in transaction_history if t["type"] == "sell")
                
                # 거래 분석 추가
                analysis["trade_analysis"] = {
                    "total_trades": total_trades,
                    "buy_trades": buy_trades,
                    "sell_trades": sell_trades
                }
            
            return analysis
        
        except Exception as e:
            logger.error(f"성과 분석 중 오류 발생: {str(e)}")
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """
        투자 보고서를 생성합니다.
        
        Returns:
            투자 보고서
        """
        try:
            # 성과 분석
            analysis = self.analyze_performance()
            
            # 포트폴리오 가치 및 내역
            portfolio_value = self.portfolio.get_current_value()
            portfolio_history = self.portfolio.get_portfolio_history()
            transaction_history = self.portfolio.get_transaction_history()
            
            # 보고서 생성
            report = {
                "timestamp": datetime.now().isoformat(),
                "portfolio_summary": {
                    "initial_cash": self.portfolio.initial_cash,
                    "current_cash": portfolio_value["cash"],
                    "positions_value": portfolio_value["positions_value"],
                    "total_value": portfolio_value["total_value"],
                    "roi": portfolio_value["roi"]
                },
                "performance_analysis": analysis["performance_metrics"] if "performance_metrics" in analysis else {},
                "trade_analysis": analysis["trade_analysis"] if "trade_analysis" in analysis else {},
                "positions": portfolio_value["positions_detail"],
                "recent_transactions": transaction_history[-5:] if len(transaction_history) > 5 else transaction_history
            }
            
            return report
        
        except Exception as e:
            logger.error(f"보고서 생성 중 오류 발생: {str(e)}")
            raise
    
    def generate_chart_data(self) -> Dict[str, Any]:
        """
        차트 데이터를 생성합니다.
        
        Returns:
            차트 데이터
        """
        try:
            # 포트폴리오 가치 내역
            portfolio_history = self.portfolio.get_portfolio_history()
            
            # 차트 데이터 생성
            chart_data = {
                "timestamps": [],
                "total_values": [],
                "cash_values": [],
                "positions_values": [],
                "roi_values": []
            }
            
            for entry in portfolio_history:
                chart_data["timestamps"].append(entry["timestamp"])
                chart_data["total_values"].append(entry["total_value"])
                chart_data["cash_values"].append(entry["cash"])
                chart_data["positions_values"].append(entry["positions_value"])
                chart_data["roi_values"].append(entry["roi"])
            
            return chart_data
        
        except Exception as e:
            logger.error(f"차트 데이터 생성 중 오류 발생: {str(e)}")
            raise
