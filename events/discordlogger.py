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
        logger.info(f'Message supprimé par {message.author}: {message.content}')

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        logger.info(f'Masse suppression: {len(messages)}')

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
