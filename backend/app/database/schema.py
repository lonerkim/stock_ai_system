"""
Neo4j 데이터베이스 스키마 설계 및 관리 모듈

이 모듈은 Neo4j 그래프 데이터베이스의 스키마를 정의하고 관리합니다.
주식 시장 데이터, 임베딩, 투자 결정 등을 저장하기 위한 노드와 관계를 정의합니다.
"""
import os
import logging
import json
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
from neo4j import GraphDatabase, Driver, Session, Result

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Neo4jSchema:
    """
    Neo4j 데이터베이스 스키마 관리 클래스
    """
    
    # 노드 레이블 정의
    NODE_LABELS = {
        "Stock": "주식 정보를 저장하는 노드",
        "Market": "시장 정보를 저장하는 노드",
        "Sector": "산업 섹터 정보를 저장하는 노드",
        "Company": "회사 정보를 저장하는 노드",
        "StockPrice": "주식 가격 정보를 저장하는 노드",
        "MarketSummary": "시장 요약 정보를 저장하는 노드",
        "Embedding": "텍스트 임베딩을 저장하는 노드",
        "AIAnalysis": "AI 분석 결과를 저장하는 노드",
        "InvestmentDecision": "투자 결정을 저장하는 노드",
        "Portfolio": "포트폴리오 정보를 저장하는 노드",
        "Transaction": "거래 내역을 저장하는 노드",
        "PerformanceReport": "성과 보고서를 저장하는 노드"
    }
    
    # 관계 타입 정의
    RELATIONSHIP_TYPES = {
        "BELONGS_TO": "소속 관계 (예: 주식 -> 시장, 회사 -> 섹터)",
        "HAS_PRICE": "가격 정보 관계 (예: 주식 -> 가격)",
        "SUMMARIZES": "요약 관계 (예: 요약 -> 시장)",
        "EMBEDS": "임베딩 관계 (예: 임베딩 -> 텍스트 데이터)",
        "ANALYZES": "분석 관계 (예: 분석 -> 시장 데이터)",
        "DECIDES": "결정 관계 (예: 결정 -> 분석)",
        "CONTAINS": "포함 관계 (예: 포트폴리오 -> 주식)",
        "EXECUTES": "실행 관계 (예: 거래 -> 결정)",
        "REPORTS": "보고 관계 (예: 보고서 -> 포트폴리오)",
        "NEXT": "시간적 순서 관계 (예: 가격1 -> 가격2)",
        "SIMILAR_TO": "유사성 관계 (예: 임베딩1 -> 임베딩2)"
    }
    
    # 인덱스 정의
    INDEXES = {
        "Stock": ["symbol", "name"],
        "Market": ["name", "region"],
        "Sector": ["name"],
        "Company": ["name", "ticker"],
        "StockPrice": ["date", "symbol"],
        "MarketSummary": ["date", "market"],
        "Embedding": ["id", "source"],
        "AIAnalysis": ["id", "timestamp", "provider"],
        "InvestmentDecision": ["id", "timestamp"],
        "Portfolio": ["id", "date"],
        "Transaction": ["id", "timestamp", "type"],
        "PerformanceReport": ["id", "date", "type"]
    }
    
    # 제약 조건 정의
    CONSTRAINTS = {
        "Stock": [("symbol", "unique")],
        "Market": [("name", "unique")],
        "Sector": [("name", "unique")],
        "Company": [("ticker", "unique")],
        "Embedding": [("id", "unique")],
        "AIAnalysis": [("id", "unique")],
        "InvestmentDecision": [("id", "unique")],
        "Portfolio": [("id", "unique")],
        "Transaction": [("id", "unique")],
        "PerformanceReport": [("id", "unique")]
    }
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Neo4j 스키마 관리자 초기화
        
        Args:
            uri: Neo4j 서버 URI
            user: 사용자 이름
            password: 비밀번호
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        
        logger.info(f"Neo4j 스키마 관리자가 초기화되었습니다. URI: {uri}")
    
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
    
    def create_schema(self) -> bool:
        """
        Neo4j 데이터베이스 스키마를 생성합니다.
        
        Returns:
            스키마 생성 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            # 인덱스 생성
            self._create_indexes()
            
            # 제약 조건 생성
            self._create_constraints()
            
            logger.info("Neo4j 데이터베이스 스키마 생성 완료")
            return True
        
        except Exception as e:
            logger.error(f"Neo4j 데이터베이스 스키마 생성 중 오류 발생: {str(e)}")
            return False
    
    def _create_indexes(self):
        """
        인덱스를 생성합니다.
        """
        with self.driver.session() as session:
            for label, properties in self.INDEXES.items():
                for prop in properties:
                    # 인덱스 이름 생성
                    index_name = f"{label}_{prop}_idx"
                    
                    # 인덱스 생성 쿼리
                    query = f"CREATE INDEX {index_name} IF NOT EXISTS FOR (n:{label}) ON (n.{prop})"
                    
                    try:
                        session.run(query)
                        logger.info(f"인덱스 생성: {index_name}")
                    
                    except Exception as e:
                        logger.warning(f"인덱스 생성 중 오류 발생: {index_name}, {str(e)}")
    
    def _create_constraints(self):
        """
        제약 조건을 생성합니다.
        """
        with self.driver.session() as session:
            for label, constraints in self.CONSTRAINTS.items():
                for prop, constraint_type in constraints:
                    # 제약 조건 이름 생성
                    constraint_name = f"{label}_{prop}_{constraint_type}"
                    
                    # 제약 조건 생성 쿼리
                    if constraint_type == "unique":
                        query = f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
                    elif constraint_type == "exists":
                        query = f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS NOT NULL"
                    else:
                        logger.warning(f"지원되지 않는 제약 조건 유형: {constraint_type}")
                        continue
                    
                    try:
                        session.run(query)
                        logger.info(f"제약 조건 생성: {constraint_name}")
                    
                    except Exception as e:
                        logger.warning(f"제약 조건 생성 중 오류 발생: {constraint_name}, {str(e)}")
    
    def drop_schema(self) -> bool:
        """
        Neo4j 데이터베이스 스키마를 삭제합니다.
        
        Returns:
            스키마 삭제 성공 여부
        """
        try:
            if not self.driver:
                if not self.connect():
                    return False
            
            # 제약 조건 삭제
            self._drop_constraints()
            
            # 인덱스 삭제
            self._drop_indexes()
            
            logger.info("Neo4j 데이터베이스 스키마 삭제 완료")
            return True
        
        except Exception as e:
            logger.error(f"Neo4j 데이터베이스 스키마 삭제 중 오류 발생: {str(e)}")
            return False
    
    def _drop_constraints(self):
        """
        제약 조건을 삭제합니다.
        """
        with self.driver.session() as session:
            # 모든 제약 조건 조회
            result = session.run("SHOW CONSTRAINTS")
            
            for record in result:
                constraint_name = record.get("name", "")
                
                if constraint_name:
                    # 제약 조건 삭제 쿼리
                    query = f"DROP CONSTRAINT {constraint_name} IF EXISTS"
                    
                    try:
                        session.run(query)
                        logger.info(f"제약 조건 삭제: {constraint_name}")
                    
                    except Exception as e:
                        logger.warning(f"제약 조건 삭제 중 오류 발생: {constraint_name}, {str(e)}")
    
    def _drop_indexes(self):
        """
        인덱스를 삭제합니다.
        """
        with self.driver.session() as session:
            # 모든 인덱스 조회
            result = session.run("SHOW INDEXES")
            
            for record in result:
                index_name = record.get("name", "")
                
                if index_name:
                    # 인덱스 삭제 쿼리
                    query = f"DROP INDEX {index_name} IF EXISTS"
                    
                    try:
                        session.run(query)
                        logger.info(f"인덱스 삭제: {index_name}")
                    
                    except Exception as e:
                        logger.warning(f"인덱스 삭제 중 오류 발생: {index_name}, {str(e)}")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Neo4j 데이터베이스 스키마 정보를 반환합니다.
        
        Returns:
            스키마 정보
        """
        try:
            if not self.driver:
                if not self.connect():
                    return {}
            
            schema_info = {
                "node_labels": {},
                "relationship_types": {},
                "indexes": [],
                "constraints": []
            }
            
            with self.driver.session() as session:
                # 노드 레이블 조회
                result = session.run("CALL db.labels()")
                for record in result:
                    label = record["label"]
                    schema_info["node_labels"][label] = self.NODE_LABELS.get(label, "")
                
                # 관계 타입 조회
                result = session.run("CALL db.relationshipTypes()")
                for record in result:
                    rel_type = record["relationshipType"]
                    schema_info["relationship_types"][rel_type] = self.RELATIONSHIP_TYPES.get(rel_type, "")
                
                # 인덱스 조회
                result = session.run("SHOW INDEXES")
                for record in result:
                    index_info = {
                        "name": record.get("name", ""),
                        "type": record.get("type", ""),
                        "labelsOrTypes": record.get("labelsOrTypes", []),
                        "properties": record.get("properties", []),
                        "state": record.get("state", "")
                    }
                    schema_info["indexes"].append(index_info)
                
                # 제약 조건 조회
                result = session.run("SHOW CONSTRAINTS")
                for record in result:
                    constraint_info = {
                        "name": record.get("name", ""),
                        "type": record.get("type", ""),
                        "labelsOrTypes": record.get("labelsOrTypes", []),
                        "properties": record.get("properties", []),
                        "state": record.get("state", "")
                    }
                    schema_info["constraints"].append(constraint_info)
            
            return schema_info
        
        except Exception as e:
            logger.error(f"Neo4j 데이터베이스 스키마 정보 조회 중 오류 발생: {str(e)}")
            return {}
    
    def export_schema_definition(self, file_path: str) -> bool:
        """
        Neo4j 데이터베이스 스키마 정의를 파일로 내보냅니다.
        
        Args:
            file_path: 저장할 파일 경로
            
        Returns:
            내보내기 성공 여부
        """
        try:
            schema_definition = {
                "node_labels": self.NODE_LABELS,
                "relationship_types": self.RELATIONSHIP_TYPES,
                "indexes": self.INDEXES,
                "constraints": self.CONSTRAINTS
            }
            
            with open(file_path, "w") as f:
                json.dump(schema_definition, f, indent=2)
            
            logger.info(f"Neo4j 데이터베이스 스키마 정의가 내보내기되었습니다: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Neo4j 데이터베이스 스키마 정의 내보내기 중 오류 발생: {str(e)}")
            return False
    
    def import_schema_definition(self, file_path: str) -> bool:
        """
        Neo4j 데이터베이스 스키마 정의를 파일에서 가져옵니다.
        
        Args:
            file_path: 가져올 파일 경로
            
        Returns:
            가져오기 성공 여부
        """
        try:
            with open(file_path, "r") as f:
                schema_definition = json.load(f)
            
            # 스키마 정의 업데이트
            if "node_labels" in schema_definition:
                self.NODE_LABELS.update(schema_definition["node_labels"])
            
            if "relationship_types" in schema_definition:
                self.RELATIONSHIP_TYPES.update(schema_definition["relationship_types"])
            
            if "indexes" in schema_definition:
                self.INDEXES.update(schema_definition["indexes"])
            
            if "constraints" in schema_definition:
                self.CONSTRAINTS.update(schema_definition["constraints"])
            
            logger.info(f"Neo4j 데이터베이스 스키마 정의가 가져오기되었습니다: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Neo4j 데이터베이스 스키마 정의 가져오기 중 오류 발생: {str(e)}")
            return False
