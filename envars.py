import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # required
HEADS_UP_TIME = os.getenv("HEADS_UP_TIME", "08:00")
SELECTION_TIME = os.getenv("SELECTION_TIME", "09:30")
CHAT_ID = os.getenv("CHAT_ID", -4201961515)

print(f'HEADS_UP_TIME: {HEADS_UP_TIME} UTC')
print(f'SELECTION_TIME: {SELECTION_TIME} UTC')
print(f'G_CHAT_ID: {CHAT_ID}')
