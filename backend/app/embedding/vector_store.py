"""
벡터 저장소 모듈

이 모듈은 임베딩 벡터를 저장하고 검색하는 기능을 제공합니다.
로컬 파일 기반 저장소와 Neo4j 그래프 데이터베이스 기반 저장소를 지원합니다.
"""
import os
import logging
import numpy as np
import json
import pickle
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
import uuid
from abc import ABC, abstractmethod
import faiss

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseVectorStore(ABC):
    """
    벡터 저장소의 기본 추상 클래스
    """
    
    @abstractmethod
    def add_vectors(self, vectors: List[np.ndarray], metadata: List[Dict[str, Any]]) -> List[str]:
        """
        벡터와 메타데이터를 저장소에 추가합니다.
        
        Args:
            vectors: 추가할 벡터 목록
            metadata: 각 벡터에 대한 메타데이터 목록
            
        Returns:
            추가된 벡터의 ID 목록
        """
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리 벡터와 가장 유사한 벡터를 검색합니다.
        
        Args:
            query_vector: 쿼리 벡터
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 목록 (벡터 ID, 유사도 점수, 메타데이터 포함)
        """
        pass
    
    @abstractmethod
    def delete_vector(self, vector_id: str) -> bool:
        """
        벡터를 저장소에서 삭제합니다.
        
        Args:
            vector_id: 삭제할 벡터의 ID
            
        Returns:
            삭제 성공 여부
        """
        pass
    
    @abstractmethod
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 벡터를 조회합니다.
        
        Args:
            vector_id: 조회할 벡터의 ID
            
        Returns:
            벡터 정보 (벡터, 메타데이터 포함) 또는 None
        """
        pass


class FaissVectorStore(BaseVectorStore):
    """
    FAISS 기반 로컬 벡터 저장소
    """
    
    def __init__(self, dimension: int, index_type: str = "Flat", store_dir: str = "/tmp/vector_store"):
        """
        FAISS 벡터 저장소 초기화
        
        Args:
            dimension: 벡터 차원
            index_type: FAISS 인덱스 유형 ('Flat', 'IVF', 'HNSW' 등)
            store_dir: 저장소 디렉토리 경로
        """
        self.dimension = dimension
        self.index_type = index_type
        self.store_dir = store_dir
        
        # 저장소 디렉토리 생성
        os.makedirs(store_dir, exist_ok=True)
        
        # 메타데이터 및 ID 매핑 저장 경로
        self.metadata_path = os.path.join(store_dir, "metadata.json")
        self.id_map_path = os.path.join(store_dir, "id_map.pickle")
        
        # FAISS 인덱스 생성
        if index_type == "Flat":
            self.index = faiss.IndexFlatL2(dimension)
        elif index_type == "IVF":
            quantizer = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIVFFlat(quantizer, dimension, 100)
            self.index.train(np.random.random((1000, dimension)).astype(np.float32))
        elif index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(dimension, 32)
        else:
            logger.warning(f"지원되지 않는 인덱스 유형: {index_type}, Flat 인덱스를 사용합니다.")
            self.index = faiss.IndexFlatL2(dimension)
        
        # 메타데이터 및 ID 매핑 로드 또는 초기화
        self.metadata = self._load_metadata()
        self.id_to_index = self._load_id_map()
        
        logger.info(f"FAISS 벡터 저장소가 초기화되었습니다. 차원: {dimension}, 인덱스 유형: {index_type}")
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        메타데이터를 로드합니다.
        
        Returns:
            메타데이터 딕셔너리
        """
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"메타데이터 로드 중 오류 발생: {str(e)}, 새 메타데이터를 초기화합니다.")
        
        return {}
    
    def _save_metadata(self):
        """
        메타데이터를 저장합니다.
        """
        try:
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            logger.error(f"메타데이터 저장 중 오류 발생: {str(e)}")
    
    def _load_id_map(self) -> Dict[str, int]:
        """
        ID 매핑을 로드합니다.
        
        Returns:
            ID 매핑 딕셔너리
        """
        if os.path.exists(self.id_map_path):
            try:
                with open(self.id_map_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"ID 매핑 로드 중 오류 발생: {str(e)}, 새 ID 매핑을 초기화합니다.")
        
        return {}
    
    def _save_id_map(self):
        """
        ID 매핑을 저장합니다.
        """
        try:
            with open(self.id_map_path, 'wb') as f:
                pickle.dump(self.id_to_index, f)
        except Exception as e:
            logger.error(f"ID 매핑 저장 중 오류 발생: {str(e)}")
    
    def add_vectors(self, vectors: List[np.ndarray], metadata: List[Dict[str, Any]]) -> List[str]:
        """
        벡터와 메타데이터를 저장소에 추가합니다.
        
        Args:
            vectors: 추가할 벡터 목록
            metadata: 각 벡터에 대한 메타데이터 목록
            
        Returns:
            추가된 벡터의 ID 목록
        """
        try:
            if len(vectors) != len(metadata):
                raise ValueError("벡터와 메타데이터의 수가 일치하지 않습니다.")
            
            # 벡터 ID 생성
            vector_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            # 벡터 배열 생성
            vectors_array = np.vstack([v.astype(np.float32) for v in vectors])
            
            # 현재 인덱스 크기 확인
            start_idx = self.index.ntotal
            
            # FAISS 인덱스에 벡터 추가
            self.index.add(vectors_array)
            
            # ID 매핑 및 메타데이터 업데이트
            for i, vector_id in enumerate(vector_ids):
                idx = start_idx + i
                self.id_to_index[vector_id] = idx
                
                # 메타데이터에 타임스탬프 추가
                meta = metadata[i].copy()
                meta["timestamp"] = datetime.now().isoformat()
                self.metadata[vector_id] = meta
            
            # 메타데이터 및 ID 매핑 저장
            self._save_metadata()
            self._save_id_map()
            
            logger.info(f"{len(vectors)} 개의 벡터가 저장소에 추가되었습니다.")
            return vector_ids
        
        except Exception as e:
            logger.error(f"벡터 추가 중 오류 발생: {str(e)}")
            raise
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리 벡터와 가장 유사한 벡터를 검색합니다.
        
        Args:
            query_vector: 쿼리 벡터
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 목록 (벡터 ID, 유사도 점수, 메타데이터 포함)
        """
        try:
            # 쿼리 벡터 형태 조정
            query_vector = query_vector.astype(np.float32).reshape(1, -1)
            
            # FAISS 검색 수행
            distances, indices = self.index.search(query_vector, top_k)
            
            # 결과 변환
            results = []
            index_to_id = {idx: id for id, idx in self.id_to_index.items()}
            
            for i, idx in enumerate(indices[0]):
                if idx < 0 or idx >= self.index.ntotal:
                    continue
                
                vector_id = index_to_id.get(idx)
                if not vector_id:
                    continue
                
                distance = distances[0][i]
                similarity = 1.0 / (1.0 + distance)  # L2 거리를 유사도 점수로 변환
                
                result = {
                    "id": vector_id,
                    "score": similarity,
                    "metadata": self.metadata.get(vector_id, {})
                }
                
                results.append(result)
            
            logger.info(f"검색 완료: {len(results)} 개의 결과를 찾았습니다.")
            return results
        
        except Exception as e:
            logger.error(f"벡터 검색 중 오류 발생: {str(e)}")
            raise
    
    def delete_vector(self, vector_id: str) -> bool:
        """
        벡터를 저장소에서 삭제합니다.
        
        Args:
            vector_id: 삭제할 벡터의 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            if vector_id not in self.id_to_index:
                logger.warning(f"벡터 ID {vector_id}를 찾을 수 없습니다.")
                return False
            
            # FAISS는 직접적인 삭제를 지원하지 않으므로, 인덱스를 재구성해야 함
            # 현재 구현에서는 메타데이터에서만 삭제하고 실제 인덱스는 유지
            # 실제 프로덕션 환경에서는 주기적으로 인덱스를 재구성하는 로직 필요
            
            # 메타데이터에서 삭제
            if vector_id in self.metadata:
                del self.metadata[vector_id]
            
            # ID 매핑에서 삭제
            if vector_id in self.id_to_index:
                del self.id_to_index[vector_id]
            
            # 메타데이터 및 ID 매핑 저장
            self._save_metadata()
            self._save_id_map()
            
            logger.info(f"벡터 ID {vector_id}가 삭제되었습니다.")
            return True
        
        except Exception as e:
            logger.error(f"벡터 삭제 중 오류 발생: {str(e)}")
            return False
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 벡터를 조회합니다.
        
        Args:
            vector_id: 조회할 벡터의 ID
            
        Returns:
            벡터 정보 (벡터, 메타데이터 포함) 또는 None
        """
        try:
            if vector_id not in self.id_to_index:
                logger.warning(f"벡터 ID {vector_id}를 찾을 수 없습니다.")
                return None
            
            idx = self.id_to_index[vector_id]
            
            # FAISS에서는 인덱스로 직접 벡터를 조회할 수 없으므로,
            # 실제 프로덕션 환경에서는 벡터를 별도로 저장하는 로직 필요
            # 현재 구현에서는 메타데이터만 반환
            
            metadata = self.metadata.get(vector_id, {})
            
            return {
                "id": vector_id,
                "metadata": metadata
            }
        
        except Exception as e:
            logger.error(f"벡터 조회 중 오류 발생: {str(e)}")
            return None


class Neo4jVectorStore(BaseVectorStore):
    """
    Neo4j 그래프 데이터베이스 기반 벡터 저장소
    """
    
    def __init__(self, uri: str, username: str, password: str, dimension: int, index_name: str = "vector_index"):
        """
        Neo4j 벡터 저장소 초기화
        
        Args:
            uri: Neo4j 데이터베이스 URI
            username: Neo4j 사용자 이름
            password: Neo4j 비밀번호
            dimension: 벡터 차원
            index_name: 벡터 인덱스 이름
        """
        try:
            from neo4j import GraphDatabase
            
            self.uri = uri
            self.username = username
            self.password = password
            self.dimension = dimension
            self.index_name = index_name
            
            # Neo4j 드라이버 초기화
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            
            # 연결 테스트
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            # 벡터 인덱스 생성 (없는 경우)
            self._create_vector_index()
            
            logger.info(f"Neo4j 벡터 저장소가 초기화되었습니다. URI: {uri}, 차원: {dimension}")
        
        except ImportError:
            logger.error("neo4j 패키지가 설치되어 있지 않습니다. 'pip install neo4j'를 실행하세요.")
            raise
        except Exception as e:
            logger.error(f"Neo4j 벡터 저장소 초기화 중 오류 발생: {str(e)}")
            raise
    
    def _create_vector_index(self):
        """
        Neo4j에 벡터 인덱스를 생성합니다.
        """
        try:
            with self.driver.session() as session:
                # 노드 제약 조건 생성
                session.run("""
                    CREATE CONSTRAINT vector_id_unique IF NOT EXISTS
                    FOR (v:Vector) REQUIRE v.id IS UNIQUE
                """)
                
                # 벡터 인덱스 생성 (Neo4j 5.0 이상)
                session.run(f"""
                    CALL db.index.vector.createNodeIndex(
                        $index_name,
                        'Vector',
                        'embedding',
                        $dimension,
                        'cosine'
                    )
                """, index_name=self.index_name, dimension=self.dimension)
                
                logger.info(f"Neo4j 벡터 인덱스 '{self.index_name}'이(가) 생성되었습니다.")
        
        except Exception as e:
            # 이미 인덱스가 존재하는 경우 무시
            if "already exists" in str(e):
                logger.info(f"Neo4j 벡터 인덱스 '{self.index_name}'이(가) 이미 존재합니다.")
            else:
                logger.error(f"Neo4j 벡터 인덱스 생성 중 오류 발생: {str(e)}")
                raise
    
    def add_vectors(self, vectors: List[np.ndarray], metadata: List[Dict[str, Any]]) -> List[str]:
        """
        벡터와 메타데이터를 저장소에 추가합니다.
        
        Args:
            vectors: 추가할 벡터 목록
            metadata: 각 벡터에 대한 메타데이터 목록
            
        Returns:
            추가된 벡터의 ID 목록
        """
        try:
            if len(vectors) != len(metadata):
                raise ValueError("벡터와 메타데이터의 수가 일치하지 않습니다.")
            
            # 벡터 ID 생성
            vector_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
            with self.driver.session() as session:
                for i, (vector_id, vector, meta) in enumerate(zip(vector_ids, vectors, metadata)):
                    # 메타데이터에 타임스탬프 추가
                    meta = meta.copy()
                    meta["timestamp"] = datetime.now().isoformat()
                    
                    # 벡터 노드 생성
                    session.run("""
                        CREATE (v:Vector {
                            id: $id,
                            embedding: $embedding,
                            metadata: $metadata
                        })
                    """, id=vector_id, embedding=vector.tolist(), metadata=json.dumps(meta))
                    
                    # 메타데이터 기반 관계 생성 (예: 주식 심볼)
                    if "symbol" in meta:
                        symbol = meta["symbol"]
                        session.run("""
                            MERGE (s:Stock {symbol: $symbol})
                            WITH s
                            MATCH (v:Vector {id: $id})
                            CREATE (v)-[:ABOUT]->(s)
                        """, symbol=symbol, id=vector_id)
                    
                    # 메타데이터 기반 관계 생성 (예: 시장 유형)
                    if "market" in meta:
                        market = meta["market"]
                        session.run("""
                            MERGE (m:Market {name: $market})
                            WITH m
                            MATCH (v:Vector {id: $id})
                            CREATE (v)-[:BELONGS_TO]->(m)
                        """, market=market, id=vector_id)
            
            logger.info(f"{len(vectors)} 개의 벡터가 Neo4j 저장소에 추가되었습니다.")
            return vector_ids
        
        except Exception as e:
            logger.error(f"Neo4j 벡터 추가 중 오류 발생: {str(e)}")
            raise
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리 벡터와 가장 유사한 벡터를 검색합니다.
        
        Args:
            query_vector: 쿼리 벡터
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 목록 (벡터 ID, 유사도 점수, 메타데이터 포함)
        """
        try:
            results = []
            
            with self.driver.session() as session:
                # 벡터 유사도 검색
                records = session.run(f"""
                    CALL db.index.vector.queryNodes(
                        $index_name,
                        $top_k,
                        $query_vector
                    )
                    YIELD node, score
                    RETURN node.id AS id, score, node.metadata AS metadata
                """, index_name=self.index_name, top_k=top_k, query_vector=query_vector.tolist())
                
                for record in records:
                    metadata = json.loads(record["metadata"]) if record["metadata"] else {}
                    
                    result = {
                        "id": record["id"],
                        "score": record["score"],
                        "metadata": metadata
                    }
                    
                    results.append(result)
            
            logger.info(f"Neo4j 검색 완료: {len(results)} 개의 결과를 찾았습니다.")
            return results
        
        except Exception as e:
            logger.error(f"Neo4j 벡터 검색 중 오류 발생: {str(e)}")
            raise
    
    def delete_vector(self, vector_id: str) -> bool:
        """
        벡터를 저장소에서 삭제합니다.
        
        Args:
            vector_id: 삭제할 벡터의 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (v:Vector {id: $id})
                    DETACH DELETE v
                    RETURN count(v) AS deleted
                """, id=vector_id)
                
                deleted = result.single()["deleted"]
                
                if deleted > 0:
                    logger.info(f"벡터 ID {vector_id}가 Neo4j에서 삭제되었습니다.")
                    return True
                else:
                    logger.warning(f"벡터 ID {vector_id}를 Neo4j에서 찾을 수 없습니다.")
                    return False
        
        except Exception as e:
            logger.error(f"Neo4j 벡터 삭제 중 오류 발생: {str(e)}")
            return False
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 벡터를 조회합니다.
        
        Args:
            vector_id: 조회할 벡터의 ID
            
        Returns:
            벡터 정보 (벡터, 메타데이터 포함) 또는 None
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (v:Vector {id: $id})
                    RETURN v.id AS id, v.embedding AS embedding, v.metadata AS metadata
                """, id=vector_id)
                
                record = result.single()
                
                if not record:
                    logger.warning(f"벡터 ID {vector_id}를 Neo4j에서 찾을 수 없습니다.")
                    return None
                
                metadata = json.loads(record["metadata"]) if record["metadata"] else {}
                
                return {
                    "id": record["id"],
                    "vector": np.array(record["embedding"]),
                    "metadata": metadata
                }
        
        except Exception as e:
            logger.error(f"Neo4j 벡터 조회 중 오류 발생: {str(e)}")
            return None
    
    def close(self):
        """
        Neo4j 연결을 닫습니다.
        """
        if self.driver:
            self.driver.close()
            logger.info("Neo4j 연결이 닫혔습니다.")


class VectorStoreFactory:
    """
    벡터 저장소 팩토리 클래스
    """
    
    @staticmethod
    def create_vector_store(store_type: str, **kwargs) -> BaseVectorStore:
        """
        벡터 저장소를 생성합니다.
        
        Args:
            store_type: 저장소 유형 ('faiss', 'neo4j')
            **kwargs: 저장소별 추가 매개변수
            
        Returns:
            벡터 저장소 인스턴스
        """
        if store_type == "faiss":
            dimension = kwargs.get("dimension", 768)
            index_type = kwargs.get("index_type", "Flat")
            store_dir = kwargs.get("store_dir", "/tmp/vector_store")
            
            return FaissVectorStore(dimension=dimension, index_type=index_type, store_dir=store_dir)
        
        elif store_type == "neo4j":
            uri = kwargs.get("uri")
            username = kwargs.get("username")
            password = kwargs.get("password")
            dimension = kwargs.get("dimension", 768)
            index_name = kwargs.get("index_name", "vector_index")
            
            if not uri or not username or not password:
                raise ValueError("Neo4j 벡터 저장소에는 URI, 사용자 이름, 비밀번호가 필요합니다.")
            
            return Neo4jVectorStore(
                uri=uri,
                username=username,
                password=password,
                dimension=dimension,
                index_name=index_name
            )
        
        else:
            raise ValueError(f"지원되지 않는 저장소 유형: {store_type}")
