import logging

from g4f.client import Client

client = Client()


def summarize_order(text):
    try:
        logging.info('summarizing ' + text)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"""
هل يمكنك تلخيص هذا الطلب بالعربي
الرجاء محاولة عرض اصناف الطعام فقط على شكل قائمة باللغة العربية
            
{text}
            """}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(e)
        return None
