/**
 * 보고서 생성 모듈
 * 일일, 주간, 월간 보고서 생성 함수를 제공합니다.
 */

const { formatCurrency, formatPercentage } = require('./utils');

/**
 * 일일 보고서 생성
 * @param {Object} data - 일일 보고서 데이터
 * @returns {string} 마크다운 형식의 보고서
 */
function generateDailyReport(data) {
  let report = `📊 *일일 보고서 (${data.date})*\n\n`;
  
  // 포트폴리오 요약
  report += '*포트폴리오 요약*\n';
  report += `현재 가치: ${formatCurrency(data.portfolioValue)}\n`;
  report += `전일 가치: ${formatCurrency(data.previousValue)}\n`;
  report += `변동: ${formatCurrency(data.change)} (${formatPercentage(data.changePercent)})\n\n`;
  
  // 시장 요약
  report += '*시장 요약*\n';
  report += `한국 시장: ${data.marketSummary.korean}\n`;
  report += `미국 시장: ${data.marketSummary.us}\n\n`;
  
  // 상위 종목
  report += '*상위 종목*\n';
  if (data.topPerformers.length > 0) {
    data.topPerformers.forEach((stock, index) => {
      report += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
    });
  } else {
    report += '상위 종목 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 하위 종목
  report += '*하위 종목*\n';
  if (data.worstPerformers.length > 0) {
    data.worstPerformers.forEach((stock, index) => {
      report += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
    });
  } else {
    report += '하위 종목 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 거래 내역
  report += '*오늘의 거래*\n';
  if (data.transactions.length > 0) {
    data.transactions.forEach((tx) => {
      const type = tx.type === 'buy' ? '매수' : '매도';
      report += `${type} ${tx.symbol} ${tx.quantity} 주 @ ${formatCurrency(tx.price)}\n`;
    });
  } else {
    report += '오늘의 거래 내역이 없습니다.\n';
  }
  
  report += '\n';
  
  // AI 분석
  report += '*AI 분석*\n';
  report += data.aiAnalysis || '분석 정보가 없습니다.';
  
  return report;
}

/**
 * 주간 보고서 생성
 * @param {Object} data - 주간 보고서 데이터
 * @returns {string} 마크다운 형식의 보고서
 */
function generateWeeklyReport(data) {
  let report = `📈 *주간 보고서 (${data.startDate} ~ ${data.endDate})*\n\n`;
  
  // 포트폴리오 요약
  report += '*포트폴리오 요약*\n';
  report += `현재 가치: ${formatCurrency(data.portfolioValue)}\n`;
  report += `시작 가치: ${formatCurrency(data.previousValue)}\n`;
  report += `변동: ${formatCurrency(data.change)} (${formatPercentage(data.changePercent)})\n\n`;
  
  // 시장 요약
  report += '*시장 요약*\n';
  report += `한국 시장: ${data.marketSummary.korean}\n`;
  report += `미국 시장: ${data.marketSummary.us}\n\n`;
  
  // 섹터 성과
  report += '*섹터별 성과*\n';
  if (data.sectorPerformance && data.sectorPerformance.labels) {
    data.sectorPerformance.labels.forEach((sector, index) => {
      const value = data.sectorPerformance.values[index];
      report += `${sector}: ${formatPercentage(value)}\n`;
    });
  } else {
    report += '섹터별 성과 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 상위 종목
  report += '*주간 상위 종목*\n';
  if (data.topPerformers.length > 0) {
    data.topPerformers.forEach((stock, index) => {
      report += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
    });
  } else {
    report += '상위 종목 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 하위 종목
  report += '*주간 하위 종목*\n';
  if (data.worstPerformers.length > 0) {
    data.worstPerformers.forEach((stock, index) => {
      report += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
    });
  } else {
    report += '하위 종목 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 거래 내역
  report += '*주간 거래 요약*\n';
  if (data.transactions.length > 0) {
    data.transactions.forEach((tx) => {
      const type = tx.type === 'buy' ? '매수' : '매도';
      report += `${tx.date}: ${type} ${tx.symbol} ${tx.quantity} 주 @ ${formatCurrency(tx.price)}\n`;
    });
  } else {
    report += '이번 주 거래 내역이 없습니다.\n';
  }
  
  report += '\n';
  
  // AI 분석
  report += '*AI 주간 분석*\n';
  report += data.aiAnalysis || '분석 정보가 없습니다.';
  
  return report;
}

/**
 * 월간 보고서 생성
 * @param {Object} data - 월간 보고서 데이터
 * @returns {string} 마크다운 형식의 보고서
 */
function generateMonthlyReport(data) {
  let report = `📆 *월간 보고서 (${data.month})*\n\n`;
  
  // 포트폴리오 요약
  report += '*포트폴리오 요약*\n';
  report += `현재 가치: ${formatCurrency(data.portfolioValue)}\n`;
  report += `시작 가치: ${formatCurrency(data.previousValue)}\n`;
  report += `변동: ${formatCurrency(data.change)} (${formatPercentage(data.changePercent)})\n\n`;
  
  // 월별 비교
  report += '*월별 수익률 비교*\n';
  if (data.monthlyComparison && data.monthlyComparison.labels) {
    data.monthlyComparison.labels.forEach((month, index) => {
      const value = data.monthlyComparison.values[index];
      report += `${month}: ${formatPercentage(value)}\n`;
    });
  } else {
    report += '월별 비교 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 시장 요약
  report += '*시장 요약*\n';
  report += `한국 시장: ${data.marketSummary.korean}\n`;
  report += `미국 시장: ${data.marketSummary.us}\n\n`;
  
  // 섹터 성과
  report += '*섹터별 성과*\n';
  if (data.sectorPerformance && data.sectorPerformance.labels) {
    data.sectorPerformance.labels.forEach((sector, index) => {
      const value = data.sectorPerformance.values[index];
      report += `${sector}: ${formatPercentage(value)}\n`;
    });
  } else {
    report += '섹터별 성과 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 상위 종목
  report += '*월간 상위 종목*\n';
  if (data.topPerformers.length > 0) {
    data.topPerformers.forEach((stock, index) => {
      report += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
    });
  } else {
    report += '상위 종목 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 하위 종목
  report += '*월간 하위 종목*\n';
  if (data.worstPerformers.length > 0) {
    data.worstPerformers.forEach((stock, index) => {
      report += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
    });
  } else {
    report += '하위 종목 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // 거래 내역 요약
  report += '*월간 거래 요약*\n';
  if (data.transactionSummary) {
    report += `총 거래 횟수: ${data.transactionSummary.totalCount}회\n`;
    report += `매수 횟수: ${data.transactionSummary.buyCount}회\n`;
    report += `매도 횟수: ${data.transactionSummary.sellCount}회\n`;
    report += `총 거래 금액: ${formatCurrency(data.transactionSummary.totalAmount)}\n`;
  } else {
    report += '거래 요약 정보가 없습니다.\n';
  }
  
  report += '\n';
  
  // AI 분석
  report += '*AI 월간 분석 및 전망*\n';
  report += data.aiAnalysis || '분석 정보가 없습니다.';
  
  return report;
}

module.exports = {
  generateDailyReport,
  generateWeeklyReport,
  generateMonthlyReport
};
