import telegram
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import main

token = '8312147261:'

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="GelSkin Data Collection Bot is online!")
    keyboard = [InlineKeyboardButton("Start Recording", callback_data='start_recording')]
    reply_markup = InlineKeyboardMarkup([keyboard])
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="Press the button to start recording.", reply_markup=reply_markup)
    await update.message.reply_text('Welcome to the GelSkin Data Collection Bot!',reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [InlineKeyboardButton("Start Recording", callback_data='start_recording')]
    reply_markup = InlineKeyboardMarkup([keyboard])
    
    if query.data == 'start_recording':
        await query.message.reply_text(text="Setting up record. Be prepared!")
        # Here you would call your main recording function
        # For demonstration, we'll just simulate a delay
        try:
            await main.main(context,update.effective_chat.id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Recording finished and data pulled!")
            await query.message.reply_text('Ready for another recording. Press the button below.', reply_markup=reply_markup)            

        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {e}")
            await query.message.reply_text('Maybe we can try again?', reply_markup=reply_markup)            

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    print('Bot started...')
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(CallbackQueryHandler(button))
    
    application.run_polling()
