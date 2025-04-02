#!/bin/bash
# 환경 변수 및 설정 파일 관리 스크립트

# 스크립트 실행 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 환경 변수 파일 생성
create_env_file() {
  if [ ! -f "$PROJECT_ROOT/docker/.env" ]; then
    echo "Creating .env file from template..."
    cp "$PROJECT_ROOT/docker/.env.example" "$PROJECT_ROOT/docker/.env"
    echo ".env file created. Please edit it with your actual configuration values."
  else
    echo ".env file already exists."
  fi
}

# 필요한 디렉토리 생성
create_directories() {
  echo "Creating necessary directories..."
  mkdir -p "$PROJECT_ROOT/data"
  mkdir -p "$PROJECT_ROOT/logs"
  echo "Directories created."
}

# 설정 파일 검증
validate_config() {
  echo "Validating configuration..."
  
  # .env 파일 존재 확인
  if [ ! -f "$PROJECT_ROOT/docker/.env" ]; then
    echo "ERROR: .env file not found. Please run this script with the 'create-env' option first."
    exit 1
  fi
  
  # 필수 환경 변수 확인
  source "$PROJECT_ROOT/docker/.env"
  
  REQUIRED_VARS=(
    "NEO4J_USER"
    "NEO4J_PASSWORD"
  )
  
  MISSING_VARS=0
  for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ]; then
      echo "ERROR: Required variable $VAR is not set in .env file."
      MISSING_VARS=$((MISSING_VARS+1))
    fi
  done
  
  if [ $MISSING_VARS -gt 0 ]; then
    echo "Please update your .env file with the required variables."
    exit 1
  fi
  
  echo "Configuration validation completed successfully."
}

# 메인 함수
main() {
  case "$1" in
    create-env)
      create_env_file
      ;;
    create-dirs)
      create_directories
      ;;
    validate)
      validate_config
      ;;
    setup)
      create_env_file
      create_directories
      validate_config
      ;;
    *)
      echo "Usage: $0 {create-env|create-dirs|validate|setup}"
      echo "  create-env: Create .env file from template"
      echo "  create-dirs: Create necessary directories"
      echo "  validate: Validate configuration"
      echo "  setup: Perform all setup steps"
      exit 1
      ;;
  esac
}

# 스크립트 실행
main "$@"
