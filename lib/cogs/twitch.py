from discord.ext.commands import Cog
from discord.ext.commands import command


class Twitch(Cog):
	def __init__(self, bot):
		self.bot = bot
		
        
	@Cog.listener()
	async def on_ready(self):
		print(self.bot.ready)
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("twitch")

async def setup(bot):
	await bot.add_cog(Twitch(bot))