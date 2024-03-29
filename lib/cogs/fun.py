from random import choice, randint
from typing import Optional

from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown


class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="hello", aliases=["hi"])
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}!")

	@command(name="zhongli")
	async def zhongli(self, ctx):
		await ctx.send("https://tenor.com/view/zhongli-spin-fly-gif-23152749")

	# must be +roll 1d6 for example
	@command(name="dice", aliases=["roll"])
	async def roll_dice(self, ctx, die_string: str):
		dice, value = (int(term) for term in die_string.split("d"))

		if dice <= 25:
			rolls = [randint(1, value) for i in range(dice)]

			await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

		else:
			await ctx.send("I can't roll that many dice. Please try a lower number.")

	@command(name="slap", aliases=["hit"])
	async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
		await ctx.send(f"{ctx.author.mention} slapped {member.mention} {reason}!") #ctx.author.displayname to not mention self/other user

	@slap_member.error
	async def slap_member_error(self, ctx, exc):
		if isinstance(exc, BadArgument):
			await ctx.send("I can't find that member")

	@command(name="echo", aliases=["say"])
	async def echo_message(self, ctx, *, message):
		await ctx.message.delete()
		await ctx.send(message)

	# @command(name="fact")
	# async def animal_fact(self, ctx, animal: str):
	# 	if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
	# 		FACT_URL = f"https://some-random-api.ml/facts/{animal}"
	# 		print(FACT_URL)
	# 		IMAGE_URL = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"
	# 		print(IMAGE_URL)

	# 		async with request("GET", IMAGE_URL, headers={}) as response:
	# 			print(response.status)
	# 			if response.status == 200:
	# 				print("status 200 image request block")
	# 				print(response)
	# 				data = await response.json()
	# 				print("data part")
	# 				print(data)
	# 				image_link = data["link"]
					

	# 			else:
	# 				image_link = None

	# 		async with request("GET", FACT_URL, headers={}) as response:
	# 			print(response.status)
	# 			if response.status == 200:
	# 				print("status 200 fact request block")
	# 				data = await response.json()

	# 				embed = Embed(title=f"{animal.title()} fact",
	# 							  description=data["fact"],
	# 							  colour=self.ctx.author.colour)
	# 				if image_link is not None:
	# 					embed.set_image(url=image_link)
	# 				await ctx.send(embed=embed)

	# 			else:
	# 				await ctx.send(f"API returned a {response.status} status.")
	# 	else:
	# 		await ctx.send("No facts are available for that animal.")

	@Cog.listener()
	async def on_ready(self):
		print(self.bot.ready)
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")


async def setup(bot):
	await bot.add_cog(Fun(bot))