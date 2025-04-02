"""
Neo4j 데이터베이스 저장 및 조회 API 모듈

이 모듈은 Neo4j 그래프 데이터베이스에 데이터를 저장하고 조회하는 API를 제공합니다.
주식 시장 데이터, 임베딩, 투자 결정 등을 저장하고 조회하는 기능을 구현합니다.
"""
import os
import logging
import json
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
import uuid
from neo4j import GraphDatabase, Driver, Session, Result

from .schema import Neo4jSchema

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Neo4jRepository:
    """
    Neo4j 데이터베이스 저장소 클래스
    """
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Neo4j 저장소 초기화
        
        Args:
            uri: Neo4j 서버 URI
            user: 사용자 이름
            password: 비밀번호
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        
        logger.info(f"Neo4j 저장소가 초기화되었습니다. URI: {uri}")
    
    def connect(self) -> bool:
        """
        Neo4j 데이터베이스에 연결합니다.
        
        Returns:
            연결 성공 여부
        """
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            
            # 연결 테스트
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                test_value = result.single()["test"]
                
                if test_value == 1:
                    logger.info("Neo4j 데이터베이스 연결 성공")
                    return True
                else:
                    logger.error("Neo4j 데이터베이스 연결 테스트 실패")
                    return False
        
        except Exception as e:
            logger.error(f"Neo4j 데이터베이스 연결 중 오류 발생: {str(e)}")
            return False
    
    def close(self):
        """
        Neo4j 데이터베이스 연결을 종료합니다.
        """
        if self.driver:
            self.driver.close()
            logger.info("Neo4j 데이터베이스 연결 종료")
    
    # 주식 관련 메서드
    
    def save_stock(self, stock_data: Dict[str, Any]) -> bool:
        """
        주식 정보를 저장합니다.
        
        Args:
            stock_data: 주식 정보
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 주식 정보 저장 쿼리
                query = """
                MERGE (s:Stock {symbol: $symbol})
                ON CREATE SET
                    s.name = $name,
                    s.created_at = datetime(),
                    s.updated_at = datetime()
                ON MATCH SET
                    s.name = $name,
                    s.updated_at = datetime()
                
                WITH s
                
                MERGE (m:Market {name: $market})
                ON CREATE SET
                    m.region = $region,
                    m.created_at = datetime(),
                    m.updated_at = datetime()
                ON MATCH SET
                    m.region = $region,
                    m.updated_at = datetime()
                
                MERGE (s)-[:BELONGS_TO]->(m)
                
                RETURN s.symbol AS symbol
                """
                
                result = session.run(
                    query,
                    symbol=stock_data.get("symbol"),
                    name=stock_data.get("name"),
                    market=stock_data.get("market"),
                    region=stock_data.get("region")
                )
                
                record = result.single()
                
                if record and record["symbol"] == stock_data.get("symbol"):
                    logger.info(f"주식 정보 저장 성공: {stock_data.get('symbol')}")
                    return True
                else:
                    logger.warning(f"주식 정보 저장 실패: {stock_data.get('symbol')}")
                    return False
        
        except Exception as e:
            logger.error(f"주식 정보 저장 중 오류 발생: {str(e)}")
            return False
    
    def save_stock_price(self, price_data: Dict[str, Any]) -> bool:
        """
        주식 가격 정보를 저장합니다.
        
        Args:
            price_data: 주식 가격 정보
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 주식 가격 정보 저장 쿼리
                query = """
                MATCH (s:Stock {symbol: $symbol})
                
                CREATE (p:StockPrice {
                    id: $id,
                    date: datetime($date),
                    open: $open,
                    high: $high,
                    low: $low,
                    close: $close,
                    volume: $volume,
                    adjusted_close: $adjusted_close,
                    created_at: datetime()
                })
                
                CREATE (s)-[:HAS_PRICE]->(p)
                
                WITH p, s
                
                OPTIONAL MATCH (s)-[:HAS_PRICE]->(prev:StockPrice)
                WHERE prev.date < p.date
                WITH p, prev
                ORDER BY prev.date DESC
                LIMIT 1
                
                FOREACH (prev IN CASE WHEN prev IS NOT NULL THEN [prev] ELSE [] END |
                    CREATE (prev)-[:NEXT]->(p)
                )
                
                RETURN p.id AS id
                """
                
                # ID 생성
                price_id = str(uuid.uuid4())
                
                result = session.run(
                    query,
                    id=price_id,
                    symbol=price_data.get("symbol"),
                    date=price_data.get("date"),
                    open=price_data.get("open"),
                    high=price_data.get("high"),
                    low=price_data.get("low"),
                    close=price_data.get("close"),
                    volume=price_data.get("volume"),
                    adjusted_close=price_data.get("adjusted_close")
                )
                
                record = result.single()
                
                if record and record["id"] == price_id:
                    logger.info(f"주식 가격 정보 저장 성공: {price_data.get('symbol')} ({price_data.get('date')})")
                    return True
                else:
                    logger.warning(f"주식 가격 정보 저장 실패: {price_data.get('symbol')} ({price_data.get('date')})")
                    return False
        
        except Exception as e:
            logger.error(f"주식 가격 정보 저장 중 오류 발생: {str(e)}")
            return False
    
    def save_market_summary(self, summary_data: Dict[str, Any]) -> bool:
        """
        시장 요약 정보를 저장합니다.
        
        Args:
            summary_data: 시장 요약 정보
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 시장 요약 정보 저장 쿼리
                query = """
                MERGE (m:Market {name: $market})
                ON CREATE SET
                    m.region = $region,
                    m.created_at = datetime(),
                    m.updated_at = datetime()
                ON MATCH SET
                    m.region = $region,
                    m.updated_at = datetime()
                
                CREATE (s:MarketSummary {
                    id: $id,
                    date: datetime($date),
                    summary_text: $summary_text,
                    created_at: datetime()
                })
                
                CREATE (s)-[:SUMMARIZES]->(m)
                
                WITH s, m
                
                OPTIONAL MATCH (prev:MarketSummary)-[:SUMMARIZES]->(m)
                WHERE prev.date < s.date
                WITH s, prev
                ORDER BY prev.date DESC
                LIMIT 1
                
                FOREACH (prev IN CASE WHEN prev IS NOT NULL THEN [prev] ELSE [] END |
                    CREATE (prev)-[:NEXT]->(s)
                )
                
                RETURN s.id AS id
                """
                
                # ID 생성
                summary_id = str(uuid.uuid4())
                
                result = session.run(
                    query,
                    id=summary_id,
                    market=summary_data.get("market"),
                    region=summary_data.get("region"),
                    date=summary_data.get("date"),
                    summary_text=summary_data.get("summary_text")
                )
                
                record = result.single()
                
                if record and record["id"] == summary_id:
                    logger.info(f"시장 요약 정보 저장 성공: {summary_data.get('market')} ({summary_data.get('date')})")
                    return True
                else:
                    logger.warning(f"시장 요약 정보 저장 실패: {summary_data.get('market')} ({summary_data.get('date')})")
                    return False
        
        except Exception as e:
            logger.error(f"시장 요약 정보 저장 중 오류 발생: {str(e)}")
            return False
    
    # 임베딩 관련 메서드
    
    def save_embedding(self, embedding_data: Dict[str, Any]) -> bool:
        """
        임베딩 정보를 저장합니다.
        
        Args:
            embedding_data: 임베딩 정보
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 임베딩 정보 저장 쿼리
                query = """
                CREATE (e:Embedding {
                    id: $id,
                    source: $source,
                    source_type: $source_type,
                    vector: $vector,
                    text: $text,
                    model: $model,
                    created_at: datetime()
                })
                
                WITH e
                
                CALL {
                    WITH e
                    MATCH (s:MarketSummary {id: $source_id})
                    WHERE $source_type = 'market_summary'
                    CREATE (e)-[:EMBEDS]->(s)
                    RETURN count(*) as cnt
                }
                
                CALL {
                    WITH e
                    MATCH (s:Stock {symbol: $source_id})
                    WHERE $source_type = 'stock'
                    CREATE (e)-[:EMBEDS]->(s)
                    RETURN count(*) as cnt
                }
                
                RETURN e.id AS id
                """
                
                # ID 생성
                embedding_id = embedding_data.get("id", str(uuid.uuid4()))
                
                result = session.run(
                    query,
                    id=embedding_id,
                    source=embedding_data.get("source"),
                    source_type=embedding_data.get("source_type"),
                    source_id=embedding_data.get("source_id"),
                    vector=embedding_data.get("vector"),
                    text=embedding_data.get("text"),
                    model=embedding_data.get("model")
                )
                
                record = result.single()
                
                if record and record["id"] == embedding_id:
                    logger.info(f"임베딩 정보 저장 성공: {embedding_id}")
                    return True
                else:
                    logger.warning(f"임베딩 정보 저장 실패: {embedding_id}")
                    return False
        
        except Exception as e:
            logger.error(f"임베딩 정보 저장 중 오류 발생: {str(e)}")
            return False
    
    def find_similar_embeddings(self, vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        유사한 임베딩을 검색합니다.
        
        Args:
            vector: 검색할 벡터
            limit: 결과 제한 수
            
        Returns:
            유사한 임베딩 목록
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                # 유사한 임베딩 검색 쿼리
                query = """
                MATCH (e:Embedding)
                WITH e, gds.similarity.cosine($vector, e.vector) AS similarity
                ORDER BY similarity DESC
                LIMIT $limit
                RETURN e.id AS id, e.source AS source, e.source_type AS source_type, 
                       e.text AS text, e.model AS model, similarity
                """
                
                result = session.run(query, vector=vector, limit=limit)
                
                embeddings = []
                for record in result:
                    embedding = {
                        "id": record["id"],
                        "source": record["source"],
                        "source_type": record["source_type"],
                        "text": record["text"],
                        "model": record["model"],
                        "similarity": record["similarity"]
                    }
                    embeddings.append(embedding)
                
                logger.info(f"유사한 임베딩 검색 성공: {len(embeddings)}개 결과")
                return embeddings
        
        except Exception as e:
            logger.error(f"유사한 임베딩 검색 중 오류 발생: {str(e)}")
            return []
    
    # AI 분석 관련 메서드
    
    def save_ai_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """
        AI 분석 결과를 저장합니다.
        
        Args:
            analysis_data: AI 분석 결과
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # AI 분석 결과 저장 쿼리
                query = """
                CREATE (a:AIAnalysis {
                    id: $id,
                    timestamp: datetime($timestamp),
                    provider: $provider,
                    model: $model,
                    analysis_type: $analysis_type,
                    analysis_text: $analysis_text,
                    created_at: datetime()
                })
                
                WITH a
                
                CALL {
                    WITH a
                    MATCH (s:MarketSummary {id: $source_id})
                    WHERE $source_type = 'market_summary'
                    CREATE (a)-[:ANALYZES]->(s)
                    RETURN count(*) as cnt
                }
                
                CALL {
                    WITH a
                    MATCH (s:Stock {symbol: $source_id})
                    WHERE $source_type = 'stock'
                    CREATE (a)-[:ANALYZES]->(s)
                    RETURN count(*) as cnt
                }
                
                RETURN a.id AS id
                """
                
                # ID 생성
                analysis_id = analysis_data.get("id", str(uuid.uuid4()))
                
                result = session.run(
                    query,
                    id=analysis_id,
                    timestamp=analysis_data.get("timestamp"),
                    provider=analysis_data.get("provider"),
                    model=analysis_data.get("model"),
                    analysis_type=analysis_data.get("analysis_type"),
                    analysis_text=analysis_data.get("analysis_text"),
                    source_type=analysis_data.get("source_type"),
                    source_id=analysis_data.get("source_id")
                )
                
                record = result.single()
                
                if record and record["id"] == analysis_id:
                    logger.info(f"AI 분석 결과 저장 성공: {analysis_id}")
                    return True
                else:
                    logger.warning(f"AI 분석 결과 저장 실패: {analysis_id}")
                    return False
        
        except Exception as e:
            logger.error(f"AI 분석 결과 저장 중 오류 발생: {str(e)}")
            return False
    
    def save_investment_decision(self, decision_data: Dict[str, Any]) -> bool:
        """
        투자 결정을 저장합니다.
        
        Args:
            decision_data: 투자 결정
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 투자 결정 저장 쿼리
                query = """
                CREATE (d:InvestmentDecision {
                    id: $id,
                    timestamp: datetime($timestamp),
                    provider: $provider,
                    model: $model,
                    available_funds: $available_funds,
                    strategy: $strategy,
                    created_at: datetime()
                })
                
                WITH d
                
                MATCH (a:AIAnalysis {id: $analysis_id})
                CREATE (d)-[:DECIDES]->(a)
                
                WITH d
                
                UNWIND $investments AS investment
                MATCH (s:Stock {symbol: investment.symbol})
                CREATE (d)-[:CONTAINS {
                    amount: investment.amount,
                    reason: investment.reason
                }]->(s)
                
                RETURN d.id AS id
                """
                
                # ID 생성
                decision_id = decision_data.get("id", str(uuid.uuid4()))
                
                result = session.run(
                    query,
                    id=decision_id,
                    timestamp=decision_data.get("timestamp"),
                    provider=decision_data.get("provider"),
                    model=decision_data.get("model"),
                    available_funds=decision_data.get("available_funds"),
                    strategy=decision_data.get("strategy"),
                    analysis_id=decision_data.get("analysis_id"),
                    investments=decision_data.get("investments", [])
                )
                
                record = result.single()
                
                if record and record["id"] == decision_id:
                    logger.info(f"투자 결정 저장 성공: {decision_id}")
                    return True
                else:
                    logger.warning(f"투자 결정 저장 실패: {decision_id}")
                    return False
        
        except Exception as e:
            logger.error(f"투자 결정 저장 중 오류 발생: {str(e)}")
            return False
    
    # 포트폴리오 관련 메서드
    
    def save_portfolio(self, portfolio_data: Dict[str, Any]) -> bool:
        """
        포트폴리오 정보를 저장합니다.
        
        Args:
            portfolio_data: 포트폴리오 정보
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 포트폴리오 정보 저장 쿼리
                query = """
                MERGE (p:Portfolio {id: $id})
                ON CREATE SET
                    p.date = datetime($date),
                    p.initial_cash = $initial_cash,
                    p.cash = $cash,
                    p.positions_value = $positions_value,
                    p.total_value = $total_value,
                    p.roi = $roi,
                    p.created_at = datetime(),
                    p.updated_at = datetime()
                ON MATCH SET
                    p.date = datetime($date),
                    p.cash = $cash,
                    p.positions_value = $positions_value,
                    p.total_value = $total_value,
                    p.roi = $roi,
                    p.updated_at = datetime()
                
                WITH p
                
                OPTIONAL MATCH (p)-[r:CONTAINS]->(:Stock)
                DELETE r
                
                WITH p
                
                UNWIND $positions AS position
                MATCH (s:Stock {symbol: position.symbol})
                CREATE (p)-[:CONTAINS {
                    quantity: position.quantity,
                    avg_price: position.avg_price,
                    current_price: position.current_price,
                    value: position.value,
                    roi: position.roi
                }]->(s)
                
                RETURN p.id AS id
                """
                
                # ID 생성
                portfolio_id = portfolio_data.get("id", str(uuid.uuid4()))
                
                result = session.run(
                    query,
                    id=portfolio_id,
                    date=portfolio_data.get("date"),
                    initial_cash=portfolio_data.get("initial_cash"),
                    cash=portfolio_data.get("cash"),
                    positions_value=portfolio_data.get("positions_value"),
                    total_value=portfolio_data.get("total_value"),
                    roi=portfolio_data.get("roi"),
                    positions=portfolio_data.get("positions", [])
                )
                
                record = result.single()
                
                if record and record["id"] == portfolio_id:
                    logger.info(f"포트폴리오 정보 저장 성공: {portfolio_id}")
                    return True
                else:
                    logger.warning(f"포트폴리오 정보 저장 실패: {portfolio_id}")
                    return False
        
        except Exception as e:
            logger.error(f"포트폴리오 정보 저장 중 오류 발생: {str(e)}")
            return False
    
    def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        거래 내역을 저장합니다.
        
        Args:
            transaction_data: 거래 내역
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 거래 내역 저장 쿼리
                query = """
                CREATE (t:Transaction {
                    id: $id,
                    timestamp: datetime($timestamp),
                    type: $type,
                    symbol: $symbol,
                    quantity: $quantity,
                    price: $price,
                    amount: $amount,
                    reason: $reason,
                    created_at: datetime()
                })
                
                WITH t
                
                MATCH (p:Portfolio {id: $portfolio_id})
                CREATE (p)-[:EXECUTES]->(t)
                
                WITH t
                
                MATCH (s:Stock {symbol: $symbol})
                CREATE (t)-[:INVOLVES]->(s)
                
                WITH t
                
                OPTIONAL MATCH (d:InvestmentDecision {id: $decision_id})
                FOREACH (d IN CASE WHEN d IS NOT NULL THEN [d] ELSE [] END |
                    CREATE (t)-[:BASED_ON]->(d)
                )
                
                RETURN t.id AS id
                """
                
                # ID 생성
                transaction_id = transaction_data.get("id", str(uuid.uuid4()))
                
                result = session.run(
                    query,
                    id=transaction_id,
                    timestamp=transaction_data.get("timestamp"),
                    type=transaction_data.get("type"),
                    symbol=transaction_data.get("symbol"),
                    quantity=transaction_data.get("quantity"),
                    price=transaction_data.get("price"),
                    amount=transaction_data.get("amount"),
                    reason=transaction_data.get("reason"),
                    portfolio_id=transaction_data.get("portfolio_id"),
                    decision_id=transaction_data.get("decision_id")
                )
                
                record = result.single()
                
                if record and record["id"] == transaction_id:
                    logger.info(f"거래 내역 저장 성공: {transaction_id}")
                    return True
                else:
                    logger.warning(f"거래 내역 저장 실패: {transaction_id}")
                    return False
        
        except Exception as e:
            logger.error(f"거래 내역 저장 중 오류 발생: {str(e)}")
            return False
    
    def save_performance_report(self, report_data: Dict[str, Any]) -> bool:
        """
        성과 보고서를 저장합니다.
        
        Args:
            report_data: 성과 보고서
            
        Returns:
            저장 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            with self.driver.session() as session:
                # 성과 보고서 저장 쿼리
                query = """
                CREATE (r:PerformanceReport {
                    id: $id,
                    date: datetime($date),
                    type: $type,
                    initial_cash: $initial_cash,
                    current_cash: $current_cash,
                    positions_value: $positions_value,
                    total_value: $total_value,
                    roi: $roi,
                    report_data: $report_data,
                    created_at: datetime()
                })
                
                WITH r
                
                MATCH (p:Portfolio {id: $portfolio_id})
                CREATE (r)-[:REPORTS]->(p)
                
                RETURN r.id AS id
                """
                
                # ID 생성
                report_id = report_data.get("id", str(uuid.uuid4()))
                
                result = session.run(
                    query,
                    id=report_id,
                    date=report_data.get("date"),
                    type=report_data.get("type"),
                    initial_cash=report_data.get("initial_cash"),
                    current_cash=report_data.get("current_cash"),
                    positions_value=report_data.get("positions_value"),
                    total_value=report_data.get("total_value"),
                    roi=report_data.get("roi"),
                    report_data=json.dumps(report_data.get("report_data", {})),
                    portfolio_id=report_data.get("portfolio_id")
                )
                
                record = result.single()
                
                if record and record["id"] == report_id:
                    logger.info(f"성과 보고서 저장 성공: {report_id}")
                    return True
                else:
                    logger.warning(f"성과 보고서 저장 실패: {report_id}")
                    return False
        
        except Exception as e:
            logger.error(f"성과 보고서 저장 중 오류 발생: {str(e)}")
            return False
    
    # 조회 메서드
    
    def get_stock_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        심볼로 주식 정보를 조회합니다.
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            주식 정보
        """
        try:
            if not self.driver:
                if not self.connect():
                    return {}
            
            with self.driver.session() as session:
                # 주식 정보 조회 쿼리
                query = """
                MATCH (s:Stock {symbol: $symbol})
                OPTIONAL MATCH (s)-[:BELONGS_TO]->(m:Market)
                RETURN s.symbol AS symbol, s.name AS name,
                       m.name AS market, m.region AS region
                """
                
                result = session.run(query, symbol=symbol)
                record = result.single()
                
                if record:
                    stock = {
                        "symbol": record["symbol"],
                        "name": record["name"],
                        "market": record["market"],
                        "region": record["region"]
                    }
                    return stock
                else:
                    logger.warning(f"주식 정보 조회 실패: {symbol}")
                    return {}
        
        except Exception as e:
            logger.error(f"주식 정보 조회 중 오류 발생: {str(e)}")
            return {}
    
    def get_stock_prices(self, symbol: str, limit: int = 30) -> List[Dict[str, Any]]:
        """
        주식 가격 정보를 조회합니다.
        
        Args:
            symbol: 주식 심볼
            limit: 결과 제한 수
            
        Returns:
            주식 가격 정보 목록
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                # 주식 가격 정보 조회 쿼리
                query = """
                MATCH (s:Stock {symbol: $symbol})-[:HAS_PRICE]->(p:StockPrice)
                RETURN p.id AS id, p.date AS date, p.open AS open, p.high AS high,
                       p.low AS low, p.close AS close, p.volume AS volume,
                       p.adjusted_close AS adjusted_close
                ORDER BY p.date DESC
                LIMIT $limit
                """
                
                result = session.run(query, symbol=symbol, limit=limit)
                
                prices = []
                for record in result:
                    price = {
                        "id": record["id"],
                        "date": record["date"],
                        "open": record["open"],
                        "high": record["high"],
                        "low": record["low"],
                        "close": record["close"],
                        "volume": record["volume"],
                        "adjusted_close": record["adjusted_close"]
                    }
                    prices.append(price)
                
                return prices
        
        except Exception as e:
            logger.error(f"주식 가격 정보 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_market_summaries(self, market: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        시장 요약 정보를 조회합니다.
        
        Args:
            market: 시장 이름
            limit: 결과 제한 수
            
        Returns:
            시장 요약 정보 목록
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                # 시장 요약 정보 조회 쿼리
                query = """
                MATCH (s:MarketSummary)-[:SUMMARIZES]->(m:Market {name: $market})
                RETURN s.id AS id, s.date AS date, s.summary_text AS summary_text,
                       m.name AS market, m.region AS region
                ORDER BY s.date DESC
                LIMIT $limit
                """
                
                result = session.run(query, market=market, limit=limit)
                
                summaries = []
                for record in result:
                    summary = {
                        "id": record["id"],
                        "date": record["date"],
                        "summary_text": record["summary_text"],
                        "market": record["market"],
                        "region": record["region"]
                    }
                    summaries.append(summary)
                
                return summaries
        
        except Exception as e:
            logger.error(f"시장 요약 정보 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_ai_analyses(self, analysis_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        AI 분석 결과를 조회합니다.
        
        Args:
            analysis_type: 분석 유형 (없으면 모든 유형)
            limit: 결과 제한 수
            
        Returns:
            AI 분석 결과 목록
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                # AI 분석 결과 조회 쿼리
                if analysis_type:
                    query = """
                    MATCH (a:AIAnalysis {analysis_type: $analysis_type})
                    RETURN a.id AS id, a.timestamp AS timestamp, a.provider AS provider,
                           a.model AS model, a.analysis_type AS analysis_type,
                           a.analysis_text AS analysis_text
                    ORDER BY a.timestamp DESC
                    LIMIT $limit
                    """
                    
                    result = session.run(query, analysis_type=analysis_type, limit=limit)
                else:
                    query = """
                    MATCH (a:AIAnalysis)
                    RETURN a.id AS id, a.timestamp AS timestamp, a.provider AS provider,
                           a.model AS model, a.analysis_type AS analysis_type,
                           a.analysis_text AS analysis_text
                    ORDER BY a.timestamp DESC
                    LIMIT $limit
                    """
                    
                    result = session.run(query, limit=limit)
                
                analyses = []
                for record in result:
                    analysis = {
                        "id": record["id"],
                        "timestamp": record["timestamp"],
                        "provider": record["provider"],
                        "model": record["model"],
                        "analysis_type": record["analysis_type"],
                        "analysis_text": record["analysis_text"]
                    }
                    analyses.append(analysis)
                
                return analyses
        
        except Exception as e:
            logger.error(f"AI 분석 결과 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_investment_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        투자 결정을 조회합니다.
        
        Args:
            limit: 결과 제한 수
            
        Returns:
            투자 결정 목록
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                # 투자 결정 조회 쿼리
                query = """
                MATCH (d:InvestmentDecision)
                OPTIONAL MATCH (d)-[:CONTAINS]->(s:Stock)
                WITH d, collect({symbol: s.symbol, name: s.name}) AS stocks
                RETURN d.id AS id, d.timestamp AS timestamp, d.provider AS provider,
                       d.model AS model, d.available_funds AS available_funds,
                       d.strategy AS strategy, stocks
                ORDER BY d.timestamp DESC
                LIMIT $limit
                """
                
                result = session.run(query, limit=limit)
                
                decisions = []
                for record in result:
                    decision = {
                        "id": record["id"],
                        "timestamp": record["timestamp"],
                        "provider": record["provider"],
                        "model": record["model"],
                        "available_funds": record["available_funds"],
                        "strategy": record["strategy"],
                        "stocks": record["stocks"]
                    }
                    decisions.append(decision)
                
                return decisions
        
        except Exception as e:
            logger.error(f"투자 결정 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        """
        포트폴리오 정보를 조회합니다.
        
        Args:
            portfolio_id: 포트폴리오 ID
            
        Returns:
            포트폴리오 정보
        """
        try:
            if not self.driver:
                if not self.connect():
                    return {}
            
            with self.driver.session() as session:
                # 포트폴리오 정보 조회 쿼리
                query = """
                MATCH (p:Portfolio {id: $portfolio_id})
                OPTIONAL MATCH (p)-[r:CONTAINS]->(s:Stock)
                WITH p, collect({
                    symbol: s.symbol,
                    name: s.name,
                    quantity: r.quantity,
                    avg_price: r.avg_price,
                    current_price: r.current_price,
                    value: r.value,
                    roi: r.roi
                }) AS positions
                RETURN p.id AS id, p.date AS date, p.initial_cash AS initial_cash,
                       p.cash AS cash, p.positions_value AS positions_value,
                       p.total_value AS total_value, p.roi AS roi, positions
                """
                
                result = session.run(query, portfolio_id=portfolio_id)
                record = result.single()
                
                if record:
                    portfolio = {
                        "id": record["id"],
                        "date": record["date"],
                        "initial_cash": record["initial_cash"],
                        "cash": record["cash"],
                        "positions_value": record["positions_value"],
                        "total_value": record["total_value"],
                        "roi": record["roi"],
                        "positions": record["positions"]
                    }
                    return portfolio
                else:
                    logger.warning(f"포트폴리오 정보 조회 실패: {portfolio_id}")
                    return {}
        
        except Exception as e:
            logger.error(f"포트폴리오 정보 조회 중 오류 발생: {str(e)}")
            return {}
    
    def get_transactions(self, portfolio_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        거래 내역을 조회합니다.
        
        Args:
            portfolio_id: 포트폴리오 ID
            limit: 결과 제한 수
            
        Returns:
            거래 내역 목록
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                # 거래 내역 조회 쿼리
                query = """
                MATCH (p:Portfolio {id: $portfolio_id})-[:EXECUTES]->(t:Transaction)
                RETURN t.id AS id, t.timestamp AS timestamp, t.type AS type,
                       t.symbol AS symbol, t.quantity AS quantity, t.price AS price,
                       t.amount AS amount, t.reason AS reason
                ORDER BY t.timestamp DESC
                LIMIT $limit
                """
                
                result = session.run(query, portfolio_id=portfolio_id, limit=limit)
                
                transactions = []
                for record in result:
                    transaction = {
                        "id": record["id"],
                        "timestamp": record["timestamp"],
                        "type": record["type"],
                        "symbol": record["symbol"],
                        "quantity": record["quantity"],
                        "price": record["price"],
                        "amount": record["amount"],
                        "reason": record["reason"]
                    }
                    transactions.append(transaction)
                
                return transactions
        
        except Exception as e:
            logger.error(f"거래 내역 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_performance_reports(self, portfolio_id: str, report_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        성과 보고서를 조회합니다.
        
        Args:
            portfolio_id: 포트폴리오 ID
            report_type: 보고서 유형 (없으면 모든 유형)
            limit: 결과 제한 수
            
        Returns:
            성과 보고서 목록
        """
        try:
            if not self.driver:
                if not self.connect():
                    return []
            
            with self.driver.session() as session:
                # 성과 보고서 조회 쿼리
                if report_type:
                    query = """
                    MATCH (r:PerformanceReport {type: $report_type})-[:REPORTS]->(p:Portfolio {id: $portfolio_id})
                    RETURN r.id AS id, r.date AS date, r.type AS type,
                           r.initial_cash AS initial_cash, r.current_cash AS current_cash,
                           r.positions_value AS positions_value, r.total_value AS total_value,
                           r.roi AS roi, r.report_data AS report_data
                    ORDER BY r.date DESC
                    LIMIT $limit
                    """
                    
                    result = session.run(
                        query,
                        portfolio_id=portfolio_id,
                        report_type=report_type,
                        limit=limit
                    )
                else:
                    query = """
                    MATCH (r:PerformanceReport)-[:REPORTS]->(p:Portfolio {id: $portfolio_id})
                    RETURN r.id AS id, r.date AS date, r.type AS type,
                           r.initial_cash AS initial_cash, r.current_cash AS current_cash,
                           r.positions_value AS positions_value, r.total_value AS total_value,
                           r.roi AS roi, r.report_data AS report_data
                    ORDER BY r.date DESC
                    LIMIT $limit
                    """
                    
                    result = session.run(query, portfolio_id=portfolio_id, limit=limit)
                
                reports = []
                for record in result:
                    report = {
                        "id": record["id"],
                        "date": record["date"],
                        "type": record["type"],
                        "initial_cash": record["initial_cash"],
                        "current_cash": record["current_cash"],
                        "positions_value": record["positions_value"],
                        "total_value": record["total_value"],
                        "roi": record["roi"],
                        "report_data": json.loads(record["report_data"]) if record["report_data"] else {}
                    }
                    reports.append(report)
                
                return reports
        
        except Exception as e:
            logger.error(f"성과 보고서 조회 중 오류 발생: {str(e)}")
            return []
