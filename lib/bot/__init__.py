from asyncio import sleep
from datetime import datetime
from glob import glob
from discord import Intents
from discord import Embed, File, DMChannel
from discord.errors import HTTPException, Forbidden
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Bot
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions

from ..db import db


OWNER_IDS = [547395323727708170]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


class Ready(object):
    def __init__(self):
        print("Ready class init")
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        print("ready_up")
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(Bot):
    def __init__(self):
        self.ready = False
        print("self.ready")
        self.cogs_ready = Ready()
        print("self.cogs_ready")

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=get_prefix, 
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    async def setup_hook(self):
        print("running setup..")
        for cog in COGS:
            await self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    async def close(self):
        await super().close()
        await self.session.close()


    def run(self, version):
        self.VERSION = version

        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("I'm not ready to recieve commands. Please wait a few seconds")

    async def rules_reminder(self):
        channel = self.get_channel(908360506610438266)
        await self.stdout.send("Remember to adhere to the rules!")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        channel = self.get_channel(1142556824030167170)
        await self.stdout.send("An error occured.")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif hasattr(exc, "original"):
            raise exc

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing.")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")

        elif isinstance(exc.original, Forbidden):
            await ctx.send("I do not have permission to do that.")

        elif isinstance(exc.original, HTTPException):
            await ctx.send("Unable to send message.")

        else:
            raise exc.original

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(1137356223646273588)
            print(self.guild)
            self.stdout = self.get_channel(1142556824030167170)
            print(self.stdout)
            ##self.scheduler.add_job(self.print_message, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()

            print("hi")
            while not self.cogs_ready.all_ready():
                print("eepy")
                await sleep(0.5)
            print("hi again")

            await self.stdout.send("Now online!")
            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                if len(message.content) < 50:
                    await message.channel.send("Your message should be at least 50 characters in length")

                else:
                    member = self.guild.get_member(message.author.id)
                    embed = Embed(title="Modmail",
                                  colour=member.colour,
                                  timestamp=datetime.utcnow())

                    embed.set_thumbnail(url=member.avatar)

                    fields = [("Member", member.display_name, False),
                              ("Message", message.content, False)]

                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)

                    self.log_channel = self.get_channel(1142556824030167170)

                    await self.log_channel.send(embed=embed)
                    await message.channel.send("Message relayed to moderators")

            else:
                await self.process_commands(message)


bot = Bot()



## commands in progress:
## -spinning zhongli gif
## -todo list for tsu
## -automatic clip sending?? need to check twitch api