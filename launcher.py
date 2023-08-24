from lib.bot import bot
import asyncio

VERSION = "0.0.19"

async def main():
    async with bot:
        await bot.run(VERSION)


asyncio.run(main())
