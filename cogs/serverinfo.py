import json, discord, aiohttp
from discord.ext import commands, tasks
from discord.utils import get

class ServerInfo(commands.Cog):
    def __init__(self, client):
        print("ServerInfo has been initiated")
        self.client = client
        self.embed_msg = 0
    
    with open("./json/config.json", "r") as f:
       config = json.load(f)
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.status.start()
        
    @tasks.loop(seconds=30)
    async def status(self):
        url = f"https://api.battlemetrics.com/servers/{self.config['server']}?include=player"
        
        async with aiohttp.ClientSession(headers={"Authorization": f"Bearer {self.config['bmtoken']}"}) as session:
            async with session.get(url=url) as r:
                response = await r.json()
        players_online = response['data']['attributes']['players']
        max_players = response['data']['attributes']['maxPlayers']
        queue = response['data']['attributes']['details']['squad_publicQueue']
        queue_limit = response['data']['attributes']['details']['squad_publicQueueLimit']
        map = response['data']['attributes']['details']['map']
        map = map.replace("_", " ")

        countrycodes = ["USA", "MEA", "RUS", "INS", "AUS", "CAF", "GB", "USMC", "PLA", "MIL"]
        
        teamone = response['data']['attributes']['details']['squad_teamOne']
        teamone = teamone.split("_")
        for team in teamone:
            if team in countrycodes:
                teamone = team
                break
        teamone_players = "None"

        teamtwo = response['data']['attributes']['details']['squad_teamTwo']
        teamtwo = teamtwo.split("_")
        for team in teamtwo:
            if team in countrycodes:
                teamtwo = team
                break
        teamtwo_players = "None"

        for i in response['included']:
            player_name= i['attributes']['name']
            meta = i['meta']['metadata']
            for a in meta:
                if a['key'] == "teamID":
                    if a['value'] == 1:
                        if teamone_players == "None":
                            teamone_players = f"{player_name}"
                        else:
                            teamone_players += f"\n{player_name}"
                    else:
                        if teamtwo_players == "None":
                            teamtwo_players = f"{player_name}"
                        else:
                            teamtwo_players += f"\n{player_name}"
        chosen_color = await self.chosencolor(self.config['color'])
        StatusEmbed = discord.Embed(title="NoD Server Status \nNoD [ENG] #1 | discord.nodsquad.net", color = chosen_color)
        StatusEmbed.add_field(name='Players', value=f"```{players_online} / {max_players}```", inline=True)
        StatusEmbed.add_field(name='Queue', value=f"```{queue} / {queue_limit}```", inline=True)
        StatusEmbed.add_field(name='Layer', value=f"```{map}```", inline=False)
        StatusEmbed.add_field(name=f'Team One | {teamone}', value=f"```{teamone_players}```", inline=True)
        StatusEmbed.add_field(name=f'Team Two | {teamtwo}', value=f"```{teamtwo_players}```", inline=True)
        StatusEmbed.set_thumbnail(url=self.config['thumbnail'])
        channel = discord.utils.get(self.client.get_all_channels(), id=self.config['channel'])
        if self.embed_msg:
            msg = await channel.fetch_message(self.embed_msg)
            await msg.edit(embed=StatusEmbed)
        else:
            msg = await channel.send(embed=StatusEmbed)
            self.embed_msg = msg.id
            
    async def chosencolor(self, color)-> int:
        with open('./json/colors.json', 'r') as f:
            colors = json.load(f)
        if color == "white":
            return colors[color]
        chosen_color = int(colors[color], base=16)
        return chosen_color
    
async def setup(client):
    await client.add_cog(ServerInfo(client))