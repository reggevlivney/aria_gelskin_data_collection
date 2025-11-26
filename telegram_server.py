import telegram
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
import main
import main_sensor_only as main_s
import main_sensor_test_comm as main_test
import json
import ipaddress
from pathlib import Path
from telegram.ext import MessageHandler, filters

class Bot():
    def __init__(self, token):
        self.token = token
        self.main_keyboard = [[InlineKeyboardButton("Full Recording", callback_data='start_full_recording'), InlineKeyboardButton("Sensor Recording", callback_data='start_sensor_recording')]
                ,[InlineKeyboardButton("Test Sensor Communication", callback_data='test_sensor_communication')]
                ,[InlineKeyboardButton("Edit Config", callback_data='edit_config')]]
        self.main_reply_markup = InlineKeyboardMarkup(self.main_keyboard)
        self.application = ApplicationBuilder().token(token).build()

        self.load_config()
        print('Bot started...')

        self.start_handler = CommandHandler('start', self.start)
        self.application.add_handler(self.start_handler)
        self.main_button_handler = CallbackQueryHandler(self.button)
        self.application.add_handler(self.main_button_handler)
        
        self.application.run_polling()

    def load_config(self):
        config_path = Path(__file__).parent / 'config.json'
        if not config_path.exists():
            # create default config if missing
            config_path.write_text(json.dumps({"sensor_ip": "", "aria_ip": "", "duration": 0}, indent=2))
        try:
            with open(config_path, 'r') as f:
                self.cfg = json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            self.cfg = {"sensor_ip": "", "aria_ip": "", "duration": 0}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="GelSkin Data Collection Bot is online!")
        await update.message.reply_text('Welcome to the GelSkin Data Collection Bot!',reply_markup=self.main_reply_markup)

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        handlers = {
            'start_full_recording': (main.main, 'full recording'),
            'start_sensor_recording': (main_s.main, 'sensor recording'),
            'test_sensor_communication': (main_test.main, 'sensor communication test'),
            'edit_config': (self.edit_config, 'editing configuration')
        }

        cmd = query.data
        chat_id = update.effective_chat.id
        handler = handlers.get(cmd)

        if not handler:
            await query.message.reply_text('Unknown action.', reply_markup=self.main_reply_markup)
            return

        func, label = handler
        if label in ['full recording', 'sensor recording', 'sensor communication test']:
            await query.message.reply_text(text=f"Setting up {label}. Be prepared!")
            try:
                await func(context, chat_id,
                           duration=self.cfg.get('duration'),
                           aria_ip=self.cfg.get('aria_ip'),
                           sensor_ip=self.cfg.get('sensor_ip'))
                await context.bot.send_message(chat_id=chat_id, text="Done!")
                await query.message.reply_text('Ready for another recording. Press the button below.', reply_markup=self.main_reply_markup)
            except Exception as e:
                await context.bot.send_message(chat_id=chat_id, text=f"An error occurred: {e}")
                await query.message.reply_text('Maybe we can try again?', reply_markup=self.main_reply_markup)
        elif label == 'editing configuration':
            await self.edit_config(update, context)

    async def edit_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        config_path = Path(__file__).parent / 'config.json'
        if not config_path.exists():
            # create default config if missing
            config_path.write_text(json.dumps({"sensor_ip": "", "aria_ip": "", "duration": 0}, indent=2))

        chat_id = update.effective_chat.id

        # load config
        try:
            with open(config_path, 'r') as f:
                self.cfg = json.load(f)
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Failed to load config: {e}")
            await context.bot.send_message(chat_id=chat_id, text='Returning to main menu.', reply_markup=self.main_reply_markup)
            return

        # show current config and present choices
        text = (
            "Current config:\n"
            f"Sensor IP: {self.cfg.get('sensor_ip','')}\n"
            f"Aria IP: {self.cfg.get('aria_ip','')}\n"
            f"Duration: {self.cfg.get('duration','')}\n\n"
            "Which config would you like to change?"
        )
        keyboard = [
            [InlineKeyboardButton("sensor_ip", callback_data='cfg_sensor_ip'),
                InlineKeyboardButton("aria_ip", callback_data='cfg_aria_ip')],
            [InlineKeyboardButton("duration", callback_data='cfg_duration'),
                InlineKeyboardButton("cancel", callback_data='cfg_cancel')]
        ]
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))

        # handler references so we can remove them later
        choice_handler = None
        value_handler = None

        async def handle_choice(inner_update: Update, inner_context: ContextTypes.DEFAULT_TYPE):
            nonlocal choice_handler, value_handler
            query = inner_update.callback_query
            await query.answer()
            if query.data == 'cfg_cancel':
                await query.message.reply_text('Edit cancelled.', reply_markup=self.main_reply_markup)
                # cleanup
                if choice_handler:
                    self.application.remove_handler(choice_handler)
                    self.application.add_handler(self.main_button_handler)
                return

            field_map = {
                'cfg_sensor_ip': 'sensor_ip',
                'cfg_aria_ip': 'aria_ip',
                'cfg_duration': 'duration'
            }

            field = field_map.get(query.data)
            if not field:
                await query.message.reply_text('Unknown selection.', reply_markup=self.main_reply_markup)
                if choice_handler:
                    self.application.remove_handler(choice_handler)
                    self.application.add_handler(self.main_button_handler)
                return

            # Ask for new value
            current = self.cfg.get(field, '')
            if field in ('sensor_ip', 'aria_ip'):
                prompt = f"Current {field}: {current}\nSend the new IP address (or 'cancel')."
            else:
                prompt = f"Current {field}: {current}\nSend the new duration in seconds (positive number) (or 'cancel')."

            await query.message.reply_text(prompt)

            # Prepare a message handler to capture the next text message from this chat
            def chat_filter(message):
                return message.chat.id == chat_id

            async def handle_value(msg_update: Update, msg_context: ContextTypes.DEFAULT_TYPE):
                nonlocal choice_handler, value_handler
                text = msg_update.message.text.strip()
                if text.lower() == 'cancel':
                    await msg_update.message.reply_text('Edit cancelled.', reply_markup=self.main_reply_markup)
                    # cleanup
                    if value_handler:
                        self.application.remove_handler(value_handler)
                    if choice_handler:
                        self.application.remove_handler(choice_handler)
                    self.application.add_handler(self.main_button_handler)
                    return
                    return

                # validate
                if field in ('sensor_ip', 'aria_ip'):
                    try:
                        ipaddress.ip_address(text)
                    except Exception:
                        await msg_update.message.reply_text('Invalid IP address. Please send a valid IP or "cancel".')
                        return
                    self.cfg[field] = text
                else:  # duration
                    try:
                        val = float(text)
                        if val <= 0:
                            raise ValueError()
                    except Exception:
                        await msg_update.message.reply_text('Duration must be a positive number. Send a valid number or "cancel".')
                        return
                    self.cfg[field] = val
                # write back to config
                try:
                    with open(config_path, 'w') as f:
                        json.dump(self.cfg, f, indent=2)
                except Exception as e:
                    await msg_update.message.reply_text(f"Failed to write config: {e}", reply_markup=self.main_reply_markup)
                else:
                    await msg_update.message.reply_text(f"{field} updated successfully.", reply_markup=self.main_reply_markup)

                # cleanup handlers
                if value_handler:
                    self.application.remove_handler(value_handler)
                if choice_handler:
                    self.application.remove_handler(choice_handler)
                self.application.add_handler(self.main_button_handler)

            # add the message handler
            value_handler = MessageHandler(filters.TEXT & filters.Chat(chat_id), handle_value)
            self.application.add_handler(value_handler)

            # remove the choice handler to avoid double-handling
            if choice_handler:
                self.application.remove_handler(choice_handler)
        
        choice_handler = CallbackQueryHandler(handle_choice, pattern='^cfg_')
        self.application.add_handler(choice_handler)
        self.application.remove_handler(self.main_button_handler)
            
if __name__ == '__main__':
    with open('/home/reggev/token.txt', 'r') as file: token = file.read().strip()
    bot = Bot(token)
