# Telegram Roast Bot

A Telegram bot that collects recent chat messages, sends them to an AI model, and replies with a roast. The bot:
- Keeps a short sliding window of recent messages per chat
- Avoids appending while waiting for the AI response (per-chat `awaiting_ai` flag)
- Calls a Gradio AI endpoint in a background thread to keep the bot responsive

## Project structure

- `main.py` – App bootstrap: loads env vars, builds the Telegram app, registers handlers
- `handlers.py` – All Telegram handlers and AI trigger logic (`/start`, text messages, error handler)
- `bot_state.py` – Per-chat state helpers: `ensure_chat_state`, `MAX_HISTORY`
- `ai_response.py` – Payload building and AI response parsing helpers
- `aiclient.py` – Gradio client and the synchronous `call_ai_client` function (with a global concurrency guard)
- `messages.py` – Dataclasses for message types shared across modules

## Requirements

- Python 3.10+
- A Telegram bot token in `.env` as `TELEGRAM_API_KEY`
- A Hugging Face token in `.env` as `HF_READ_TOKEN`

Create a `.env` file in the project root:

```
TELEGRAM_API_KEY=123456:abcdef-your-token
HF_READ_TOKEN=hf_xxx_your_token
```

## Install & run (Windows cmd.exe)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Notes
- The bot maintains a per-chat `awaiting_ai` flag and ignores new text while the AI response is in-flight.
- History is trimmed to `MAX_HISTORY` messages before calling the AI.
- If the AI endpoint is busy or returns invalid JSON, the bot sends a friendly message and resets the flag.

