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

class JoinHandler(commands.Cog):
    """Gestionnaire global des join."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        server = member.guild
        try:
            settings = db.get_server_settings(server.id)
            welcome_channel_id = settings['server_welcome_id']
            welcome_channel = discord.utils.get(server.channels, id=int(welcome_channel_id))
            
            count_channel_id = settings['server_count_id']
            count_channel = discord.utils.get(server.channels, id=int(count_channel_id))
            
            if welcome_channel:
                embed = discord.Embed(title="Bienvenue sur Nexuria", url="https://nexuria.fr", color=discord.Color.orange(), timestamp=datetime.datetime.now())
                embed.set_thumbnail(url=server.icon.url if server.icon else self.bot.user.display_avatar.url)
                embed.description = (f"Bienvenue à toi, <@{member.id}> sur Nexuria !\nVous êtes le {server.member_count}ème membre du discord !\n\nRejoins-nous vite sur: PLAY.NEXURIA.FR")
                embed.set_footer(
                    text="© Nexuria ▫️ 2024",
                    icon_url=member.avatar.url if member.avatar else self.bot.user.display_avatar.url
                )
                await welcome_channel.send(embed=embed)
            else:
                logger.error(f"Aucun channel de log pour: {server.name}.")
                
            if count_channel:
                await count_channel.edit(name = f"📜｜{server.member_count} membres", reason = f'Nouveau membre')
            else:
                logger.error(f"Aucun channel count trouvée {server.name}.")
                
        except Exception as e:
            logger.error(f"Membre qui a rejoint: {e}")

async def setup(bot):
    await bot.add_cog(JoinHandler(bot))
