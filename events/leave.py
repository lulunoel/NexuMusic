from discord.ext import commands
import discord
from database import Database
import os
import datetime
from console_config import setup_console 

logger = setup_console(__name__)
db = Database(
    host=os.getenv("HOST"),
    user=os.getenv("UTILISATEUR"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    port=int(os.getenv("PORT")) 
)

class LeaveHandler(commands.Cog):
    """Gestionnaire global du lancement."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        server = member.guild
        try:
            settings = db.get_server_settings(server.id)
            count_channel_id = settings['server_count_id']
            count_channel = discord.utils.get(server.channels, id=int(count_channel_id))
            
            if count_channel:
                await count_channel.edit(name = f"📜｜{server.member_count} membres", reason = f'Depart de membre')
            else:
                logger.error(f"No count channel found for {server.name}.")                
        except Exception as e:
            logger.error(f"Error handling member join: {e}")

async def setup(bot):
    await bot.add_cog(LeaveHandler(bot))
