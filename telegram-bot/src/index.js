require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const cron = require('cron');
const moment = require('moment');
const logger = require('./logger');
const { generateDailyReport, generateWeeklyReport, generateMonthlyReport } = require('./reports');
const { formatCurrency, formatPercentage } = require('./utils');

// 환경 변수에서 텔레그램 봇 토큰 가져오기
const token = process.env.TELEGRAM_BOT_TOKEN;
const apiBaseUrl = process.env.API_BASE_URL || 'http://backend:8000';

// 봇 생성
const bot = new TelegramBot(token, { polling: true });

// 허용된 채팅 ID 목록
const allowedChatIds = (process.env.ALLOWED_CHAT_IDS || '').split(',').map(id => id.trim());

// 설정
const config = {
  notifyOnMarketOpen: process.env.NOTIFY_ON_MARKET_OPEN === 'true',
  notifyOnMarketClose: process.env.NOTIFY_ON_MARKET_CLOSE === 'true',
  notifyOnSignificantChange: process.env.NOTIFY_ON_SIGNIFICANT_CHANGE === 'true',
  significantChangeThreshold: parseFloat(process.env.SIGNIFICANT_CHANGE_THRESHOLD || '5'),
  dailyReportTime: process.env.DAILY_REPORT_TIME || '18:00',
  weeklyReportDay: process.env.WEEKLY_REPORT_DAY || 'friday',
  weeklyReportTime: process.env.WEEKLY_REPORT_TIME || '18:00',
  monthlyReportDay: parseInt(process.env.MONTHLY_REPORT_DAY || '1'),
  monthlyReportTime: process.env.MONTHLY_REPORT_TIME || '18:00'
};

// 권한 확인 함수
const isAuthorized = (chatId) => {
  return allowedChatIds.includes(chatId.toString());
};

// 시작 명령어 처리
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    logger.warn(`Unauthorized access attempt from chat ID: ${chatId}`);
    return;
  }

  bot.sendMessage(chatId,
    '안녕하세요! 주식 시장 AI 분석 시스템 봇입니다.\n\n' +
    '다음 명령어를 사용할 수 있습니다:\n' +
    '/summary - 현재 시장 요약 보기\n' +
    '/portfolio - 포트폴리오 상태 보기\n' +
    '/daily - 일일 보고서 요청\n' +
    '/weekly - 주간 보고서 요청\n' +
    '/monthly - 월간 보고서 요청\n' +
    '/recommendations - AI 추천 종목 보기\n' +
    '/help - 도움말 보기'
  );

  logger.info(`Bot started by user with chat ID: ${chatId}`);
});

// 도움말 명령어 처리
bot.onText(/\/help/, (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    return;
  }

  bot.sendMessage(chatId,
    '주식 시장 AI 분석 시스템 봇 도움말:\n\n' +
    '명령어 목록:\n' +
    '/summary - 현재 시장 요약 보기\n' +
    '/portfolio - 포트폴리오 상태 보기\n' +
    '/daily - 일일 보고서 요청\n' +
    '/weekly - 주간 보고서 요청\n' +
    '/monthly - 월간 보고서 요청\n' +
    '/recommendations - AI 추천 종목 보기\n' +
    '/help - 도움말 보기\n\n' +
    '설정된 알림:\n' +
    `- 시장 개장 알림: ${config.notifyOnMarketOpen ? '활성화' : '비활성화'}\n` +
    `- 시장 마감 알림: ${config.notifyOnMarketClose ? '활성화' : '비활성화'}\n` +
    `- 중요 변동 알림: ${config.notifyOnSignificantChange ? '활성화' : '비활성화'} (기준: ${config.significantChangeThreshold}%)\n` +
    `- 일일 보고서: 매일 ${config.dailyReportTime}\n` +
    `- 주간 보고서: 매주 ${config.weeklyReportDay} ${config.weeklyReportTime}\n` +
    `- 월간 보고서: 매월 ${config.monthlyReportDay}일 ${config.monthlyReportTime}`
  );
});

// 시장 요약 명령어 처리
bot.onText(/\/summary/, async (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    return;
  }

  try {
    bot.sendMessage(chatId, '시장 요약을 가져오는 중입니다...');

    // API에서 시장 요약 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/market/summary`);
    const data = response.data;

    let message = '📊 *시장 요약*\n\n';

    // 한국 시장
    message += '*한국 시장*\n';
    message += `${data.korean.summary}\n\n`;
    message += `KOSPI: ${data.korean.kospi} (${formatPercentage(data.korean.kospiChange)})\n`;
    message += `KOSDAQ: ${data.korean.kosdaq} (${formatPercentage(data.korean.kosdaqChange)})\n\n`;

    // 미국 시장
    message += '*미국 시장*\n';
    message += `${data.us.summary}\n\n`;
    message += `S&P 500: ${data.us.sp500} (${formatPercentage(data.us.sp500Change)})\n`;
    message += `NASDAQ: ${data.us.nasdaq} (${formatPercentage(data.us.nasdaqChange)})\n`;
    message += `DOW: ${data.us.dow} (${formatPercentage(data.us.dowChange)})\n\n`;

    // AI 분석
    message += '*AI 분석*\n';
    message += data.aiAnalysis;

    bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
    logger.info(`Market summary sent to chat ID: ${chatId}`);
  } catch (error) {
    logger.error(`Error fetching market summary: ${error.message}`);
    bot.sendMessage(chatId, '시장 요약을 가져오는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
  }
});

// 포트폴리오 상태 명령어 처리
bot.onText(/\/portfolio/, async (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    return;
  }

  try {
    bot.sendMessage(chatId, '포트폴리오 정보를 가져오는 중입니다...');

    // API에서 포트폴리오 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/portfolio/status`);
    const data = response.data;

    let message = '💼 *포트폴리오 상태*\n\n';

    // 포트폴리오 요약
    message += `*총 가치*: ${formatCurrency(data.totalValue)}\n`;
    message += `*초기 투자*: ${formatCurrency(data.initialCash)}\n`;
    message += `*수익률*: ${formatPercentage(data.roi)}\n`;
    message += `*현금 잔액*: ${formatCurrency(data.cash)}\n\n`;

    // 보유 포지션
    message += '*보유 포지션*\n';
    if (data.positions.length > 0) {
      data.positions.forEach(position => {
        message += `${position.symbol} (${position.name}): ${position.quantity} 주\n`;
        message += `  가치: ${formatCurrency(position.value)} | 수익률: ${formatPercentage(position.roi)}\n`;
      });
    } else {
      message += '보유 중인 포지션이 없습니다.\n';
    }

    // 최근 거래
    message += '\n*최근 거래*\n';
    if (data.recentTransactions.length > 0) {
      data.recentTransactions.forEach(tx => {
        const type = tx.type === 'buy' ? '매수' : '매도';
        message += `${tx.date}: ${type} ${tx.symbol} ${tx.quantity} 주 @ ${formatCurrency(tx.price)}\n`;
      });
    } else {
      message += '최근 거래 내역이 없습니다.\n';
    }

    bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
    logger.info(`Portfolio status sent to chat ID: ${chatId}`);
  } catch (error) {
    logger.error(`Error fetching portfolio status: ${error.message}`);
    bot.sendMessage(chatId, '포트폴리오 정보를 가져오는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
  }
});

// 일일 보고서 명령어 처리
bot.onText(/\/daily/, async (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    return;
  }

  try {
    bot.sendMessage(chatId, '일일 보고서를 생성하는 중입니다...');

    // API에서 일일 보고서 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/reports/daily`);
    const data = response.data;

    // 보고서 생성
    const report = generateDailyReport(data);

    bot.sendMessage(chatId, report, { parse_mode: 'Markdown' });
    logger.info(`Daily report sent to chat ID: ${chatId}`);
  } catch (error) {
    logger.error(`Error generating daily report: ${error.message}`);
    bot.sendMessage(chatId, '일일 보고서를 생성하는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
  }
});

// 주간 보고서 명령어 처리
bot.onText(/\/weekly/, async (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    return;
  }

  try {
    bot.sendMessage(chatId, '주간 보고서를 생성하는 중입니다...');

    // API에서 주간 보고서 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/reports/weekly`);
    const data = response.data;

    // 보고서 생성
    const report = generateWeeklyReport(data);

    bot.sendMessage(chatId, report, { parse_mode: 'Markdown' });
    logger.info(`Weekly report sent to chat ID: ${chatId}`);
  } catch (error) {
    logger.error(`Error generating weekly report: ${error.message}`);
    bot.sendMessage(chatId, '주간 보고서를 생성하는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
  }
});

// 월간 보고서 명령어 처리
bot.onText(/\/monthly/, async (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    return;
  }

  try {
    bot.sendMessage(chatId, '월간 보고서를 생성하는 중입니다...');

    // API에서 월간 보고서 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/reports/monthly`);
    const data = response.data;

    // 보고서 생성
    const report = generateMonthlyReport(data);

    bot.sendMessage(chatId, report, { parse_mode: 'Markdown' });
    logger.info(`Monthly report sent to chat ID: ${chatId}`);
  } catch (error) {
    logger.error(`Error generating monthly report: ${error.message}`);
    bot.sendMessage(chatId, '월간 보고서를 생성하는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
  }
});

// AI 추천 종목 명령어 처리
bot.onText(/\/recommendations/, async (msg) => {
  const chatId = msg.chat.id;

  if (!isAuthorized(chatId)) {
    bot.sendMessage(chatId, '죄송합니다. 이 봇을 사용할 권한이 없습니다.');
    return;
  }

  try {
    bot.sendMessage(chatId, 'AI 추천 종목을 가져오는 중입니다...');

    // API에서 추천 종목 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/recommendations`);
    const data = response.data;

    let message = '🤖 *AI 추천 종목*\n\n';

    // 추천 이유
    message += `*분석 요약*\n${data.summary}\n\n`;

    // 한국 시장 추천
    message += '*한국 시장 추천 종목*\n';
    if (data.korean.length > 0) {
      data.korean.forEach((stock, index) => {
        message += `${index + 1}. ${stock.symbol} (${stock.name})\n`;
        message += `   가격: ${formatCurrency(stock.price)} | 추천 이유: ${stock.reason}\n`;
      });
    } else {
      message += '현재 추천 종목이 없습니다.\n';
    }

    message += '\n';

    // 미국 시장 추천
    message += '*미국 시장 추천 종목*\n';
    if (data.us.length > 0) {
      data.us.forEach((stock, index) => {
        message += `${index + 1}. ${stock.symbol} (${stock.name})\n`;
        message += `   가격: ${formatCurrency(stock.price)} | 추천 이유: ${stock.reason}\n`;
      });
    } else {
      message += '현재 추천 종목이 없습니다.\n';
    }

    bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
    logger.info(`AI recommendations sent to chat ID: ${chatId}`);
  } catch (error) {
    logger.error(`Error fetching AI recommendations: ${error.message}`);
    bot.sendMessage(chatId, 'AI 추천 종목을 가져오는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.');
  }
});

// 시장 개장 알림 스케줄러
if (config.notifyOnMarketOpen) {
  // 한국 시장 개장 (오전 9시)
  new cron.CronJob('0 0 9 * * 1-5', async () => {
    try {
      // API에서 한국 시장 개장 데이터 가져오기
      const response = await axios.get(`${apiBaseUrl}/api/market/korea/open`);
      const data = response.data;

      let message = '🇰🇷 *한국 시장 개장*\n\n';
      message += `${data.date} 한국 시장이 개장했습니다.\n\n`;
      message += `KOSPI 전일 종가: ${data.kospiPrevClose}\n`;
      message += `KOSDAQ 전일 종가: ${data.kosdaqPrevClose}\n\n`;
      message += `*오늘의 주요 이슈*\n${data.keyIssues}`;

      // 모든 허용된 채팅에 메시지 전송
      for (const chatId of allowedChatIds) {
        bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
      }

      logger.info('Korean market open notification sent');
    } catch (error) {
      logger.error(`Error sending Korean market open notification: ${error.message}`);
    }
  }, null, true, 'Asia/Seoul');

  // 미국 시장 개장 (오후 10시 30분, 한국 시간)
  new cron.CronJob('0 30 22 * * 1-5', async () => {
    try {
      // API에서 미국 시장 개장 데이터 가져오기
      const response = await axios.get(`${apiBaseUrl}/api/market/us/open`);
      const data = response.data;

      let message = '🇺🇸 *미국 시장 개장*\n\n';
      message += `${data.date} 미국 시장이 개장했습니다.\n\n`;
      message += `S&P 500 전일 종가: ${data.sp500PrevClose}\n`;
      message += `NASDAQ 전일 종가: ${data.nasdaqPrevClose}\n`;
      message += `DOW 전일 종가: ${data.dowPrevClose}\n\n`;
      message += `*오늘의 주요 이슈*\n${data.keyIssues}`;

      // 모든 허용된 채팅에 메시지 전송
      for (const chatId of allowedChatIds) {
        bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
      }

      logger.info('US market open notification sent');
    } catch (error) {
      logger.error(`Error sending US market open notification: ${error.message}`);
    }
  }, null, true, 'Asia/Seoul');
}

// 시장 마감 알림 스케줄러
if (config.notifyOnMarketClose) {
  // 한국 시장 마감 (오후 3시 30분)
  new cron.CronJob('0 30 15 * * 1-5', async () => {
    try {
      // API에서 한국 시장 마감 데이터 가져오기
      const response = await axios.get(`${apiBaseUrl}/api/market/korea/close`);
      const data = response.data;

      let message = '🇰🇷 *한국 시장 마감*\n\n';
      message += `${data.date} 한국 시장이 마감했습니다.\n\n`;
      message += `KOSPI: ${data.kospi} (${formatPercentage(data.kospiChange)})\n`;
      message += `KOSDAQ: ${data.kosdaq} (${formatPercentage(data.kosdaqChange)})\n\n`;
      message += `*오늘의 주요 이슈*\n${data.keyIssues}\n\n`;
      message += `*상위 종목*\n`;

      data.topGainers.forEach((stock, index) => {
        message += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
      });

      message += `\n*하위 종목*\n`;

      data.topLosers.forEach((stock, index) => {
        message += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
      });

      // 모든 허용된 채팅에 메시지 전송
      for (const chatId of allowedChatIds) {
        bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
      }

      logger.info('Korean market close notification sent');
    } catch (error) {
      logger.error(`Error sending Korean market close notification: ${error.message}`);
    }
  }, null, true, 'Asia/Seoul');

  // 미국 시장 마감 (오전 5시, 한국 시간)
  new cron.CronJob('0 0 5 * * 2-6', async () => {
    try {
      // API에서 미국 시장 마감 데이터 가져오기
      const response = await axios.get(`${apiBaseUrl}/api/market/us/close`);
      const data = response.data;

      let message = '🇺🇸 *미국 시장 마감*\n\n';
      message += `${data.date} 미국 시장이 마감했습니다.\n\n`;
      message += `S&P 500: ${data.sp500} (${formatPercentage(data.sp500Change)})\n`;
      message += `NASDAQ: ${data.nasdaq} (${formatPercentage(data.nasdaqChange)})\n`;
      message += `DOW: ${data.dow} (${formatPercentage(data.dowChange)})\n\n`;
      message += `*오늘의 주요 이슈*\n${data.keyIssues}\n\n`;
      message += `*상위 종목*\n`;

      data.topGainers.forEach((stock, index) => {
        message += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
      });

      message += `\n*하위 종목*\n`;

      data.topLosers.forEach((stock, index) => {
        message += `${index + 1}. ${stock.symbol} (${stock.name}): ${formatPercentage(stock.change)}\n`;
      });

      // 모든 허용된 채팅에 메시지 전송
      for (const chatId of allowedChatIds) {
        bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
      }

      logger.info('US market close notification sent');
    } catch (error) {
      logger.error(`Error sending US market close notification: ${error.message}`);
    }
  }, null, true, 'Asia/Seoul');
}

// 중요 변동 알림 폴링
if (config.notifyOnSignificantChange) {
  // 15분마다 중요 변동 확인
  setInterval(async () => {
    try {
      // API에서 중요 변동 데이터 가져오기
      const response = await axios.get(`${apiBaseUrl}/api/alerts/significant-changes`, {
        params: { threshold: config.significantChangeThreshold }
      });
      const data = response.data;

      if (data.changes.length > 0) {
        let message = '⚠️ *중요 변동 알림*\n\n';

        data.changes.forEach(change => {
          const direction = change.changePercent > 0 ? '상승' : '하락';
          message += `${change.symbol} (${change.name}): ${formatPercentage(change.changePercent)} ${direction}\n`;
          message += `현재가: ${formatCurrency(change.currentPrice)}\n`;
          message += `변동 이유: ${change.reason || '정보 없음'}\n\n`;
        });

        // 모든 허용된 채팅에 메시지 전송
        for (const chatId of allowedChatIds) {
          bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
        }

        logger.info(`Significant change notification sent for ${data.changes.length} stocks`);
      }
    } catch (error) {
      logger.error(`Error checking for significant changes: ${error.message}`);
    }
  }, 15 * 60 * 1000); // 15분마다
}

// 일일 보고서 스케줄러
const dailyReportTime = config.dailyReportTime || '18:00';
const [dailyHour, dailyMinute] = dailyReportTime.split(':').map(Number);
new cron.CronJob(`0 ${dailyMinute} ${dailyHour} * * *`, async () => {
  try {
    // API에서 일일 보고서 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/reports/daily`);
    const data = response.data;

    // 보고서 생성
    const report = generateDailyReport(data);

    // 모든 허용된 채팅에 메시지 전송
    for (const chatId of allowedChatIds) {
      bot.sendMessage(chatId, report, { parse_mode: 'Markdown' });
    }

    logger.info('Daily report sent to all allowed chats');
  } catch (error) {
    logger.error(`Error sending scheduled daily report: ${error.message}`);
  }
}, null, true, 'Asia/Seoul');

// 주간 보고서 스케줄러
const weekDays = { 'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6 };
const weeklyReportDay = config.weeklyReportDay || 'friday';
const weeklyDay = weekDays[weeklyReportDay.toLowerCase()] || 5; // 기본값은 금요일
const weeklyReportTime = config.weeklyReportTime || '18:00';
const [weeklyHour, weeklyMinute] = weeklyReportTime.split(':').map(Number);
new cron.CronJob(`0 ${weeklyMinute} ${weeklyHour} * * ${weeklyDay}`, async () => {
  try {
    // API에서 주간 보고서 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/reports/weekly`);
    const data = response.data;

    // 보고서 생성
    const report = generateWeeklyReport(data);

    // 모든 허용된 채팅에 메시지 전송
    for (const chatId of allowedChatIds) {
      bot.sendMessage(chatId, report, { parse_mode: 'Markdown' });
    }

    logger.info('Weekly report sent to all allowed chats');
  } catch (error) {
    logger.error(`Error sending scheduled weekly report: ${error.message}`);
  }
}, null, true, 'Asia/Seoul');

// 월간 보고서 스케줄러
const monthlyReportDay = parseInt(config.monthlyReportDay || '1');
const monthlyReportTime = config.monthlyReportTime || '18:00';
const [monthlyHour, monthlyMinute] = monthlyReportTime.split(':').map(Number);
new cron.CronJob(`0 ${monthlyMinute} ${monthlyHour} ${monthlyReportDay} * *`, async () => {
  try {
    // API에서 월간 보고서 데이터 가져오기
    const response = await axios.get(`${apiBaseUrl}/api/reports/monthly`);
    const data = response.data;

    // 보고서 생성
    const report = generateMonthlyReport(data);

    // 모든 허용된 채팅에 메시지 전송
    for (const chatId of allowedChatIds) {
      bot.sendMessage(chatId, report, { parse_mode: 'Markdown' });
    }

    logger.info('Monthly report sent to all allowed chats');
  } catch (error) {
    logger.error(`Error sending scheduled monthly report: ${error.message}`);
  }
}, null, true, 'Asia/Seoul');

// 봇 시작 로그
logger.info('Telegram bot started');
console.log('Telegram bot is running...');

module.exports = bot;
