import logging

import g4f.models
from g4f.client import Client

from util import retry_function

client = Client()


def _is_food(text):
    logging.info(f"calling is_food for {text}")

    request = f"Does this text contain food (Arabic/English) name (answer in English only by yes/no only): {text}"
    response = client.chat.completions.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": request}],
    )
    logging.info(f"request: {request}, response: {response.choices[0].message.content}")
    result = "yes" in response.choices[0].message.content.lower()
    logging.info(f"checking if {text} is food => {result}")
    return result


def is_food(text):
    try:
        return retry_function(_is_food, text=text)
    except Exception as e:
        logging.error(e)
        return False
