from asyncio import sleep
from datetime import datetime
from glob import glob
from discord import Intents
from discord import Embed, File
from discord.errors import HTTPException, Forbidden
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Bot as BotBase
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
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=get_prefix, 
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")


    def run(self, version):
        self.VERSION = version

        print("running setup..")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
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

        channel = self.get_channel(908360506610438266)
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
            self.guild = self.get_guild(899636129698033694)
            self.stdout = self.get_channel(908360506610438266)
            #self.scheduler.add_job(self.print_message, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()


            # embed = Embed(title="Now online!", description="Umbral Stars is now online.", 
            #               colour=0xFF0000, timestamp=datetime.utcnow())
            # fields = [("Name", "Value", True),
            #           ("Another field", "This field is next to the other one.", True),
            #           ("A non-inline field", "This field will appear on its own row.", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Thomas Whettam", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is a footer")
            # embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)
            # await channel.send(embed=embed)

            # await channel.send(file=File("./data/images/image1.png"))

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("Now online!")
            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
