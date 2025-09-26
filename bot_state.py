import logging
from telegram.ext import CallbackContext
from messages import MessageList

logger = logging.getLogger(__name__)

# How many messages to keep in chat history
MAX_HISTORY = 5

def ensure_chat_state(context: CallbackContext) -> None:
    """Ensure chat_data has required structures for the bot to operate."""
    if "messages" not in context.chat_data:
        context.chat_data["messages"] = MessageList(messages=[])
    if "awaiting_ai" not in context.chat_data:
        context.chat_data["awaiting_ai"] = False

