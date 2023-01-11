import discord, os, json
from discord.ext import commands


class MyBot(commands.Bot):
    def __init__(self):
        with open("./json/config.json", "r") as f:
            config = json.load(f)
        super().__init__(
            command_prefix=f"{config['prefix']}",
            intents=discord.Intents.all(),
            application_id=config['application_id']
        )

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
        await bot.tree.sync()

    async def on_ready(self):
        print('Logged in!')


bot = MyBot()
with open("./json/config.json", "r") as f:
    config = json.load(f)
bot.run(config['discord_token'])
