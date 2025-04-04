/**
 * API 서비스
 * 
 * 백엔드 API와의 통신을 담당하는 서비스
 */

// API 기본 URL 설정
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

/**
 * API 요청 함수
 * 
 * @param {string} endpoint - API 엔드포인트
 * @param {Object} options - fetch 옵션
 * @returns {Promise<any>} - API 응답
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // 기본 헤더 설정
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };
    
    const response = await fetch(url, {
      ...options,
      headers
    });
    
    // 응답 확인
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API 요청 실패: ${response.status}`);
    }
    
    // 응답 데이터 반환
    return await response.json();
  } catch (error) {
    console.error('API 요청 중 오류 발생:', error);
    throw error;
  }
}

/**
 * 시장 데이터 API
 */
export const marketApi = {
  /**
   * 시장 개요 데이터를 가져옵니다.
   * 
   * @param {string} market - 시장 유형 (korean, us)
   * @returns {Promise<Object>} - 시장 개요 데이터
   */
  getMarketOverview: (market) => {
    return apiRequest('/api/market/data', {
      method: 'POST',
      body: JSON.stringify({ market })
    });
  },
  
  /**
   * 특정 주식 데이터를 가져옵니다.
   * 
   * @param {string} market - 시장 유형 (korean, us)
   * @param {string} symbol - 주식 심볼
   * @param {string} startDate - 시작 날짜 (YYYY-MM-DD)
   * @param {string} endDate - 종료 날짜 (YYYY-MM-DD)
   * @returns {Promise<Object>} - 주식 데이터
   */
  getStockData: (market, symbol, startDate, endDate) => {
    return apiRequest('/api/market/data', {
      method: 'POST',
      body: JSON.stringify({
        market,
        symbol,
        start_date: startDate,
        end_date: endDate
      })
    });
  }
};

/**
 * AI 분석 API
 */
export const aiApi = {
  /**
   * 시장 데이터를 분석합니다.
   * 
   * @param {string} providerType - AI 제공자 유형 (openai, mistral, gemini, local)
   * @param {Object} marketData - 시장 데이터
   * @returns {Promise<Object>} - 분석 결과
   */
  analyzeMarket: (providerType, marketData) => {
    return apiRequest('/api/ai/analyze', {
      method: 'POST',
      body: JSON.stringify({
        provider_type: providerType,
        market_data: marketData
      })
    });
  },
  
  /**
   * 투자할 주식을 추천받습니다.
   * 
   * @param {string} providerType - AI 제공자 유형 (openai, mistral, gemini, local)
   * @param {Object} marketData - 시장 데이터
   * @param {number} count - 추천 주식 수
   * @returns {Promise<Object>} - 추천 결과
   */
  recommendStocks: (providerType, marketData, count = 5) => {
    return apiRequest('/api/ai/recommend', {
      method: 'POST',
      body: JSON.stringify({
        provider_type: providerType,
        market_data: marketData,
        count
      })
    });
  },
  
  /**
   * 투자 결정을 내립니다.
   * 
   * @param {string} providerType - AI 제공자 유형 (openai, mistral, gemini, local)
   * @param {Object} marketData - 시장 데이터
   * @param {number} availableFunds - 사용 가능한 자금
   * @returns {Promise<Object>} - 투자 결정
   */
  makeInvestmentDecision: (providerType, marketData, availableFunds) => {
    return apiRequest('/api/ai/invest', {
      method: 'POST',
      body: JSON.stringify({
        provider_type: providerType,
        market_data: marketData,
        available_funds: availableFunds
      })
    });
  }
};

/**
 * 포트폴리오 API
 */
export const portfolioApi = {
  /**
   * 포트폴리오 데이터를 가져옵니다.
   * 
   * @returns {Promise<Object>} - 포트폴리오 데이터
   */
  getPortfolio: () => {
    return apiRequest('/api/portfolio', {
      method: 'GET'
    });
  },
  
  /**
   * 포트폴리오 성과를 가져옵니다.
   * 
   * @param {string} period - 기간 (daily, weekly, monthly, yearly, all)
   * @returns {Promise<Object>} - 포트폴리오 성과
   */
  getPerformance: (period = 'all') => {
    return apiRequest(`/api/portfolio/performance?period=${period}`, {
      method: 'GET'
    });
  }
};

/**
 * 설정 API
 */
export const settingsApi = {
  /**
   * 시스템 설정을 가져옵니다.
   * 
   * @returns {Promise<Object>} - 시스템 설정
   */
  getSettings: () => {
    return apiRequest('/api/settings', {
      method: 'GET'
    });
  },
  
  /**
   * AI 설정을 저장합니다.
   * 
   * @param {Object} settings - AI 설정
   * @returns {Promise<Object>} - 저장 결과
   */
  saveAISettings: (settings) => {
    return apiRequest('/api/settings/ai', {
      method: 'POST',
      body: JSON.stringify(settings)
    });
  },
  
  /**
   * 시스템 설정을 저장합니다.
   * 
   * @param {Object} settings - 시스템 설정
   * @returns {Promise<Object>} - 저장 결과
   */
  saveSystemSettings: (settings) => {
    return apiRequest('/api/settings/system', {
      method: 'POST',
      body: JSON.stringify(settings)
    });
  }
};

export default {
  market: marketApi,
  ai: aiApi,
  portfolio: portfolioApi,
  settings: settingsApi
};
