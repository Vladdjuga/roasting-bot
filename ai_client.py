import logging
import os

from dotenv import load_dotenv
from gradio_client import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
api_key=os.environ.get('HF_READ_TOKEN')

client = Client("vladdjuga/PrikolistRoastBot",hf_token=api_key)

# To prevent concurrent calls to the AI client
is_calling=False

def call_ai_client(payload):
    logger.info("Calling AI client")

    global is_calling # Use the global variable
    if is_calling:
        logger.warning("AI client is already being called. Please wait.")
        return "AI client is busy. Please try again later."
    is_calling=True

    result = client.predict(
        messages_batch=payload,
        maximum_tokens=1024,
        temp=0.6,
        nucleus=0.95,
        api_name="/respond_with_reasoning"
    )

    is_calling=False
    logger.info(f"AI client returned: {result}")
    # result[0] is the models reasoning, result[1] is the text/json response
    return result[1] # return only the text part of the response


