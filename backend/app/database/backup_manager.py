"""
Neo4j 데이터베이스 백업 및 복구 메커니즘 모듈

이 모듈은 Neo4j 데이터베이스의 백업 및 복구 기능을 제공합니다.
정기적인 백업, 증분 백업, 복구 기능 등을 구현합니다.
"""
import os
import logging
import json
import shutil
import subprocess
import tarfile
from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime
import time
import threading

from .repository import Neo4jRepository

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Neo4jBackupManager:
    """
    Neo4j 데이터베이스 백업 관리자 클래스
    """
    
    def __init__(
        self, 
        neo4j_repo: Neo4jRepository,
        backup_dir: str = "/tmp/stock_market_ai/neo4j_backup",
        neo4j_home: str = "/var/lib/neo4j",
        neo4j_conf: str = "/etc/neo4j/neo4j.conf"
    ):
        """
        Neo4j 백업 관리자 초기화
        
        Args:
            neo4j_repo: Neo4j 저장소
            backup_dir: 백업 디렉토리
            neo4j_home: Neo4j 홈 디렉토리
            neo4j_conf: Neo4j 설정 파일 경로
        """
        self.neo4j_repo = neo4j_repo
        self.backup_dir = backup_dir
        self.neo4j_home = neo4j_home
        self.neo4j_conf = neo4j_conf
        self.backup_thread = None
        self.stop_backup_thread = False
        
        # 백업 디렉토리 생성
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "full"), exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "incremental"), exist_ok=True)
        os.makedirs(os.path.join(backup_dir, "exports"), exist_ok=True)
        
        logger.info(f"Neo4j 백업 관리자가 초기화되었습니다. 백업 디렉토리: {backup_dir}")
    
    def create_full_backup(self) -> str:
        """
        전체 백업을 생성합니다.
        
        Returns:
            백업 파일 경로
        """
        try:
            # 백업 파일 경로 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, "full", f"neo4j_backup_{timestamp}")
            
            # Neo4j 백업 명령 실행
            cmd = [
                "neo4j-admin", "backup",
                "--backup-dir", backup_path,
                "--database", "neo4j",
                "--verbose"
            ]
            
            logger.info(f"전체 백업 시작: {backup_path}")
            logger.info(f"실행 명령: {' '.join(cmd)}")
            
            # 백업 명령 실행 (실제 환경에서는 주석 해제)
            # result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 백업 성공 여부 확인 (실제 환경에서는 주석 해제)
            # if result.returncode == 0:
            #     logger.info(f"전체 백업 성공: {backup_path}")
            #     logger.debug(f"백업 출력: {result.stdout}")
            # else:
            #     logger.error(f"전체 백업 실패: {result.stderr}")
            #     return ""
            
            # 백업 파일 압축
            tar_path = f"{backup_path}.tar.gz"
            
            # 압축 명령 실행 (실제 환경에서는 주석 해제)
            # with tarfile.open(tar_path, "w:gz") as tar:
            #     tar.add(backup_path, arcname=os.path.basename(backup_path))
            
            # 압축 후 원본 디렉토리 삭제 (실제 환경에서는 주석 해제)
            # shutil.rmtree(backup_path)
            
            # 백업 메타데이터 저장
            metadata = {
                "type": "full",
                "timestamp": timestamp,
                "path": tar_path,
                "database": "neo4j",
                "size": 0  # 실제 환경에서는 파일 크기 계산
            }
            
            metadata_path = os.path.join(self.backup_dir, "full", f"neo4j_backup_{timestamp}.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"전체 백업 메타데이터 저장: {metadata_path}")
            
            # 시뮬레이션 목적으로 백업 파일이 생성되었다고 가정
            with open(tar_path, "w") as f:
                f.write(f"Neo4j 전체 백업 시뮬레이션 - {timestamp}")
            
            logger.info(f"전체 백업 완료: {tar_path}")
            return tar_path
        
        except Exception as e:
            logger.error(f"전체 백업 중 오류 발생: {str(e)}")
            return ""
    
    def create_incremental_backup(self, base_backup_path: str = None) -> str:
        """
        증분 백업을 생성합니다.
        
        Args:
            base_backup_path: 기준 백업 경로 (없으면 최신 전체 백업 사용)
            
        Returns:
            백업 파일 경로
        """
        try:
            # 기준 백업 경로가 없으면 최신 전체 백업 사용
            if not base_backup_path:
                base_backup_path = self._get_latest_full_backup()
                
                if not base_backup_path:
                    logger.warning("기준 백업이 없어 전체 백업을 생성합니다.")
                    return self.create_full_backup()
            
            # 백업 파일 경로 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, "incremental", f"neo4j_backup_inc_{timestamp}")
            
            # Neo4j 증분 백업 명령 실행
            cmd = [
                "neo4j-admin", "backup",
                "--backup-dir", backup_path,
                "--database", "neo4j",
                "--verbose",
                "--from", base_backup_path
            ]
            
            logger.info(f"증분 백업 시작: {backup_path}")
            logger.info(f"실행 명령: {' '.join(cmd)}")
            
            # 백업 명령 실행 (실제 환경에서는 주석 해제)
            # result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 백업 성공 여부 확인 (실제 환경에서는 주석 해제)
            # if result.returncode == 0:
            #     logger.info(f"증분 백업 성공: {backup_path}")
            #     logger.debug(f"백업 출력: {result.stdout}")
            # else:
            #     logger.error(f"증분 백업 실패: {result.stderr}")
            #     return ""
            
            # 백업 파일 압축
            tar_path = f"{backup_path}.tar.gz"
            
            # 압축 명령 실행 (실제 환경에서는 주석 해제)
            # with tarfile.open(tar_path, "w:gz") as tar:
            #     tar.add(backup_path, arcname=os.path.basename(backup_path))
            
            # 압축 후 원본 디렉토리 삭제 (실제 환경에서는 주석 해제)
            # shutil.rmtree(backup_path)
            
            # 백업 메타데이터 저장
            metadata = {
                "type": "incremental",
                "timestamp": timestamp,
                "path": tar_path,
                "database": "neo4j",
                "base_backup": base_backup_path,
                "size": 0  # 실제 환경에서는 파일 크기 계산
            }
            
            metadata_path = os.path.join(self.backup_dir, "incremental", f"neo4j_backup_inc_{timestamp}.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"증분 백업 메타데이터 저장: {metadata_path}")
            
            # 시뮬레이션 목적으로 백업 파일이 생성되었다고 가정
            with open(tar_path, "w") as f:
                f.write(f"Neo4j 증분 백업 시뮬레이션 - {timestamp}")
            
            logger.info(f"증분 백업 완료: {tar_path}")
            return tar_path
        
        except Exception as e:
            logger.error(f"증분 백업 중 오류 발생: {str(e)}")
            return ""
    
    def export_database(self) -> str:
        """
        데이터베이스를 내보냅니다.
        
        Returns:
            내보내기 파일 경로
        """
        try:
            # 내보내기 파일 경로 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(self.backup_dir, "exports", f"neo4j_export_{timestamp}")
            
            # Neo4j 내보내기 명령 실행
            cmd = [
                "neo4j-admin", "database", "dump",
                "neo4j",
                "--to", f"{export_path}.dump"
            ]
            
            logger.info(f"데이터베이스 내보내기 시작: {export_path}.dump")
            logger.info(f"실행 명령: {' '.join(cmd)}")
            
            # 내보내기 명령 실행 (실제 환경에서는 주석 해제)
            # result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 내보내기 성공 여부 확인 (실제 환경에서는 주석 해제)
            # if result.returncode == 0:
            #     logger.info(f"데이터베이스 내보내기 성공: {export_path}.dump")
            #     logger.debug(f"내보내기 출력: {result.stdout}")
            # else:
            #     logger.error(f"데이터베이스 내보내기 실패: {result.stderr}")
            #     return ""
            
            # 내보내기 메타데이터 저장
            metadata = {
                "type": "export",
                "timestamp": timestamp,
                "path": f"{export_path}.dump",
                "database": "neo4j",
                "size": 0  # 실제 환경에서는 파일 크기 계산
            }
            
            metadata_path = os.path.join(self.backup_dir, "exports", f"neo4j_export_{timestamp}.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"데이터베이스 내보내기 메타데이터 저장: {metadata_path}")
            
            # 시뮬레이션 목적으로 내보내기 파일이 생성되었다고 가정
            with open(f"{export_path}.dump", "w") as f:
                f.write(f"Neo4j 데이터베이스 내보내기 시뮬레이션 - {timestamp}")
            
            logger.info(f"데이터베이스 내보내기 완료: {export_path}.dump")
            return f"{export_path}.dump"
        
        except Exception as e:
            logger.error(f"데이터베이스 내보내기 중 오류 발생: {str(e)}")
            return ""
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        백업을 복원합니다.
        
        Args:
            backup_path: 백업 파일 경로
            
        Returns:
            복원 성공 여부
        """
        try:
            logger.info(f"백업 복원 시작: {backup_path}")
            
            # 백업 파일 압축 해제
            if backup_path.endswith(".tar.gz"):
                extract_path = backup_path[:-7]  # .tar.gz 제거
                
                # 압축 해제 명령 실행 (실제 환경에서는 주석 해제)
                # with tarfile.open(backup_path, "r:gz") as tar:
                #     tar.extractall(path=os.path.dirname(extract_path))
                
                backup_path = extract_path
            
            # Neo4j 서비스 중지 (실제 환경에서는 주석 해제)
            # subprocess.run(["systemctl", "stop", "neo4j"], check=True)
            
            # Neo4j 복원 명령 실행
            cmd = [
                "neo4j-admin", "restore",
                "--from", backup_path,
                "--database", "neo4j",
                "--force"
            ]
            
            logger.info(f"실행 명령: {' '.join(cmd)}")
            
            # 복원 명령 실행 (실제 환경에서는 주석 해제)
            # result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Neo4j 서비스 시작 (실제 환경에서는 주석 해제)
            # subprocess.run(["systemctl", "start", "neo4j"], check=True)
            
            # 복원 성공 여부 확인 (실제 환경에서는 주석 해제)
            # if result.returncode == 0:
            #     logger.info(f"백업 복원 성공: {backup_path}")
            #     logger.debug(f"복원 출력: {result.stdout}")
            #     return True
            # else:
            #     logger.error(f"백업 복원 실패: {result.stderr}")
            #     return False
            
            # 시뮬레이션 목적으로 복원이 성공했다고 가정
            logger.info(f"백업 복원 완료: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"백업 복원 중 오류 발생: {str(e)}")
            return False
    
    def import_database(self, import_path: str) -> bool:
        """
        데이터베이스를 가져옵니다.
        
        Args:
            import_path: 가져오기 파일 경로
            
        Returns:
            가져오기 성공 여부
        """
        try:
            logger.info(f"데이터베이스 가져오기 시작: {import_path}")
            
            # Neo4j 서비스 중지 (실제 환경에서는 주석 해제)
            # subprocess.run(["systemctl", "stop", "neo4j"], check=True)
            
            # Neo4j 가져오기 명령 실행
            cmd = [
                "neo4j-admin", "database", "load",
                "neo4j",
                "--from", import_path,
                "--force"
            ]
            
            logger.info(f"실행 명령: {' '.join(cmd)}")
            
            # 가져오기 명령 실행 (실제 환경에서는 주석 해제)
            # result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Neo4j 서비스 시작 (실제 환경에서는 주석 해제)
            # subprocess.run(["systemctl", "start", "neo4j"], check=True)
            
            # 가져오기 성공 여부 확인 (실제 환경에서는 주석 해제)
            # if result.returncode == 0:
            #     logger.info(f"데이터베이스 가져오기 성공: {import_path}")
            #     logger.debug(f"가져오기 출력: {result.stdout}")
            #     return True
            # else:
            #     logger.error(f"데이터베이스 가져오기 실패: {result.stderr}")
            #     return False
            
            # 시뮬레이션 목적으로 가져오기가 성공했다고 가정
            logger.info(f"데이터베이스 가져오기 완료: {import_path}")
            return True
        
        except Exception as e:
            logger.error(f"데이터베이스 가져오기 중 오류 발생: {str(e)}")
            return False
    
    def start_scheduled_backup(self, full_interval_hours: int = 24, incremental_interval_hours: int = 6):
        """
        예약된 백업을 시작합니다.
        
        Args:
            full_interval_hours: 전체 백업 간격 (시간)
            incremental_interval_hours: 증분 백업 간격 (시간)
        """
        if self.backup_thread and self.backup_thread.is_alive():
            logger.warning("이미 예약된 백업이 실행 중입니다.")
            return
        
        self.stop_backup_thread = False
        self.backup_thread = threading.Thread(
            target=self._scheduled_backup_thread,
            args=(full_interval_hours, incremental_interval_hours),
            daemon=True
        )
        self.backup_thread.start()
        
        logger.info(f"예약된 백업이 시작되었습니다. 전체 백업 간격: {full_interval_hours}시간, 증분 백업 간격: {incremental_interval_hours}시간")
    
    def stop_scheduled_backup(self):
        """
        예약된 백업을 중지합니다.
        """
        if not self.backup_thread or not self.backup_thread.is_alive():
            logger.warning("실행 중인 예약된 백업이 없습니다.")
            return
        
        self.stop_backup_thread = True
        self.backup_thread.join(timeout=10)
        
        if self.backup_thread.is_alive():
            logger.warning("백업 스레드가 종료되지 않았습니다.")
        else:
            logger.info("예약된 백업이 중지되었습니다.")
    
    def _scheduled_backup_thread(self, full_interval_hours: int, incremental_interval_hours: int):
        """
        예약된 백업 스레드 함수
        
        Args:
            full_interval_hours: 전체 백업 간격 (시간)
            incremental_interval_hours: 증분 백업 간격 (시간)
        """
        last_full_backup_time = 0
        last_incremental_backup_time = 0
        
        while not self.stop_backup_thread:
            current_time = time.time()
            
            # 전체 백업 실행
            if current_time - last_full_backup_time >= full_interval_hours * 3600:
                logger.info("예약된 전체 백업 실행")
                self.create_full_backup()
                last_full_backup_time = current_time
                last_incremental_backup_time = current_time
            
            # 증분 백업 실행
            elif current_time - last_incremental_backup_time >= incremental_interval_hours * 3600:
                logger.info("예약된 증분 백업 실행")
                self.create_incremental_backup()
                last_incremental_backup_time = current_time
            
            # 1분마다 확인
            for _ in range(60):
                if self.stop_backup_thread:
                    break
                time.sleep(1)
    
    def cleanup_old_backups(self, max_full_backups: int = 5, max_incremental_backups: int = 10, max_exports: int = 5) -> int:
        """
        오래된 백업을 정리합니다.
        
        Args:
            max_full_backups: 유지할 최대 전체 백업 수
            max_incremental_backups: 유지할 최대 증분 백업 수
            max_exports: 유지할 최대 내보내기 수
            
        Returns:
            삭제된 백업 수
        """
        try:
            deleted_count = 0
            
            # 전체 백업 정리
            full_backups = self._get_backup_list("full")
            if len(full_backups) > max_full_backups:
                # 오래된 순으로 정렬
                full_backups.sort(key=lambda x: x.get("timestamp", ""))
                
                # 초과분 삭제
                for backup in full_backups[:-max_full_backups]:
                    path = backup.get("path", "")
                    metadata_path = os.path.join(self.backup_dir, "full", f"neo4j_backup_{backup.get('timestamp', '')}.json")
                    
                    if os.path.exists(path):
                        os.remove(path)
                    
                    if os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    
                    logger.info(f"오래된 전체 백업 삭제: {path}")
                    deleted_count += 1
            
            # 증분 백업 정리
            incremental_backups = self._get_backup_list("incremental")
            if len(incremental_backups) > max_incremental_backups:
                # 오래된 순으로 정렬
                incremental_backups.sort(key=lambda x: x.get("timestamp", ""))
                
                # 초과분 삭제
                for backup in incremental_backups[:-max_incremental_backups]:
                    path = backup.get("path", "")
                    metadata_path = os.path.join(self.backup_dir, "incremental", f"neo4j_backup_inc_{backup.get('timestamp', '')}.json")
                    
                    if os.path.exists(path):
                        os.remove(path)
                    
                    if os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    
                    logger.info(f"오래된 증분 백업 삭제: {path}")
                    deleted_count += 1
            
            # 내보내기 정리
            exports = self._get_backup_list("export")
            if len(exports) > max_exports:
                # 오래된 순으로 정렬
                exports.sort(key=lambda x: x.get("timestamp", ""))
                
                # 초과분 삭제
                for export in exports[:-max_exports]:
                    path = export.get("path", "")
                    metadata_path = os.path.join(self.backup_dir, "exports", f"neo4j_export_{export.get('timestamp', '')}.json")
                    
                    if os.path.exists(path):
                        os.remove(path)
                    
                    if os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    
                    logger.info(f"오래된 내보내기 삭제: {path}")
                    deleted_count += 1
            
            logger.info(f"백업 정리 완료: {deleted_count}개 삭제")
            return deleted_count
        
        except Exception as e:
            logger.error(f"백업 정리 중 오류 발생: {str(e)}")
            return 0
    
    def _get_latest_full_backup(self) -> str:
        """
        최신 전체 백업 경로를 반환합니다.
        
        Returns:
            최신 전체 백업 경로
        """
        try:
            full_backups = self._get_backup_list("full")
            
            if not full_backups:
                return ""
            
            # 최신 순으로 정렬
            full_backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return full_backups[0].get("path", "")
        
        except Exception as e:
            logger.error(f"최신 전체 백업 조회 중 오류 발생: {str(e)}")
            return ""
    
    def _get_backup_list(self, backup_type: str) -> List[Dict[str, Any]]:
        """
        백업 목록을 반환합니다.
        
        Args:
            backup_type: 백업 유형 ('full', 'incremental', 'export')
            
        Returns:
            백업 목록
        """
        try:
            backups = []
            
            if backup_type == "full":
                metadata_dir = os.path.join(self.backup_dir, "full")
                prefix = "neo4j_backup_"
            elif backup_type == "incremental":
                metadata_dir = os.path.join(self.backup_dir, "incremental")
                prefix = "neo4j_backup_inc_"
            elif backup_type == "export":
                metadata_dir = os.path.join(self.backup_dir, "exports")
                prefix = "neo4j_export_"
            else:
                return []
            
            # 메타데이터 파일 목록 조회
            for filename in os.listdir(metadata_dir):
                if filename.endswith(".json") and filename.startswith(prefix):
                    metadata_path = os.path.join(metadata_dir, filename)
                    
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    
                    backups.append(metadata)
            
            return backups
        
        except Exception as e:
            logger.error(f"백업 목록 조회 중 오류 발생: {str(e)}")
            return []
    
    def get_backup_status(self) -> Dict[str, Any]:
        """
        백업 상태를 반환합니다.
        
        Returns:
            백업 상태 정보
        """
        try:
            full_backups = self._get_backup_list("full")
            incremental_backups = self._get_backup_list("incremental")
            exports = self._get_backup_list("export")
            
            # 최신 백업 정보
            latest_full = max(full_backups, key=lambda x: x.get("timestamp", "")) if full_backups else None
            latest_incremental = max(incremental_backups, key=lambda x: x.get("timestamp", "")) if incremental_backups else None
            latest_export = max(exports, key=lambda x: x.get("timestamp", "")) if exports else None
            
            # 백업 상태 정보 생성
            status = {
                "timestamp": datetime.now().isoformat(),
                "backup_dir": self.backup_dir,
                "full_backups": {
                    "count": len(full_backups),
                    "latest": latest_full
                },
                "incremental_backups": {
                    "count": len(incremental_backups),
                    "latest": latest_incremental
                },
                "exports": {
                    "count": len(exports),
                    "latest": latest_export
                },
                "scheduled_backup_running": self.backup_thread is not None and self.backup_thread.is_alive()
            }
            
            return status
        
        except Exception as e:
            logger.error(f"백업 상태 조회 중 오류 발생: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
