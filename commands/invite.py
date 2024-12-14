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
            description=f"Voici la liste des invitations actives pour le serveur **{ctx.guild.name}**.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow(),
        )

        if not invites:
            embed.description = "🔍 **Aucune invitation active n'a été trouvée sur ce serveur.**"
        else:
            for invite in invites:
                inviter = invite.inviter.mention if invite.inviter else "Inconnu"
                expiration = (
                    "Jamais"
                    if invite.max_age == 0
                    else f"<t:{int(invite.created_at.timestamp() + invite.max_age)}:R>"
                )
                embed.add_field(
                    name=f"🔑 Code : `{invite.code}`",
                    value=(
                        f"👤 **Inviteur** : {inviter}\n"
                        f"🔄 **Utilisations** : {invite.uses}\n"
                        f"⏳ **Expire** : {expiration}"
                    ),
                    inline=False,
                )

        embed.set_footer(
            text=f"Commandé par {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )
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

            embed = discord.Embed(
                title="🔍 Détails d'Invitation",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Membre invité", value=member.mention, inline=False)

            if result:
                inviter_id = result["inviter_id"]
                invite_count = result["invite_count"]
                inviter = ctx.guild.get_member(inviter_id)

                if inviter:
                    embed.add_field(
                        name="Invité par",
                        value=f"{inviter.mention} (a invité **{invite_count}** personne(s))",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="Invité par",
                        value=f"Un utilisateur qui n'est plus sur le serveur.\n**Personnes invitées** : {invite_count}",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="Erreur",
                    value=f":x: Impossible de déterminer qui a invité {member.mention}.",
                    inline=False,
                )

            await ctx.send(embed=embed)
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
            # Requête pour compter les utilisateurs invités par cette personne
            query = """
            SELECT COUNT(iu.user_id) AS invite_count
            FROM invite_uses iu
            JOIN invites i ON iu.invite_code = i.invite_code
            WHERE i.inviter_id = %s AND i.guild_id = %s;
            """
            self.db.cursor.execute(query, (inviter_id, guild_id))
            result = self.db.cursor.fetchone()

            invite_count = result["invite_count"] if result and result["invite_count"] > 0 else 0

            embed = discord.Embed(
                title="📊 Invitations Compte",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(
                name="Utilisateur",
                value=f"{member.mention}",
                inline=False
            )
            embed.add_field(
                name="Invitations",
                value=f"{invite_count} personne(s) invitée(s)",
                inline=False
            )

            await ctx.send(embed=embed)
        except Exception as e:
            print(f"[ERREUR] invite_count: {e}")
            await ctx.send(":x: Une erreur s'est produite lors de l'exécution de la commande.")


async def setup(bot):
    await bot.add_cog(Invite(bot))
