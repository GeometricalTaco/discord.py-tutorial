from lib.bot import bot
import asyncio
import nest_asyncio
nest_asyncio.apply()


VERSION = "0.0.19"

async def main():
    async with bot:
        await bot.run(VERSION)


asyncio.run(main())
