import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from handlers import start, on_text, error_handler, end

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.environ.get('TELEGRAM_API_KEY')

if __name__ == "__main__":
    if not api_key:
        raise RuntimeError("TELEGRAM_API_KEY is not set in environment")

    app = Application.builder().token(api_key).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("end", end))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(error_handler)

    app.run_polling()