from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    text:str
    message_id:int
    timestamp:datetime

@dataclass
class MessageResponse:
    response_to_id: int
    text: str

@dataclass
class MessageList:
    messages: list[Message]