from discord.ext import commands
import discord
from database import Database
import os
from discord.ui import View, Button
import datetime
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(
            host=os.getenv("HOST"),
            user=os.getenv("UTILISATEUR"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            port=os.getenv("PORT"),
        )

    @commands.group(name="point", aliases=["points"], help="Prefix des commandes de points.")
    async def point(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Vérifie la fin de ta commande.")


    @point.command(name="look", aliases=["regarde"], help="Regarde tes points.")
    async def point_look(self, ctx):
        points = self.db.get_points(str(ctx.author.id), str(ctx.guild.id))
        embed = discord.Embed(
            title="🏦 Solde de Points",
            description=f"**{ctx.author.display_name}**, vous avez **{points} points**.",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

    @point.command(name="info", help="Regarde les points de quelqu'un.")
    async def balanceother(self, ctx, member: discord.Member):
        try:
            points = self.db.get_points(str(member.id), str(ctx.guild.id))
            rank = self.db.get_user_position(member.id, ctx.guild.id)
            created_at = member.created_at.strftime("%d/%m/%Y %H:%M:%S")
            invite_count = max(self.db.get_invite_count(member.id, ctx.guild.id), 0)

            embed = discord.Embed(
                title=f"🏦 Solde de Points de {member.display_name}",
                description=(f"**{member.display_name}** a **{points} points**.\n"
                             f"Il se trouve à la **{rank}ème place**.\n"
                             f"Il a invité au total **{invite_count} personne(s)**.\n\n"
                             f"**Date de création du compte:** {created_at}"),
                color=discord.Color.purple()
            )
            embed.set_footer(text=f"ID du joueur : {member.id}")

            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            embed.set_thumbnail(url=avatar_url)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Une erreur est survenue: {str(e)}")



        
    @point.command(name="add", aliases=["ajout"], help="Ajoute des points.")
    @commands.has_permissions(administrator=True)
    async def addpoints(self, ctx, member: discord.Member, amount: int):
        self.db.add_points(str(member.id), str(ctx.guild.id), amount)
        embed = discord.Embed(
            title="🔼 Ajout de Points",
            description=f"Ajout de **{amount} points** à **{member.display_name}**.",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)
        
    @point.command(name="set", aliases=["fixer"], help="Fixe les points d'un membre.")
    @commands.has_permissions(administrator=True)
    async def setpoints(self, ctx, member: discord.Member, amount: int):
        self.db.set_points(str(member.id), str(ctx.guild.id), amount)
        embed = discord.Embed(
            title="🔄 Modification de Points",
            description=f"Les points de **{member.display_name}** sont maintenant fixés à **{amount} points**.",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

    @point.command(name="remove", aliases=["retrait"], help="Retire des points.")
    @commands.has_permissions(administrator=True)
    async def removepoints(self, ctx, member: discord.Member, amount: int):
        self.db.remove_points(str(member.id), str(ctx.guild.id), amount)
        embed = discord.Embed(
            title="🔽 Retrait de Points",
            description=f"Retrait de **{amount} points** à **{member.display_name}**.",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

    @point.command(name="position", aliases=["poss"],  help="Permet de voir sa position dans le classement.")
    async def position(self, ctx):
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        points = self.db.get_points(user_id, guild_id)
        rank = self.db.get_user_position(user_id, guild_id)
        if rank is not None:
            embed = discord.Embed(
                title="🏆 Votre Position dans le Classement",
                description=f"Vous êtes **{rank}ème** au classement avec **{points} points**.",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Il semble que vous n'ayez pas encore de points ou que vous ne soyez pas dans le classement.")
            
    @point.command(name="help", aliases=["infopoint"],  help="Affiche les informations sur les points.")
    async def infopoint(self, ctx):
        embed = discord.Embed(
            title="🌟 Comment gagner des points ?",
            description=(
                "Vous pouvez gagner des points facilement et rapidement sur NexuCup, nous vous avons mis plein de moyens à disposition. Voici les actions qui vous rapporterons des points :\n\n"
                "・Envoyer un message vous rapporte **5 points** (Cooldown de 30 secondes par message) dans n’importe quel salon !\n\n"
                "・Inviter un ami sur notre serveur Discord, vous rapporte **100 points** (le bot vérifie automatiquement les invitations discord) !\n\n"
                "・Obtenir un rôle spécifique sur notre discord vous rapportera entre 30 et 150 points par jour ( utilise la commande !grade pour découvrir le système de grade ) !\n\n"
                "・Appuyez sur certaines réactions dans des salons prédéfinis par notre système vous rapportera entre 4 et 10 points par jour  ( utilise la commande !salonpoint pour découvrir les salons destinés aux réactions ) !\n\n"
                "・Restez actif dans un vocal vous rapportera 2 points toutes les 5 minutes ( Sauf les salons support et AFK ) !\n\n"
                "・Participer aux divers events vous rapportera un certain nombre de points ( les points sont parallèles à l’évent, plus l’évent et long/d’un niveau compliqué, plus le nombre de points est élevé ) !\n\n"
                "⚠️Le staff s’octroie le droit de vous retirer des points selon les sanctions prises à votre égard ! Pour faire une réclamation merci de passer par nos tickets, avec des preuves ( Date et heure, screen, pseudo ) ."
            ),
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)
    
    @point.command(name="grade", aliases=["infograde", "helpgrades"],  help="Affiche les informations sur les grades.")
    async def infograde(self, ctx):
        embed = discord.Embed(
            title="🌟 Système de Grade Discord ",
            description=(
                "Nous avons mis en place un système de grade qui permet de vous attribuer X points par jour ! Ce système fonctionne comme un système de rang, c'est-à-dire qu’il y a divers paliers qui vous apportent divers grades ( voir ci-dessous ) .\n\n"
                "Chaque palier passé, un grade vous est octroyé sans pour autant vous retirer des points . \n\n"
                "Un système de bonus à aussi était mis en place afin que tout le monde puisse participer à sa guise !\n\n"
                "Voici le système en question : "
            ),            
            color=discord.Color.purple()
        )
        embed.add_field(name=f"> Palier 0 :", value=f"- Joueur = 30 points par jour", inline=False)
        embed.add_field(name=f"> Palier 1 :", value=f"- Charbon = 50 points par jour\n - Points requis : 5 000", inline=False)
        embed.add_field(name=f"> Palier 2 :", value=f"- Fer = 70 points par jour\n - Points requis = 15 000", inline=False)
        embed.add_field(name=f"> Palier 3 :", value=f"- Or = 90 points par jour\n - Points requis : 30 000", inline=False)
        embed.add_field(name=f"> Palier 4 :", value=f"- Diamant = 110 points par jour\n - Point requis = 50 000", inline=False)
        embed.add_field(name=f"> Palier 5 :", value=f"- Emeraude = 130 points par jour\n - Points requis = 70 000", inline=False)

        await ctx.send(embed=embed)
        
    @point.command(name="classement", aliases=["class"],  help="Affiche le classement du serveur en fonction des points.")
    async def classement(self, ctx, page: int = 1):
        total_entries = self.db.get_total_entries(str(ctx.guild.id))
        total_pages = (total_entries - 1) // 10 + 1
        view = LeaderboardView(ctx, self.db, total_pages, self.bot)
        await view.show_page(ctx, is_initial=True)
    
    @point.command(name="daily", aliases=["jour", "claim"],  help="Récupérez votre récompense journalière selon votre grade.")
    async def dailypoint(self, ctx):
        user_id = str(ctx.author.id)
        last_claimed = self.db.get_last_claimed(user_id)
        
        if last_claimed and (datetime.datetime.now() - last_claimed).total_seconds() < 86400:
            await ctx.send("Vous avez déjà récupéré votre récompense journalière. Revenez dans 24 heures !", ephemeral=True)
            return
        
        points = 0
        for role in ctx.author.roles:
            if role.name == "fondateur":
                points = 100
                break
            elif role.name == "NexuMusic":
                points = 200
                break

        if points == 0:
            await ctx.send("Vous n'avez pas le grade requis pour récupérer des points journaliers. Veuillez vérifier les conditions d'éligibilité ou contacter un administrateur.", ephemeral=True)
            return
        
        self.db.update_last_claimed(user_id)
        self.db.add_points(user_id, str(ctx.guild.id), points)
        
        embed = discord.Embed(
            title="Récompense Journalière",
            description=f"Vous venez de récupérer **{points} Points** ! Revenez dans 24 heures pour récupérer la récompense journalière ! 🎉",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

class LeaderboardView(View):
    def __init__(self, ctx, db, total_pages, bot):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.db = db
        self.current_page = 1
        self.total_pages = total_pages
        self.bot = bot

    @discord.ui.button(label="Précédent", style=discord.ButtonStyle.grey, custom_id="previous_page")
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page > 1:
            self.current_page -= 1
            await self.show_page(interaction)

    @discord.ui.button(label="Suivant", style=discord.ButtonStyle.grey, custom_id="next_page")
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.show_page(interaction)

    async def show_page(self, ctx_or_interaction, is_initial=False):
        limit = 10
        offset = (self.current_page - 1) * limit
        leaderboard = self.db.get_leaderboard(str(self.ctx.guild.id), limit, offset)

        if isinstance(ctx_or_interaction, commands.Context):
            user = ctx_or_interaction.author
            guild = ctx_or_interaction.guild
        else:
            user = ctx_or_interaction.user
            guild = ctx_or_interaction.guild

        user_id = str(user.id)
        guild_id = str(guild.id)
        points = self.db.get_points(user_id, guild_id)
        rank = self.db.get_user_position(user_id, guild_id)

        embed = discord.Embed(
            title=f"🏆 Classement des Points",
            description=f"Votre position: **{rank}** avec **{points} points**",
            color=discord.Color.purple()
        )
        for index, entry in enumerate(leaderboard, start=offset + 1):
            member = guild.get_member(int(entry['user_id']))
            name = member.display_name if member else "Utilisateur inconnu"
            embed.add_field(name=f"``{index}``. {name} - **{entry['points']}** points", value=f"", inline=False)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f"Page {self.current_page}", icon_url=self.bot.user.avatar.url)

        if is_initial:
            await ctx_or_interaction.send(embed=embed, view=self)
        else:
            await ctx_or_interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(Economy(bot))
