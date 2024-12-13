import discord
from discord.ext import commands
import os
from database import Database
import datetime


class Invite(commands.Cog):
    """Commandes pour la gestion des serveurs."""

    def __init__(self, bot):
        self.bot = bot
        self.db = Database(
            host=os.getenv("HOST"),
            user=os.getenv("UTILISATEUR"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            port=os.getenv("PORT"),
        )

    @commands.command(name="invitations", help="Affiche toutes les invitations actives du serveur.")
    async def show_invitations(self, ctx):
        """Affiche les invitations actives dans le serveur."""
        invites = await ctx.guild.invites()
        embed = discord.Embed(
            title="📨 Invitations Actives",
            description=f"Liste des invitations actives pour le serveur {ctx.guild.name}.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow(),
        )

        if not invites:
            embed.description = "Aucune invitation active pour ce serveur."
        else:
            for invite in invites:
                inviter = invite.inviter.mention if invite.inviter else "Inconnu"
                embed.add_field(
                    name=f"Code : `{invite.code}`",
                    value=f"👤 **Inviteur** : {inviter}\n🔄 **Utilisations** : {invite.uses}",
                    inline=False,
                )

        embed.set_footer(text="Commandé par " + str(ctx.author), icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="who_invited", help="Montre qui a invité un utilisateur.")
    async def who_invited(self, ctx, member: discord.Member):
        guild_id = ctx.guild.id
        user_id = member.id

        try:
            # Requête pour trouver l'invitation utilisée et son créateur
            query = """
            SELECT i.inviter_id, COUNT(iu.user_id) AS invite_count
            FROM invite_uses iu
            JOIN invites i ON iu.invite_code = i.invite_code
            WHERE iu.user_id = %s AND iu.guild_id = %s
            GROUP BY i.inviter_id;
            """
            self.db.cursor.execute(query, (user_id, guild_id))
            result = self.db.cursor.fetchone()

            if result:
                inviter_id = result["inviter_id"]
                invite_count = result["invite_count"]

                inviter = ctx.guild.get_member(inviter_id)
                embed = discord.Embed(
                    title="👤 Invitation Info",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.utcnow(),
                )

                if inviter:
                    embed.description = (
                        f"{member.mention} a été invité par **{inviter.mention}**.\n"
                        f"**{inviter.mention}** a actuellement invité **{invite_count}** personne(s)."
                    )
                else:
                    embed.description = (
                        f"{member.mention} a été invité par un utilisateur qui n'est plus sur ce serveur.\n"
                        f"Cet utilisateur a invité **{invite_count}** personne(s)."
                    )
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=discord.Embed(
                    description=f":x: Impossible de trouver qui a invité {member.mention}.",
                    color=discord.Color.red(),
                ))
        except Exception as e:
            print(f"[ERREUR] who_invited: {e}")
            await ctx.send(embed=discord.Embed(
                description=":x: Une erreur s'est produite lors de l'exécution de la commande.",
                color=discord.Color.red(),
            ))

    @commands.command(name="invite_count", help="Montre combien de personnes un utilisateur a invité.")
    async def invite_count(self, ctx, member: discord.Member):
        guild_id = ctx.guild.id
        inviter_id = member.id

        try:
            query = """
            SELECT COUNT(iu.user_id) AS invite_count
            FROM invite_uses iu
            JOIN invites i ON iu.invite_code = i.invite_code
            WHERE i.inviter_id = %s AND i.guild_id = %s;
            """
            self.db.cursor.execute(query, (inviter_id, guild_id))
            result = self.db.cursor.fetchone()

            embed = discord.Embed(
                title="📊 Invitations Compte",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.utcnow(),
            )

            if result and result["invite_count"] > 0:
                invite_count = result["invite_count"]
                embed.description = f"👤 {member.mention} a invité **{invite_count}** personne(s) sur ce serveur."
            else:
                embed.description = f"👤 {member.mention} n'a invité personne sur ce serveur."
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"[ERREUR] invite_count: {e}")
            await ctx.send(embed=discord.Embed(
                description=":x: Une erreur s'est produite lors de l'exécution de la commande.",
                color=discord.Color.red(),
            ))


async def setup(bot):
    await bot.add_cog(Invite(bot))
