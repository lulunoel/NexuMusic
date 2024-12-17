import discord
from discord.ext import commands, tasks
from discord.ui import View, Select
import os
import random
from database import Database
from radios import RADIOS
import json
from console_config import setup_console  
logger = setup_console('ready')
db = Database(
    host=os.getenv("HOST"),
    user=os.getenv("UTILISATEUR"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    port=int(os.getenv("PORT"))
)

class ReadyHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_id = None 

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Bot connecté en tant que {self.bot.user}")
        await self.resume_radios()
        await self.update_status()

    @tasks.loop(minutes=5)
    async def update_status(self):
        status_options = [
            discord.Game(f"sur {len(self.bot.guilds)} serveurs"),
            discord.Streaming(name="la radio sur Nexuria", url="https://nexuria.fr"),
            discord.Activity(type=discord.ActivityType.listening, name="des demandes"),
            discord.Activity(type=discord.ActivityType.watching, name=f"{sum(len(guild.members) for guild in self.bot.guilds)} utilisateurs")
        ]
        await self.bot.change_presence(activity=random.choice(status_options))
    
    async def resume_radios(self):
        for guild in self.bot.guilds:
            settings = db.get_server_settings(guild.id)
            if settings and settings["last_radio"]:
                voice_channels = [vc for vc in guild.voice_channels if vc.permissions_for(guild.me).connect]
                if not voice_channels:
                    logger.info(f"Aucun canal vocal accessible pour le serveur {guild.name}")
                    continue

                channel = voice_channels[0] 
                try:
                    vc = await channel.connect()
                    vc.play(discord.FFmpegPCMAudio(
                        RADIOS[settings["last_radio"]],
                        options=f"-filter:a 'volume={settings['volume']}'"
                    ))
                    logger.info(f"Reprise automatique : {settings['last_radio']} pour {guild.name}")
                except Exception as e:
                   	logger.error(f"Impossible de reprendre la radio pour {guild.name} : {e}")
                    
async def setup(bot):
    await bot.add_cog(ReadyHandler(bot))
