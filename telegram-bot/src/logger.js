const winston = require('winston');
const path = require('path');

// 로그 디렉토리 설정
const logDir = path.join(__dirname, '../logs');

// 로그 포맷 설정
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message }) => {
    return `${timestamp} [${level.toUpperCase()}]: ${message}`;
  })
);

// 로거 생성
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  transports: [
    // 콘솔 출력
    new winston.transports.Console(),
    // 파일 출력 (일반 로그)
    new winston.transports.File({ 
      filename: path.join(logDir, 'telegram-bot.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    // 파일 출력 (에러 로그)
    new winston.transports.File({ 
      filename: path.join(logDir, 'telegram-bot-error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

module.exports = logger;
