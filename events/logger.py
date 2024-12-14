import discord
from discord.ext import commands
from database import Database
import os
import datetime
from console_config import setup_console

logger = setup_console('Log')
db = Database(
    host=os.getenv("HOST"),
    user=os.getenv("UTILISATEUR"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    port=os.getenv("PORT")
)

class LoggerHandler(commands.Cog):
    """Cog pour logger les commandes utilisées."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        command = ctx.command 
        description = ctx.command.help  
        args = ctx.current_argument  
        args = args if args is not None else " "
        user = ctx.author  
        server = ctx.guild  
        settings = db.get_server_settings(server.id)
        prefix = self.bot.command_prefix
        if command:
            logger.info(f"Une commande: {command} a été exécutée par: {user} (ID: {user.id}) sur le serveur: {server} (ID: {server.id})")
            log_channel_id = settings['server_log_id']
            log_channel = discord.utils.get(server.channels, id=int(log_channel_id))
            
            if log_channel:
                embed = discord.Embed(title="Commande utilisée", color=discord.Color.red(), timestamp=datetime.datetime.now())
                embed.add_field(name="Utilisateur", value=f"{user} (ID: {user.id})", inline=False)
                embed.add_field(name="Commande", value=prefix + str(command) + " " + str(args), inline=False)
                embed.add_field(name="Description", value=str(description), inline=False)
                embed.add_field(name="Serveur", value=f"{server} (ID: {server.id})", inline=False)
                embed.set_thumbnail(url=user.avatar.url)
                await log_channel.send(embed=embed)
            else:
                logger.error(f"No log channel found for {server.name}.")

async def setup(bot):
    await bot.add_cog(LoggerHandler(bot))
