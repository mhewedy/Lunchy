# Lunchy

A simple Telegram chatbot to suggest who will order the lunch today!

## Deployment

1. Create bot using telegram [@botfather](https://telegram.me/BotFather)
   see [How to get Telegram Bot Chat ID](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a)
2. Create a telegram group, add the bot to the group, and make it admin
3. You need to set the env var `BOT_TOKEN` and `CHAT_ID`. (you get from previous steps, where `CHAT_ID` should refer to the group created in prev step)
4. Run the app using `python main.py`.
5. Start sending commands in the group (e.g. `/help`), the bot will detect food names as well (using chatgpt)
6. Enjoy!

> This app uses [telebot](https://github.com/mhewedy/telebot) 
