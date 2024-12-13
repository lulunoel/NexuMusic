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
        
    @commands.command(name="setlogchannel", help="Définit ou met à jour le canal de logs pour le serveur.")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """Met à jour ou définit le canal de logs pour le serveur dans la base de données."""
        server_id = ctx.guild.id
        server_name = ctx.guild.name
        channel_id = channel.id  
        try:
            with self.db.connection.cursor() as cursor:
                update_query = """
                INSERT INTO server_settings (server_id, server_name, server_log_id)
                VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE server_log_id = %s
                """
                cursor.execute(update_query, (server_id, server_name, channel_id, channel_id))
                self.db.connection.commit()
            await ctx.send(f"Le canal de logs a été défini sur {channel.mention}.")
        except Exception as e:
            await ctx.send(f"Erreur lors de la mise à jour de la base de données: {e}")
            self.db.connection.rollback()
            
    @commands.command(name="setwelcomechannel", help="Définit ou met à jour le canal de bienvenue pour le serveur.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        """Met à jour ou définit le canal de bienvenue pour le serveur dans la base de données."""
        server_id = ctx.guild.id
        server_name = ctx.guild.name
        channel_id = channel.id 

        try:
            with self.db.connection.cursor() as cursor:
                update_query = """
                INSERT INTO server_settings (server_id, server_name, server_welcome_id)
                VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE server_welcome_id = %s
                """
                cursor.execute(update_query, (server_id, server_name, channel_id, channel_id))
                self.db.connection.commit()
            await ctx.send(f"Le canal de bienvenue a été défini sur {channel.mention}.")
        except Exception as e:
            await ctx.send(f"Erreur lors de la mise à jour de la base de données: {e}")
            self.db.connection.rollback()
            
    @commands.command(name="setcountchannel", help="Définit ou met à jour le canal de conteur pour le serveur.")
    @commands.has_permissions(administrator=True)
    async def set_count_channel(self, ctx, channel: discord.TextChannel):
        """Met à jour ou définit le canal de conteur pour le serveur dans la base de données."""
        server_id = ctx.guild.id
        server_name = ctx.guild.name
        channel_id = channel.id 

        try:
            with self.db.connection.cursor() as cursor:
                update_query = """
                INSERT INTO server_settings (server_id, server_name, server_count_id)
                VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE server_count_id = %s
                """
                cursor.execute(update_query, (server_id, server_name, channel_id, channel_id))
                self.db.connection.commit()
            await ctx.send(f"Le canal de conteur a été défini sur {channel.mention}.")
        except Exception as e:
            await ctx.send(f"Erreur lors de la mise à jour de la base de données: {e}")
            self.db.connection.rollback()
            
async def setup(bot):
    await bot.add_cog(SetupCommands(bot))
