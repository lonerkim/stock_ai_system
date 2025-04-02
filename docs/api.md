# API 문서

이 문서는 주식 시장 AI 분석 시스템의 백엔드 API에 대한 상세 설명을 제공합니다.

## 기본 정보

- 기본 URL: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs` (Swagger UI)
- 대체 API 문서: `http://localhost:8000/redoc` (ReDoc)

## 인증

대부분의 API 엔드포인트는 인증이 필요합니다. 인증은 Bearer 토큰 방식을 사용합니다.

```
Authorization: Bearer {access_token}
```

## 엔드포인트

### 인증 관련

#### 로그인

```
POST /api/auth/login
```

요청 본문:
```json
{
  "username": "string",
  "password": "string"
}
```

응답:
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

### 시장 데이터

#### 시장 요약 조회

```
GET /api/market/summary
```

응답:
```json
{
  "korean": {
    "summary": "string",
    "kospi": 0,
    "kospiChange": 0,
    "kosdaq": 0,
    "kosdaqChange": 0
  },
  "us": {
    "summary": "string",
    "sp500": 0,
    "sp500Change": 0,
    "nasdaq": 0,
    "nasdaqChange": 0,
    "dow": 0,
    "dowChange": 0
  },
  "aiAnalysis": "string"
}
```

#### 한국 시장 개장 정보

```
GET /api/market/korea/open
```

응답:
```json
{
  "date": "string",
  "kospiPrevClose": 0,
  "kosdaqPrevClose": 0,
  "keyIssues": "string"
}
```

#### 한국 시장 마감 정보

```
GET /api/market/korea/close
```

응답:
```json
{
  "date": "string",
  "kospi": 0,
  "kospiChange": 0,
  "kosdaq": 0,
  "kosdaqChange": 0,
  "keyIssues": "string",
  "topGainers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "topLosers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ]
}
```

#### 미국 시장 개장 정보

```
GET /api/market/us/open
```

응답:
```json
{
  "date": "string",
  "sp500PrevClose": 0,
  "nasdaqPrevClose": 0,
  "dowPrevClose": 0,
  "keyIssues": "string"
}
```

#### 미국 시장 마감 정보

```
GET /api/market/us/close
```

응답:
```json
{
  "date": "string",
  "sp500": 0,
  "sp500Change": 0,
  "nasdaq": 0,
  "nasdaqChange": 0,
  "dow": 0,
  "dowChange": 0,
  "keyIssues": "string",
  "topGainers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "topLosers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ]
}
```

#### 주식 차트 데이터 조회

```
GET /api/stocks/{symbol}/chart
```

매개변수:
- `symbol`: 주식 심볼 (예: AAPL, 005930.KS)
- `interval`: 데이터 간격 (1d, 1wk, 1mo)
- `range`: 데이터 범위 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

응답:
```json
{
  "symbol": "string",
  "name": "string",
  "currency": "string",
  "timestamps": [0],
  "opens": [0],
  "highs": [0],
  "lows": [0],
  "closes": [0],
  "volumes": [0],
  "adjCloses": [0]
}
```

#### 주식 상세 정보 조회

```
GET /api/stocks/{symbol}/info
```

매개변수:
- `symbol`: 주식 심볼 (예: AAPL, 005930.KS)

응답:
```json
{
  "symbol": "string",
  "name": "string",
  "sector": "string",
  "industry": "string",
  "country": "string",
  "exchange": "string",
  "currency": "string",
  "price": 0,
  "change": 0,
  "changePercent": 0,
  "marketCap": 0,
  "volume": 0,
  "avgVolume": 0,
  "pe": 0,
  "eps": 0,
  "dividend": 0,
  "dividendYield": 0,
  "targetPrice": 0,
  "fiftyTwoWeekHigh": 0,
  "fiftyTwoWeekLow": 0
}
```

### 포트폴리오 관리

#### 포트폴리오 상태 조회

```
GET /api/portfolio/status
```

응답:
```json
{
  "totalValue": 0,
  "initialCash": 0,
  "roi": 0,
  "cash": 0,
  "positions": [
    {
      "symbol": "string",
      "name": "string",
      "quantity": 0,
      "value": 0,
      "roi": 0
    }
  ],
  "recentTransactions": [
    {
      "date": "string",
      "type": "string",
      "symbol": "string",
      "quantity": 0,
      "price": 0
    }
  ]
}
```

#### 주식 매수

```
POST /api/portfolio/buy
```

요청 본문:
```json
{
  "symbol": "string",
  "quantity": 0,
  "price": 0
}
```

응답:
```json
{
  "success": true,
  "message": "string",
  "transaction": {
    "date": "string",
    "type": "buy",
    "symbol": "string",
    "quantity": 0,
    "price": 0
  }
}
```

#### 주식 매도

```
POST /api/portfolio/sell
```

요청 본문:
```json
{
  "symbol": "string",
  "quantity": 0,
  "price": 0
}
```

응답:
```json
{
  "success": true,
  "message": "string",
  "transaction": {
    "date": "string",
    "type": "sell",
    "symbol": "string",
    "quantity": 0,
    "price": 0
  }
}
```

### 보고서

#### 일일 보고서 조회

```
GET /api/reports/daily
```

매개변수:
- `date`: 보고서 날짜 (YYYY-MM-DD, 기본값: 오늘)

응답:
```json
{
  "date": "string",
  "portfolioValue": 0,
  "previousValue": 0,
  "change": 0,
  "changePercent": 0,
  "marketSummary": {
    "korean": "string",
    "us": "string"
  },
  "topPerformers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "worstPerformers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "transactions": [
    {
      "type": "string",
      "symbol": "string",
      "quantity": 0,
      "price": 0
    }
  ],
  "aiAnalysis": "string"
}
```

#### 주간 보고서 조회

```
GET /api/reports/weekly
```

매개변수:
- `endDate`: 보고서 종료 날짜 (YYYY-MM-DD, 기본값: 오늘)

응답:
```json
{
  "startDate": "string",
  "endDate": "string",
  "portfolioValue": 0,
  "previousValue": 0,
  "change": 0,
  "changePercent": 0,
  "marketSummary": {
    "korean": "string",
    "us": "string"
  },
  "sectorPerformance": {
    "labels": ["string"],
    "values": [0]
  },
  "topPerformers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "worstPerformers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "transactions": [
    {
      "date": "string",
      "type": "string",
      "symbol": "string",
      "quantity": 0,
      "price": 0
    }
  ],
  "aiAnalysis": "string"
}
```

#### 월간 보고서 조회

```
GET /api/reports/monthly
```

매개변수:
- `month`: 보고서 월 (YYYY-MM, 기본값: 현재 월)

응답:
```json
{
  "month": "string",
  "portfolioValue": 0,
  "previousValue": 0,
  "change": 0,
  "changePercent": 0,
  "monthlyComparison": {
    "labels": ["string"],
    "values": [0]
  },
  "marketSummary": {
    "korean": "string",
    "us": "string"
  },
  "sectorPerformance": {
    "labels": ["string"],
    "values": [0]
  },
  "topPerformers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "worstPerformers": [
    {
      "symbol": "string",
      "name": "string",
      "change": 0
    }
  ],
  "transactionSummary": {
    "totalCount": 0,
    "buyCount": 0,
    "sellCount": 0,
    "totalAmount": 0
  },
  "aiAnalysis": "string"
}
```

### AI 관련

#### AI 추천 종목 조회

```
GET /api/recommendations
```

응답:
```json
{
  "summary": "string",
  "korean": [
    {
      "symbol": "string",
      "name": "string",
      "price": 0,
      "reason": "string"
    }
  ],
  "us": [
    {
      "symbol": "string",
      "name": "string",
      "price": 0,
      "reason": "string"
    }
  ]
}
```

#### AI 설정 조회

```
GET /api/ai/settings
```

응답:
```json
{
  "provider": "string",
  "model": "string",
  "apiKey": "string",
  "localEndpoint": "string",
  "temperature": 0,
  "maxTokens": 0
}
```

#### AI 설정 업데이트

```
PUT /api/ai/settings
```

요청 본문:
```json
{
  "provider": "string",
  "model": "string",
  "apiKey": "string",
  "localEndpoint": "string",
  "temperature": 0,
  "maxTokens": 0
}
```

응답:
```json
{
  "success": true,
  "message": "string"
}
```

### 알림 관련

#### 중요 변동 알림 조회

```
GET /api/alerts/significant-changes
```

매개변수:
- `threshold`: 중요 변동 기준값 (기본값: 5)

응답:
```json
{
  "changes": [
    {
      "symbol": "string",
      "name": "string",
      "changePercent": 0,
      "currentPrice": 0,
      "reason": "string"
    }
  ]
}
```

#### 알림 설정 조회

```
GET /api/alerts/settings
```

응답:
```json
{
  "notifyOnMarketOpen": true,
  "notifyOnMarketClose": true,
  "notifyOnSignificantChange": true,
  "significantChangeThreshold": 0,
  "dailyReportTime": "string",
  "weeklyReportDay": "string",
  "weeklyReportTime": "string",
  "monthlyReportDay": 0,
  "monthlyReportTime": "string"
}
```

#### 알림 설정 업데이트

```
PUT /api/alerts/settings
```

요청 본문:
```json
{
  "notifyOnMarketOpen": true,
  "notifyOnMarketClose": true,
  "notifyOnSignificantChange": true,
  "significantChangeThreshold": 0,
  "dailyReportTime": "string",
  "weeklyReportDay": "string",
  "weeklyReportTime": "string",
  "monthlyReportDay": 0,
  "monthlyReportTime": "string"
}
```

응답:
```json
{
  "success": true,
  "message": "string"
}
```

## 오류 응답

API는 다음과 같은 형식의 오류 응답을 반환합니다:

```json
{
  "detail": "string"
}
```

## 상태 코드

- `200 OK`: 요청 성공
- `201 Created`: 리소스 생성 성공
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스를 찾을 수 없음
- `500 Internal Server Error`: 서버 오류

## 제한 사항

- API 요청 비율: 분당 100회
- 최대 페이로드 크기: 10MB
