/**
 * 유틸리티 함수 모듈
 * 텔레그램 봇에서 사용하는 다양한 유틸리티 함수를 제공합니다.
 */

/**
 * 통화 형식으로 포맷팅
 * @param {number} value - 포맷팅할 값
 * @param {string} currency - 통화 기호 (기본값: $)
 * @returns {string} 포맷팅된 통화 문자열
 */
function formatCurrency(value, currency = '$') {
  if (value === undefined || value === null) return `${currency}0.00`;
  
  return `${currency}${parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
}

/**
 * 퍼센트 형식으로 포맷팅
 * @param {number} value - 포맷팅할 값
 * @returns {string} 포맷팅된 퍼센트 문자열
 */
function formatPercentage(value) {
  if (value === undefined || value === null) return '0.00%';
  
  const sign = value >= 0 ? '+' : '';
  return `${sign}${parseFloat(value).toFixed(2)}%`;
}

/**
 * 날짜 형식으로 포맷팅
 * @param {string|Date} date - 포맷팅할 날짜
 * @param {string} format - 날짜 형식 (기본값: YYYY-MM-DD)
 * @returns {string} 포맷팅된 날짜 문자열
 */
function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '';
  
  const d = new Date(date);
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  
  if (format === 'YYYY-MM-DD') {
    return `${year}-${month}-${day}`;
  } else if (format === 'MM/DD/YYYY') {
    return `${month}/${day}/${year}`;
  } else if (format === 'DD/MM/YYYY') {
    return `${day}/${month}/${year}`;
  }
  
  return `${year}-${month}-${day}`;
}

/**
 * 텍스트 길이 제한
 * @param {string} text - 제한할 텍스트
 * @param {number} maxLength - 최대 길이 (기본값: 100)
 * @returns {string} 제한된 텍스트
 */
function truncateText(text, maxLength = 100) {
  if (!text) return '';
  
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength) + '...';
}

/**
 * 마크다운 이스케이프
 * @param {string} text - 이스케이프할 텍스트
 * @returns {string} 이스케이프된 텍스트
 */
function escapeMarkdown(text) {
  if (!text) return '';
  
  return text
    .replace(/_/g, '\\_')
    .replace(/\*/g, '\\*')
    .replace(/\[/g, '\\[')
    .replace(/\]/g, '\\]')
    .replace(/\(/g, '\\(')
    .replace(/\)/g, '\\)')
    .replace(/~/g, '\\~')
    .replace(/`/g, '\\`')
    .replace(/>/g, '\\>')
    .replace(/#/g, '\\#')
    .replace(/\+/g, '\\+')
    .replace(/-/g, '\\-')
    .replace(/=/g, '\\=')
    .replace(/\|/g, '\\|')
    .replace(/\{/g, '\\{')
    .replace(/\}/g, '\\}')
    .replace(/\./g, '\\.')
    .replace(/!/g, '\\!');
}

module.exports = {
  formatCurrency,
  formatPercentage,
  formatDate,
  truncateText,
  escapeMarkdown
};
