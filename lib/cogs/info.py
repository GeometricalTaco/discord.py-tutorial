from datetime import datetime
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog
from discord.ext.commands import command

class Info(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="userinfo", aliases=["memberinfo", "mi", "ui"])
	async def user_info(self, ctx, target: Optional[Member]):
		target = target or ctx.author

		embed = Embed(title="User Information",
					  colour=target.colour,
					  timestamp=datetime.utcnow())

		fields = [("ID", target.id, False),
				  ("Name", str(target), True),
				  ("Bot?", target.bot, True),
				  ("Top role", target.top_role.mention, True),
				  ("Status", str(target.status).title(), True),
				  #("Activity", f"{str(target.activity.type).split('.')[-1].title()} {target.activity.name}", True),
				  ("Created at", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Joined at", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Boosted", bool(target.premium_since), True)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		embed.set_thumbnail(url=target.avatar_url)

		await ctx.send(embed=embed)

	@command(name="serverinfo", aliases=["guildinfo", "si", "gi"])
	async def server_info(self, ctx):
		pass
		embed.set_thumbnail(url=ctx.guild.icon_url)

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("info")


def setup(bot):
	bot.add_cog(Info(bot))