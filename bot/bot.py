import asyncio
from decouple import config
import logging
from aiogram import Bot, Dispatcher
from handlers import applications

async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config('TOKEN'))
    dp = Dispatcher()

    dp.include_routers(applications.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())