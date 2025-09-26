import json
from dataclasses import asdict
import logging
from typing import Optional

from messages import MessageList, MessageResponse

logger = logging.getLogger(__name__)


def build_payload(message_list: MessageList) -> str:
    """Serialize MessageList to JSON for the AI client."""
    return json.dumps(asdict(message_list), ensure_ascii=False, default=str)


def parse_ai_response(response: str) -> Optional[MessageResponse]:
    """Parse AI response JSON into MessageResponse. Return None if invalid."""
    try:
        message_resp = json.loads(response)
        # Defensive extraction with type coercion for response_to_id
        resp_to = message_resp.get("response_to_id")
        try:
            resp_to = int(resp_to) if resp_to is not None else None
        except (TypeError, ValueError):
            logger.warning("response_to_id not convertible to int: %s", resp_to)
            resp_to = None
        text = message_resp.get("text")
        if resp_to is None or not isinstance(text, str):
            logger.warning("AI response missing required fields: %s", message_resp)
            return None
        return MessageResponse(response_to_id=resp_to, text=text)
    except json.JSONDecodeError:
        logger.warning("AI response is not valid JSON: %s", response[:200])
        return None

