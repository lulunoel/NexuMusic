import discord
from discord.ext import commands
import os
from database import Database
import datetime

class Server(commands.Cog):
    """Commandes pour la gestion des serveurs."""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database(
            host=os.getenv("HOST"),
    		user=os.getenv("UTILISATEUR"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            port=os.getenv("PORT")
        )
    @commands.command(name="serverinfo", help="Affiche les informations du serveur.")
    async def server_info(self, ctx):
        guild = ctx.guild
        settings = self.db.get_server_settings(guild.id)
        embed = discord.Embed(title="Informations sur le serveur", url=f"https://discord.com/channels/{guild.id}", color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon)
        embed.add_field(name="Nom", value=guild.name)
        embed.add_field(name="Nombre de membres", value=guild.member_count)
        embed.add_field(name="Propriétaire", value=f"<@{guild.owner_id}>")
        embed.add_field(name="Créé le", value=guild.created_at.strftime('%d/%m/%Y'))
        embed.add_field(name="Volume", value=settings["volume"])
        embed.add_field(name="Radio", value=settings["last_radio"])
        embed.set_footer(text=f"ID du serveur : {guild.id}")
        embed.add_field(name="Niveau de boost", value=f"{guild.premium_tier}/3")
        embed.add_field(name="Nombre de boost", value=guild.premium_subscription_count)
        rules_channel = guild.rules_channel
        if rules_channel:
            embed.add_field(name="Channel règlement", value=f"<#{rules_channel.id}>", inline=False)
        else:
            embed.add_field(name="Channel règlement", value="Pas de channel de règlement défini", inline=False)
        embed.add_field(name="Emoji", value=f"{len(guild.emojis)}/{guild.emoji_limit}")
        embed.add_field(name="Stickers", value=f"{len(guild.stickers)}/{guild.sticker_limit}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Server(bot))
