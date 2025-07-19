# Lunchy

Lunchy is a smart AI-powered Telegram bot designed to fairly and intelligently choose one person from a chat group to be responsible for ordering lunch. Whether you're tired of the same person ordering every day, or you just want to make lunch assignments more fun, Lunchy has your back.

Built with modular components and optional AI integration (via Google Gemini or ChatGPT), Lunchy uses natural language detection to identify food-related conversations and trigger a fair selection process based on configurable criteria.

## Deployment

1. Create bot using telegram [@BotFather](https://telegram.me/BotFather)
   see [How to get Telegram Bot Chat ID](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a).
2. Create a telegram group, add the bot to the group, and make it admin.
3. Set the env var `BOT_TOKEN` and `CHAT_ID`. (you get from previous steps, where `CHAT_ID` should refer to
   the group created in prev step).
4. if you want to use Google Gemini AI, then obtain and set `GEMINI_API_KEY`
5. Optionally, if you need to persist the data between restarts, configure `VOLUME_ROOT_FS` to point to path of some
   persistent volume (block or network storage).
6. Run the app using `BOT_TOKEN=<bot_token> CHAT_ID=<chat_id> python main.py`
7. Start sending commands in the group (e.g. `/help`), the bot will detect food names as well (using chatgpt).
8. Enjoy!

> This app built using [telebot](https://github.com/mhewedy/telebot) 
