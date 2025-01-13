from discord.ext import commands
import discord
import logging
from console_config import setup_console
from database import Database
import os
import asyncio
import logging
from console_config import setup_console
logger = setup_console('discord')
db = Database(
    host=os.getenv("HOST"),
    user=os.getenv("UTILISATEUR"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    port=int(os.getenv("PORT"))
)

class DiscordLoggerHandler(commands.Cog):
    """Cog pour logger les commandes utilisées."""

    def __init__(self, bot):
        self.bot = bot
        self.message_cooldowns = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None:
            return
        async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            if entry.target.id == message.author.id:
                logger.info(f"Message de {message.author} supprimé par {entry.user}: {message.content}")
                db.remove_points(str(message.author.id), str(message.guild.id), 5)
                break
        else:
            logger.info(f"Message de {message.author} supprimé: {message.content}")
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        
        user_id = (message.author.id, message.guild.id)
        if user_id in self.message_cooldowns:
            return
        logger.info(f"Message de {message.author} envoyer: {message.content}")

        db.add_points(str(message.author.id), str(message.guild.id), 5)
        self.message_cooldowns[user_id] = True
        await asyncio.sleep(30)
        del self.message_cooldowns[user_id]
        
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if messages[0].guild is None:  
            return
        async for entry in messages[0].guild.audit_logs(limit=1, action=discord.AuditLogAction.message_bulk_delete):
            logger.info(f"Masse suppression: {len(messages)} messages par {entry.user}")
            break
        else:
            logger.info(f'Masse suppression: {len(messages)} messages')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            removed = [role.name for role in before.roles if role not in after.roles]
            added = [role.name for role in after.roles if role not in before.roles]
            logger.info(f'Roles editée pour {after.name}: Ajout: {added}, Retrait: {removed}')
                
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        logger.info(f'Role crée: {role.name}')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        logger.info(f'Role supprimée: {role.name}')

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if before.permissions != after.permissions:
            logger.info(f'Role permissions éditée pour {after.name}: de {before.permissions} à {after.permissions}')
        if before.name != after.name:
            logger.info(f'Role nom changée pour {before.name} à {after.name}')
            
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        logger.info(f"{user} à été banni de {guild.name}")
        db.remove_points(str(user.id), str(guild.id), 60)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        logger.info(f"{user} à été débanni de {guild.name}")
        
async def setup(bot):
    await bot.add_cog(DiscordLoggerHandler(bot))
