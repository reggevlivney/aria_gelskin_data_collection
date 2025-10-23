import telegram
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import main
import main_sensor_only as main_s

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="GelSkin Data Collection Bot is online!")
    keyboard = [InlineKeyboardButton("Full Recording", callback_data='start_full_recording'), InlineKeyboardButton("Sensor Recording", callback_data='start_sensor_recording')]
    reply_markup = InlineKeyboardMarkup([keyboard])
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Press the button to start recording.", reply_markup=reply_markup)
    await update.message.reply_text('Welcome to the GelSkin Data Collection Bot!',reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [InlineKeyboardButton("Full Recording", callback_data='start_full_recording'), InlineKeyboardButton("Sensor Recording", callback_data='start_sensor_recording')]
    reply_markup = InlineKeyboardMarkup([keyboard])

    handlers = {
        'start_full_recording': (main.main, 'full recording'),
        'start_sensor_recording': (main_s.main, 'sensor recording'),
    }

    cmd = query.data
    chat_id = update.effective_chat.id
    handler = handlers.get(cmd)

    if not handler:
        await query.message.reply_text('Unknown action.', reply_markup=reply_markup)
        return

    func, label = handler
    await query.message.reply_text(text=f"Setting up {label}. Be prepared!")
    try:
        await func(context, chat_id)
        await context.bot.send_message(chat_id=chat_id, text="Recording finished and data pulled!")
        await query.message.reply_text('Ready for another recording. Press the button below.', reply_markup=reply_markup)
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"An error occurred: {e}")
        await query.message.reply_text('Maybe we can try again?', reply_markup=reply_markup)
            
if __name__ == '__main__':
    with open('/home/reggev/token.txt', 'r') as file: token = file.read().strip()
    application = ApplicationBuilder().token(token).build()
    print('Bot started...')
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(CallbackQueryHandler(button))
    
    application.run_polling()
