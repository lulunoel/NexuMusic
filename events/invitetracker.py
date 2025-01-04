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

        embed = discord.Embed(
            title="🎉 Nouveau Membre",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Membre", value=member.mention, inline=False)

        if used_invite:
            query = """
            SELECT COUNT(*) as count
            FROM invite_uses
            WHERE user_id = %s AND invite_code = %s AND guild_id = %s
            """
            self.db.cursor.execute(query, (member.id, used_invite.code, member.guild.id))
            result = self.db.cursor.fetchone()

            if result and result["count"] == 0:
                self.db.cursor.execute(
                    """
                    INSERT INTO invite_uses (user_id, invite_code, guild_id)
                    VALUES (%s, %s, %s)
                    """,
                    (member.id, used_invite.code, member.guild.id)
                )
                self.db.connection.commit()

                inviter = await member.guild.fetch_member(used_invite.inviter.id)
                embed.add_field(
                    name="Invité par",
                    value=f"{inviter.mention} (Code : `{used_invite.code}`)",
                    inline=False,
                )
                self.db.add_points(str(member.id), str(member.guild.id), 0)
                self.db.add_points(str(inviter.id), str(member.guild.id), 100)
            else:
                embed.add_field(
                    name="Information",
                    value="Le membre a réutilisé une invitation, aucun changement enregistré.",
                    inline=False,
                )
        else:
            embed.add_field(
                name="Information",
                value="Impossible de déterminer l'invitation utilisée.",
                inline=False,
            )

        await member.guild.system_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        """Met à jour le cache lorsque des invitations sont supprimées."""
        self.invites_cache[invite.guild.id] = await invite.guild.invites()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Gère le départ d'un membre."""
        query = """
        SELECT iu.invite_code, i.inviter_id 
        FROM invite_uses iu
        JOIN invites i ON iu.invite_code = i.invite_code
        WHERE iu.user_id = %s AND iu.guild_id = %s
        """
        self.db.cursor.execute(query, (member.id, member.guild.id))
        result = self.db.cursor.fetchone()

        embed = discord.Embed(
            title="👋 Départ d'un membre",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Membre parti", value=f"{member.mention}", inline=False)

        if result:
            invite_code = result["invite_code"]
            inviter_id = result["inviter_id"]
            inviter = member.guild.get_member(inviter_id)

            if inviter:
                embed.add_field(
                    name="Invité par",
                    value=f"{inviter.mention} (Code: `{invite_code}`)",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Invité par",
                    value=f"Utilisateur inconnu (Code: `{invite_code}`)",
                    inline=False
                )
        else:
            embed.add_field(
                name="Invité par",
                value="Impossible de déterminer l'invitation utilisée.",
                inline=False
            )

        await member.guild.system_channel.send(embed=embed)


async def setup(bot):
    db = Database(
        host=os.getenv("HOST"),
        user=os.getenv("UTILISATEUR"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
        port=os.getenv("PORT")
    )
    await bot.add_cog(InviteManager(bot, db))
