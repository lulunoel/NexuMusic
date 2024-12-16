from discord.ext import commands
import discord
import logging
from console_config import setup_console

logger = setup_console('discord')

class DiscordLoggerHandler(commands.Cog):
    """Cog pour logger les commandes utilisées."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None:
            return
        async for entry in message.guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            if entry.target.id == message.author.id:
                logger.info(f"Message de {message.author} supprimé par {entry.user}: {message.content}")
                break
        else:
            logger.info(f"Message de {message.author} supprimé: {message.content}")

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

async def setup(bot):
    await bot.add_cog(DiscordLoggerHandler(bot))
