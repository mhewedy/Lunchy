import logging

from g4f.client import Client

client = Client()


def summarize_order(text):
    logging.info('summarizing ' + text)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"""
extract food items (in arabic) and give me this food order details as bullet points (in Arabic):
        
{text}
        """}]
    )
    return response.choices[0].message.content
