import asyncio
import logging

from telegram import Update
from telegram.ext import CallbackContext

import ai_client
from messages import Message, MessageList
from bot_state import ensure_chat_state, MAX_HISTORY
from ai_response import build_payload, parse_ai_response

logger = logging.getLogger(__name__)

is_bot_active = False

async def error_handler(update: Update, context: CallbackContext):
    logger.error("Exception while handling update:", exc_info=context.error)
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="An error occurred. Please try to restart the bot."
        )


async def start(update: Update, context: CallbackContext):
    global is_bot_active
    if is_bot_active:
        await update.message.reply_text("Я уже запущен и готов к работе! 🤖")
        return
    is_bot_active = True
    await update.message.reply_text("Йоу! Я живой 🤖")
    # Initialize chat state explicitly
    context.chat_data["messages"] = MessageList(messages=[])
    context.chat_data["awaiting_ai"] = False

async def end(update: Update, context: CallbackContext):
    global is_bot_active
    if not is_bot_active:
        await update.message.reply_text("Я и так не запущен. 🤖")
        return
    is_bot_active = False
    await update.message.reply_text("Пока! Если что, я тут 🤖")
    # Clear chat state
    context.chat_data.clear()


async def trigger_ai_if_needed(update: Update, context: CallbackContext):
    """If history exceeds MAX_HISTORY, call AI and send reply. Runs blocking call in a thread."""
    ensure_chat_state(context)
    msgs = context.chat_data["messages"].messages
    if len(msgs) > MAX_HISTORY:
        if context.chat_data.get("awaiting_ai"):
            logger.info("Already awaiting AI response; skip triggering.")
            return
        logger.info("Message threshold exceeded. Preparing to call AI client...")
        # Prepare payload first
        payload = build_payload(context.chat_data["messages"])
        logger.info("Message appended to chat history: %s", payload)

        # Clear old messages to keep history manageable
        context.chat_data["messages"].messages = []

        # Mark that we're awaiting an AI response
        context.chat_data["awaiting_ai"] = True

        chat_id = update.effective_chat.id
        # Execute blocking AI call in a background thread
        try:
            response = await asyncio.to_thread(ai_client.call_ai_client, payload)
        except Exception as e:
            logger.exception("AI client call failed: %s", e)
            context.chat_data["awaiting_ai"] = False
            await context.bot.send_message(chat_id=chat_id, text="AI service error. Please try again later.")
            return

        # Handle AI saying it's busy (aiclient returns a plain string in that case)
        if isinstance(response, str) and response.startswith("AI client is busy"):
            logger.info("AI client busy. Not sending a reply.")
            context.chat_data["awaiting_ai"] = False
            await context.bot.send_message(chat_id=chat_id, text="I'm a bit busy right now. Try again in a moment.")
            return

        message_response_obj = parse_ai_response(response)
        context.chat_data["awaiting_ai"] = False
        if not message_response_obj:
            logger.warning("Could not parse AI response; skipping send.")
            await context.bot.send_message(chat_id=chat_id, text="Couldn't parse AI response. Please try again.")
            return

        # Add AI response to history
        ai_msg = Message(
            text=message_response_obj.text,
            message_id=message_response_obj.response_to_id,
            timestamp=update.message.date
        )
        context.chat_data["messages"].messages.append(ai_msg)

        await context.bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=message_response_obj.response_to_id,
            text=message_response_obj.text
        )



async def on_text(update: Update, context: CallbackContext):
    global is_bot_active
    if not is_bot_active:
        return
    if not update.message or not update.effective_chat:
        return

    ensure_chat_state(context)

    user = update.effective_user
    message = update.message
    if user.is_bot:
        return
    # Check first if the message is text message
    if not update.message.text:
        return
    text = update.message.text
    logger.info("Message from %s: %s", user.id if user else "?", text)

    # If we're awaiting an AI response, don't add anything to the history
    if context.chat_data.get("awaiting_ai"):
        logger.info("Awaiting AI response; not appending new messages to history.")
        return

    if context.chat_data.get("messages"):
        msg=Message(
            text=text,
            message_id=message.id,
            timestamp=update.message.date
        )
        context.chat_data["messages"].messages.append(msg)

        # Potentially trigger AI after appending
        await trigger_ai_if_needed(update, context)
