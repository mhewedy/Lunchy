import logging

import cache
from util import retry_function

import os
from google import genai
from google.genai import types


def _is_food_gemini(text):
    logging.info(f"calling _is_food_gemini for {text}")

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"Does this full text considered a food name in Arabic or English (answer in English only by yes/no only): {text}"),
            ],
        ),
    ]
    chunks = client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=(types.GenerateContentConfig(
            response_mime_type="text/plain",
        )),
    )
    result = "yes" in next(chunks).text.lower()
    logging.info(f"checking if {text} is food => {result}")
    return result


def is_food(text):
    result = cache.get('food', text)
    if result is not None: return result

    try:
        result = retry_function(_is_food_gemini, text=text)
        return result
    except Exception as e:
        logging.error(e)
        return None
