import discord
from discord.ext import commands
from database import Database
import datetime
import os

class InviteManager(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.invites_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        """Charge toutes les invitations existantes au démarrage."""
        for guild in self.bot.guilds:
            self.invites_cache[guild.id] = await guild.invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        """Ajoute une nouvelle invitation dans la base de données."""
        self.db.cursor.execute(
            """
            INSERT INTO invites (invite_code, inviter_id, guild_id)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE inviter_id = VALUES(inviter_id)
            """,
            (invite.code, invite.inviter.id, invite.guild.id)
        )
        self.db.connection.commit()
        self.invites_cache[invite.guild.id] = await invite.guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Détecte quelle invitation a été utilisée par le membre."""
        cached_invites = self.invites_cache.get(member.guild.id, [])
        current_invites = await member.guild.invites()

        used_invite = None
        for invite in cached_invites:
            matching_invite = next((i for i in current_invites if i.code == invite.code), None)
            if matching_invite and invite.uses < matching_invite.uses:
                used_invite = invite
                break

        self.invites_cache[member.guild.id] = current_invites

        if used_invite:
            self.db.cursor.execute(
                """
                INSERT INTO invite_uses (user_id, invite_code, guild_id)
                VALUES (%s, %s, %s)
                """,
                (member.id, used_invite.code, member.guild.id)
            )
            self.db.connection.commit()

            inviter = await member.guild.fetch_member(used_invite.inviter.id)
            await member.guild.system_channel.send(
                f"🎉 {member.mention} a été invité par {inviter.mention} en utilisant le code `{used_invite.code}`."
            )
        else:
            await member.guild.system_channel.send(
                f"🎉 {member.mention} a rejoint le serveur, mais l'invitation utilisée n'a pas pu être déterminée."
            )

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        """Met à jour le cache lorsque des invitations sont supprimées."""
        self.invites_cache[invite.guild.id] = await invite.guild.invites()

async def setup(bot):
    db = Database(
        host=os.getenv("HOST"),
        user=os.getenv("UTILISATEUR"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        port=os.getenv("PORT")
    )
    await bot.add_cog(InviteManager(bot, db))
