import discord
from discord.ext import commands
from database import Database 
import os

class SetupCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(
            host=os.getenv("HOST"),
    		user=os.getenv("UTILISATEUR"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            port=os.getenv("PORT")
        )
        
    async def refresh_settings(self):
        """Rafraîchit la configuration en mémoire pour tous les serveurs."""
        try:
            all_settings = self.db.get_all_server_settings()
            self.settings = {setting['server_id']: setting for setting in all_settings}
        except Exception as e:
            print(f"Erreur lors de la récupération des paramètres: {e}")

    @commands.command(name="setlogchannel", help="Définit ou met à jour le canal de logs pour le serveur.")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        server_id = ctx.guild.id
        log_channel_id = channel.id
        try:
            self.db.set_log_channel(server_id, log_channel_id)
            await ctx.send(f"Le canal de log a été mis à jour avec succès pour le canal: {channel.mention}")
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la mise à jour du canal de log: {e}")

    @commands.command(name="setwelcomechannel", help="Définit ou met à jour le canal de bienvenue pour le serveur.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        server_id = ctx.guild.id
        welcome_channel_id = channel.id
        try:
            self.db.set_welcome_channel(server_id, welcome_channel_id)
            await ctx.send(f"Le canal de bienvenue a été mis à jour avec succès pour le canal: {channel.mention}")
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la mise à jour du canal de bienvenue: {e}")

    @commands.command(name="setcountchannel", help="Définit ou met à jour le canal de compteur pour le serveur.")
    @commands.has_permissions(administrator=True)
    async def set_count_channel(self, ctx, channel: discord.TextChannel):
        server_id = ctx.guild.id
        count_channel_id = channel.id
        try:
            self.db.set_count_channel(server_id, count_channel_id)
            await ctx.send(f"Le canal de compteur a été mis à jour avec succès pour le canal: {channel.mention}")
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la mise à jour du canal de compteur: {e}")

    @commands.command(name="setsuggestionchannel", help="Définit ou met à jour le canal de suggestions pour le serveur.")
    @commands.has_permissions(administrator=True)
    async def set_suggestion_channel(self, ctx, channel: discord.TextChannel):
        server_id = ctx.guild.id
        suggestion_channel_id = channel.id
        try:
            self.db.set_suggestion_channel(server_id, suggestion_channel_id)
            await ctx.send(f"Le canal de suggestions a été mis à jour avec succès pour le canal: {channel.mention}")
        except Exception as e:
            await ctx.send(f"Une erreur est survenue lors de la mise à jour du canal de suggestions: {e}")

            
async def setup(bot):
    await bot.add_cog(SetupCommands(bot))
