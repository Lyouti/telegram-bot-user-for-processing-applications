import asyncio
from decouple import config
import logging
from aiogram import Bot, Dispatcher
from handlers import applications
import logging
import os

async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, 'my_log.log')
    logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode="w", encoding='utf-8')

    bot = Bot(token=config('TOKEN'))
    dp = Dispatcher()

    dp.include_routers(applications.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())