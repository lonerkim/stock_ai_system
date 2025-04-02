#!/bin/bash
# 컨테이너 간 네트워크 설정 스크립트

# 스크립트 실행 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 네트워크 생성
create_network() {
  echo "Creating Docker network for stock-market-ai services..."
  
  # 기존 네트워크 확인
  NETWORK_EXISTS=$(docker network ls | grep stock-market-network | wc -l)
  
  if [ "$NETWORK_EXISTS" -eq "0" ]; then
    docker network create stock-market-network
    echo "Docker network 'stock-market-network' created successfully."
  else
    echo "Docker network 'stock-market-network' already exists."
  fi
}

# 네트워크 설정 검증
validate_network() {
  echo "Validating network configuration..."
  
  # 네트워크 존재 확인
  NETWORK_EXISTS=$(docker network ls | grep stock-market-network | wc -l)
  
  if [ "$NETWORK_EXISTS" -eq "0" ]; then
    echo "ERROR: Docker network 'stock-market-network' does not exist."
    echo "Please run this script with the 'create' option first."
    exit 1
  fi
  
  echo "Network configuration validation completed successfully."
}

# 네트워크 정보 표시
show_network_info() {
  echo "Displaying network information..."
  
  # 네트워크 존재 확인
  NETWORK_EXISTS=$(docker network ls | grep stock-market-network | wc -l)
  
  if [ "$NETWORK_EXISTS" -eq "0" ]; then
    echo "ERROR: Docker network 'stock-market-network' does not exist."
    echo "Please run this script with the 'create' option first."
    exit 1
  fi
  
  # 네트워크 정보 표시
  docker network inspect stock-market-network
}

# 컨테이너 연결 상태 확인
check_connections() {
  echo "Checking container connections..."
  
  # 실행 중인 컨테이너 확인
  RUNNING_CONTAINERS=$(docker ps --filter "network=stock-market-network" --format "{{.Names}}")
  
  if [ -z "$RUNNING_CONTAINERS" ]; then
    echo "No containers running on 'stock-market-network'."
    exit 0
  fi
  
  echo "Containers connected to 'stock-market-network':"
  echo "$RUNNING_CONTAINERS"
  
  # 각 컨테이너의 네트워크 연결 확인
  for CONTAINER in $RUNNING_CONTAINERS; do
    echo "Checking network connectivity for $CONTAINER..."
    
    # 다른 컨테이너에 대한 연결 테스트
    for TARGET in $RUNNING_CONTAINERS; do
      if [ "$CONTAINER" != "$TARGET" ]; then
        echo "Testing connection from $CONTAINER to $TARGET..."
        docker exec $CONTAINER ping -c 1 $TARGET > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
          echo "  ✅ Connection successful"
        else
          echo "  ❌ Connection failed"
        fi
      fi
    done
  done
}

# 메인 함수
main() {
  case "$1" in
    create)
      create_network
      ;;
    validate)
      validate_network
      ;;
    info)
      show_network_info
      ;;
    check)
      check_connections
      ;;
    *)
      echo "Usage: $0 {create|validate|info|check}"
      echo "  create: Create Docker network for services"
      echo "  validate: Validate network configuration"
      echo "  info: Display network information"
      echo "  check: Check container connections"
      exit 1
      ;;
  esac
}

# 스크립트 실행
main "$@"
