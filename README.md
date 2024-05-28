# Lunchy

A simple Telegram chatbot to suggest who will order the lunch today!

## Deployment

1. Create bot using telegram [@BotFather](https://telegram.me/BotFather)
   see [How to get Telegram Bot Chat ID](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a).
2. Create a telegram group, add the bot to the group, and make it admin.
3. Set the env var `BOT_TOKEN` and `CHAT_ID`. (you get from previous steps, where `CHAT_ID` should refer to
   the group created in prev step).
4. Optionally, if you need to persist the data between restarts, configure `VOLUME_ROOT_FS` to point to path of some
   persistent volume (block or network storage).
5. Run the app using `BOT_TOKEN=<bot_token> CHAT_ID=<chat_id> python main.py`
6. Start sending commands in the group (e.g. `/help`), the bot will detect food names as well (using chatgpt).
7. Enjoy!

> This app built using [telebot](https://github.com/mhewedy/telebot) 
