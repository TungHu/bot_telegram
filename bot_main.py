import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
from bot_api import get_token_balances, chain_apis
from config import telegrambot_token

# Bật logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Định nghĩa các trạng thái cho ConversationHandler
CHAIN_SELECTION, WALLET_INPUT = range(2)

# Hàm bắt đầu bot
async def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['ethereum', 'bsc', 'arbitrum', 'polygon', 'optimism', 'base']]
    await update.message.reply_text(
        'Chào bạn! Hãy chọn chain bạn muốn kiểm tra:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHAIN_SELECTION

# Hàm xử lý lựa chọn chain
async def chain_selection(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    chain = update.message.text.lower()
    logger.info("Chain selected by %s: %s", user.first_name, chain)
    if chain not in chain_apis:
        await update.message.reply_text('Chain không hợp lệ. Vui lòng chọn lại.')
        return CHAIN_SELECTION
    context.user_data['chain'] = chain
    context.user_data['cancelled'] = False  # Reset cancellation flag
    await update.message.reply_text('Vui lòng nhập các địa chỉ ví, mỗi ví trên một dòng:')
    return WALLET_INPUT

async def wallet_input(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    wallets_text = update.message.text
    wallets = wallets_text.strip().split('\n')
    wallets = [wallet.strip() for wallet in wallets if wallet.strip()]
    logger.info("Wallets input by %s: %s", user.first_name, wallets)

    chain = context.user_data['chain']
    api_info = chain_apis[chain]
    api_key = api_info['api_key']
    chain_url = api_info['url']

    total_wallets = len(wallets)
    for index, address in enumerate(wallets, start=1):
        # Check for cancellation
        if context.user_data.get('cancelled', False):
            await update.message.reply_text('Đã hủy bỏ thao tác.')
            return ConversationHandler.END
        
        try:
            token_balances = get_token_balances(api_key, address, chain_url)
            message = f"Ví {index}/{total_wallets}: {address}\n"
            if token_balances:
                message += "Token balances:\n"
                for token, balance in token_balances.items():
                    message += f"- {token}: {balance}\n"
            else:
                message += "Không có token nào hoặc không lấy được thông tin.\n"
        except Exception as e:
            message = f"Đã xảy ra lỗi khi lấy thông tin cho ví {address}: {str(e)}"
        
        # Gửi thông tin sau khi xử lý mỗi ví
        await update.message.reply_text(message)

    # Thông báo gửi xong
    await update.message.reply_text("Đã xử lý xong tất cả các ví.")

    # Kết thúc conversation
    return ConversationHandler.END

# Hàm hủy bỏ
async def cancel(update: Update, context: CallbackContext) -> int:
    context.user_data['cancelled'] = True
    await update.message.reply_text('Đã hủy bỏ thao tác.')
    return ConversationHandler.END

def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot's token
    application = Application.builder().token(telegrambot_token).build()

    # ConversationHandler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHAIN_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, chain_selection)],
            WALLET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
