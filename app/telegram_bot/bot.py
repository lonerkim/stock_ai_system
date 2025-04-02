"""
텔레그램 봇 모듈

이 모듈은 텔레그램 봇을 구현하여 사용자와 상호작용합니다.
"""
import logging
import os
import json
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 환경 변수에서 설정 로드
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_USER_IDS = os.environ.get('ADMIN_USER_IDS', '').split(',')
ADMIN_USER_IDS = [int(user_id.strip()) for user_id in ADMIN_USER_IDS if user_id.strip()]

# 데이터 API 모듈 로드 시도 (없으면 대체 방법 사용)
try:
    import sys
    sys.path.append('/opt/.manus/.sandbox-runtime')
    from data_api import ApiClient
    client = ApiClient()
    logger.info("data_api 모듈 로드 성공")
    USE_DATA_API = True
except ImportError:
    logger.warning("data_api 모듈을 찾을 수 없습니다. 대체 방법을 사용합니다.")
    USE_DATA_API = False

# AI 모델 인터페이스 로드 시도
try:
    from app.embedding.ai_interface import AIModelInterface
    ai_interface = AIModelInterface()
    logger.info("AI 모델 인터페이스 로드 성공")
    USE_AI_INTERFACE = True
except ImportError:
    logger.warning("AI 모델 인터페이스를 찾을 수 없습니다. 대체 방법을 사용합니다.")
    USE_AI_INTERFACE = False

# 시작 명령어 처리
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """봇 시작 명령어 처리"""
    user = update.effective_user
    logger.info(f"사용자 {user.id} ({user.username})가 봇을 시작했습니다.")
    
    welcome_message = (
        f"안녕하세요, {user.first_name}님! 주식 시장 정보 수집 및 AI 분석 봇입니다.\n\n"
        "이 봇은 한국 및 미국 주식 시장 데이터를 수집하고 AI를 활용하여 분석합니다.\n"
        "또한 모의 투자를 통해 투자 성과를 추적할 수 있습니다.\n\n"
        "사용 가능한 명령어를 보려면 /help를 입력하세요."
    )
    
    await update.message.reply_text(welcome_message)

# 도움말 명령어 처리
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """도움말 명령어 처리"""
    help_text = (
        "📋 사용 가능한 명령어 목록:\n\n"
        "/start - 봇 시작\n"
        "/help - 도움말 표시\n"
        "/market - 시장 개요 조회\n"
        "/stock [심볼] - 특정 주식 정보 조회 (예: /stock AAPL)\n"
        "/portfolio - 모의 투자 포트폴리오 조회\n"
        "/invest - 모의 투자 실행\n"
        "/performance - 투자 성과 분석\n"
        "/ask [질문] - AI에게 주식 관련 질문하기\n\n"
        "또한 일반 메시지를 보내면 질문으로 처리됩니다."
    )
    
    # 관리자인 경우 추가 명령어 표시
    user_id = update.effective_user.id
    if str(user_id) in ADMIN_USER_IDS:
        help_text += (
            "\n\n🔐 관리자 명령어:\n"
            "/reset - 모의 투자 포트폴리오 초기화\n"
            "/update - 주식 데이터 수동 업데이트"
        )
    
    await update.message.reply_text(help_text)

# 시장 개요 명령어 처리
async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """시장 개요 조회 명령어 처리"""
    await update.message.reply_text("시장 데이터를 조회 중입니다...")
    
    try:
        # 실제 구현에서는 데이터 수집기를 사용하여 시장 데이터 조회
        market_data = "현재 시장 데이터를 표시합니다. (데모 데이터)\n\n"
        
        # 미국 시장 데이터
        market_data += "🇺🇸 미국 시장:\n"
        market_data += "S&P 500: 5,123.45 (+0.75%)\n"
        market_data += "나스닥: 16,234.56 (+1.2%)\n"
        market_data += "다우존스: 38,567.89 (+0.5%)\n\n"
        
        # 한국 시장 데이터
        market_data += "🇰🇷 한국 시장:\n"
        market_data += "코스피: 2,876.54 (+0.3%)\n"
        market_data += "코스닥: 987.65 (+0.8%)\n\n"
        
        # 업데이트 시간
        market_data += f"마지막 업데이트: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(market_data)
    except Exception as e:
        logger.error(f"시장 데이터 조회 중 오류 발생: {str(e)}")
        await update.message.reply_text(f"시장 데이터 조회 중 오류가 발생했습니다: {str(e)}")

# 주식 정보 명령어 처리
async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """특정 주식 정보 조회 명령어 처리"""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("주식 심볼을 입력해주세요. 예: /stock AAPL")
        return
    
    symbol = context.args[0].upper()
    await update.message.reply_text(f"{symbol} 주식 정보를 조회 중입니다...")
    
    try:
        # 실제 구현에서는 데이터 수집기를 사용하여 주식 정보 조회
        stock_data = f"📊 {symbol} 주식 정보 (데모 데이터):\n\n"
        
        if symbol == "AAPL":
            stock_data += "애플 (Apple Inc.)\n"
            stock_data += "현재가: $187.45 (+1.2%)\n"
            stock_data += "시가총액: 2.94조 달러\n"
            stock_data += "52주 최고가: $198.23\n"
            stock_data += "52주 최저가: $143.90\n"
            stock_data += "P/E 비율: 31.5\n"
            stock_data += "배당 수익률: 0.5%\n"
        elif symbol == "005930":
            stock_data += "삼성전자 (Samsung Electronics Co., Ltd.)\n"
            stock_data += "현재가: 78,500원 (+0.8%)\n"
            stock_data += "시가총액: 468.5조원\n"
            stock_data += "52주 최고가: 83,200원\n"
            stock_data += "52주 최저가: 65,300원\n"
            stock_data += "P/E 비율: 14.2\n"
            stock_data += "배당 수익률: 2.1%\n"
        else:
            stock_data += f"{symbol}에 대한 데모 데이터가 없습니다.\n"
        
        # 업데이트 시간
        stock_data += f"\n마지막 업데이트: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 관심 종목 추가 버튼
        keyboard = [
            [InlineKeyboardButton("관심 종목에 추가", callback_data=f"add_watchlist_{symbol}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(stock_data, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"주식 정보 조회 중 오류 발생: {str(e)}")
        await update.message.reply_text(f"주식 정보 조회 중 오류가 발생했습니다: {str(e)}")

# 포트폴리오 명령어 처리
async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """모의 투자 포트폴리오 조회 명령어 처리"""
    await update.message.reply_text("모의 투자 포트폴리오를 조회 중입니다...")
    
    try:
        # 실제 구현에서는 포트폴리오 관리자를 사용하여 포트폴리오 조회
        portfolio_data = "💼 모의 투자 포트폴리오 (데모 데이터):\n\n"
        
        # 포트폴리오 요약
        portfolio_data += "📊 포트폴리오 요약:\n"
        portfolio_data += "초기 투자금: $100.00\n"
        portfolio_data += "현재 가치: $127.35\n"
        portfolio_data += "총 수익률: +27.35%\n"
        portfolio_data += "보유 현금: $42.50\n\n"
        
        # 보유 종목
        portfolio_data += "🏢 보유 종목:\n"
        portfolio_data += "AAPL: 0.3주 ($56.24, +12.5%)\n"
        portfolio_data += "MSFT: 0.1주 ($28.61, +9.2%)\n\n"
        
        # 업데이트 시간
        portfolio_data += f"마지막 업데이트: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(portfolio_data)
    except Exception as e:
        logger.error(f"포트폴리오 조회 중 오류 발생: {str(e)}")
        await update.message.reply_text(f"포트폴리오 조회 중 오류가 발생했습니다: {str(e)}")

# 투자 명령어 처리
async def invest_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """모의 투자 실행 명령어 처리"""
    # 투자 옵션 버튼
    keyboard = [
        [
            InlineKeyboardButton("AI 추천 투자", callback_data="invest_ai"),
            InlineKeyboardButton("수동 투자", callback_data="invest_manual")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "모의 투자 방식을 선택하세요:",
        reply_markup=reply_markup
    )

# 성과 분석 명령어 처리
async def performance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """투자 성과 분석 명령어 처리"""
    await update.message.reply_text("투자 성과를 분석 중입니다...")
    
    try:
        # 실제 구현에서는 포트폴리오 관리자를 사용하여 성과 분석
        performance_data = "📈 투자 성과 분석 (데모 데이터):\n\n"
        
        # 수익률 분석
        performance_data += "📊 수익률 분석:\n"
        performance_data += "총 수익률: +27.35%\n"
        performance_data += "연간 수익률: +32.82%\n"
        performance_data += "월간 수익률: +2.5%\n\n"
        
        # 위험 분석
        performance_data += "⚠️ 위험 분석:\n"
        performance_data += "변동성: 15.4%\n"
        performance_data += "최대 손실: -8.2%\n"
        performance_data += "샤프 비율: 1.8\n\n"
        
        # 종목별 성과
        performance_data += "🏢 종목별 성과:\n"
        performance_data += "AAPL: +12.5%\n"
        performance_data += "MSFT: +9.2%\n\n"
        
        # 업데이트 시간
        performance_data += f"마지막 업데이트: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(performance_data)
    except Exception as e:
        logger.error(f"성과 분석 중 오류 발생: {str(e)}")
        await update.message.reply_text(f"성과 분석 중 오류가 발생했습니다: {str(e)}")

# 질문 명령어 처리
async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """AI에게 질문하는 명령어 처리"""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("질문을 입력해주세요. 예: /ask 애플 주식은 좋은 투자일까요?")
        return
    
    question = ' '.join(context.args)
    await process_question(update, question)

# 일반 메시지 처리 (질문으로 처리)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """일반 메시지를 질문으로 처리"""
    question = update.message.text
    await process_question(update, question)

# 질문 처리 함수
async def process_question(update: Update, question: str) -> None:
    """질문을 처리하고 AI 응답 생성"""
    await update.message.reply_text(f"질문을 처리 중입니다: '{question}'")
    
    try:
        # AI 모델 인터페이스가 있는 경우 사용
        if USE_AI_INTERFACE:
            response = ai_interface.generate_response(question)
        else:
            # 대체 응답 생성
            response = generate_fallback_response(question)
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"질문 처리 중 오류 발생: {str(e)}")
        await update.message.reply_text(f"질문 처리 중 오류가 발생했습니다: {str(e)}")

# 대체 응답 생성 함수
def generate_fallback_response(question: str) -> str:
    """AI 모델 인터페이스가 없을 때 대체 응답 생성"""
    question_lower = question.lower()
    
    if "애플" in question_lower or "apple" in question_lower or "aapl" in question_lower:
        return "애플(AAPL)은 안정적인 성장과 혁신적인 제품 라인업으로 장기 투자자들에게 인기 있는 종목입니다. 최근 실적과 향후 전망을 고려할 때 대체로 긍정적인 평가를 받고 있습니다."
    
    elif "삼성" in question_lower or "samsung" in question_lower or "005930" in question_lower:
        return "삼성전자(005930)는 한국 시장을 대표하는 기업으로, 반도체, 스마트폰, 가전제품 등 다양한 사업 분야에서 경쟁력을 갖추고 있습니다. 글로벌 반도체 시장의 변동성에 영향을 받지만, 장기적으로는 안정적인 성장이 예상됩니다."
    
    elif "시장" in question_lower or "market" in question_lower:
        return "현재 글로벌 주식 시장은 인플레이션 우려와 금리 정책의 영향을 받고 있습니다. 미국 시장은 기술주를 중심으로 강세를 보이고 있으며, 한국 시장은 수출 기업들의 실적에 따라 변동성을 보이고 있습니다. 개별 종목 분석과 함께 거시경제 지표를 주시하는 것이 중요합니다."
    
    elif "투자" in question_lower or "investment" in question_lower:
        return "투자 전략은 개인의 재정 상황, 위험 감수 성향, 투자 기간 등에 따라 달라집니다. 일반적으로 장기 투자와 분산 투자가 위험을 줄이는 데 도움이 됩니다. 특히 주식 시장의 변동성이 큰 시기에는 정기적인 분할 매수 전략이 효과적일 수 있습니다."
    
    else:
        return "죄송합니다. 현재 AI 모델 인터페이스가 연결되지 않아 상세한 답변을 제공하기 어렵습니다. 주식 시장, 특정 종목, 투자 전략 등에 대한 질문을 더 구체적으로 해주시면 도움이 될 수 있습니다."

# 콜백 쿼리 처리
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """인라인 버튼 콜백 처리"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data.startswith("add_watchlist_"):
        symbol = callback_data.replace("add_watchlist_", "")
        await query.edit_message_text(text=f"{symbol}이(가) 관심 종목에 추가되었습니다.")
    
    elif callback_data == "invest_ai":
        await query.edit_message_text(text="AI 추천 투자를 진행 중입니다...")
        # 실제 구현에서는 AI 기반 투자 결정 엔진 호출
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="AI 분석 결과에 따라 다음과 같이 투자했습니다:\n\nAAPL: $30.00 (0.16주)\nMSFT: $20.00 (0.07주)\n\n남은 현금: $50.00"
        )
    
    elif callback_data == "invest_manual":
        keyboard = [
            [
                InlineKeyboardButton("AAPL 매수", callback_data="buy_AAPL"),
                InlineKeyboardButton("MSFT 매수", callback_data="buy_MSFT")
            ],
            [
                InlineKeyboardButton("GOOGL 매수", callback_data="buy_GOOGL"),
                InlineKeyboardButton("AMZN 매수", callback_data="buy_AMZN")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text="매수할 종목을 선택하세요:",
            reply_markup=reply_markup
        )
    
    elif callback_data.startswith("buy_"):
        symbol = callback_data.replace("buy_", "")
        await query.edit_message_text(text=f"{symbol} 주식 매수 주문이 실행되었습니다.")
        # 실제 구현에서는 포트폴리오 관리자를 사용하여 매수 주문 실행
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{symbol} 주식을 $30.00 매수했습니다. (데모 데이터)"
        )

# 관리자 명령어: 포트폴리오 초기화
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """모의 투자 포트폴리오 초기화 명령어 처리 (관리자 전용)"""
    user_id = update.effective_user.id
    if str(user_id) not in ADMIN_USER_IDS:
        await update.message.reply_text("이 명령어는 관리자만 사용할 수 있습니다.")
        return
    
    await update.message.reply_text("모의 투자 포트폴리오를 초기화 중입니다...")
    
    try:
        # 실제 구현에서는 포트폴리오 관리자를 사용하여 포트폴리오 초기화
        await update.message.reply_text("모의 투자 포트폴리오가 초기화되었습니다. 초기 투자금: $100.00")
    except Exception as e:
        logger.error(f"포트폴리오 초기화 중 오류 발생: {str(e)}")
        await update.message.reply_text(f"포트폴리오 초기화 중 오류가 발생했습니다: {str(e)}")

# 관리자 명령어: 데이터 업데이트
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """주식 데이터 수동 업데이트 명령어 처리 (관리자 전용)"""
    user_id = update.effective_user.id
    if str(user_id) not in ADMIN_USER_IDS:
        await update.message.reply_text("이 명령어는 관리자만 사용할 수 있습니다.")
        return
    
    await update.message.reply_text("주식 데이터를 수동으로 업데이트 중입니다...")
    
    try:
        # 실제 구현에서는 데이터 수집기를 사용하여 주식 데이터 업데이트
        await update.message.reply_text("주식 데이터가 성공적으로 업데이트되었습니다.")
    except Exception as e:
        logger.error(f"데이터 업데이트 중 오류 발생: {str(e)}")
        await update.message.reply_text(f"데이터 업데이트 중 오류가 발생했습니다: {str(e)}")

# 메인 함수
def main() -> None:
    """텔레그램 봇 실행"""
    # 봇 토큰 확인
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
        return
    
    # 애플리케이션 생성
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 명령어 핸들러 등록
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("market", market_command))
    application.add_handler(CommandHandler("stock", stock_command))
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    application.add_handler(CommandHandler("invest", invest_command))
    application.add_handler(CommandHandler("performance", performance_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("update", update_command))
    
    # 콜백 쿼리 핸들러 등록
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # 일반 메시지 핸들러 등록
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # 봇 실행
    logger.info("텔레그램 봇 시작")
    application.run_polling()

if __name__ == "__main__":
    main()
