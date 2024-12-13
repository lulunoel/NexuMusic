import discord
from discord.ext import commands
from database import Database 
from radios import RADIOS
import os
import re
from discord import ButtonStyle, ui
from discord.ext import tasks
import datetime
import asyncio
from console_config import setup_console 

logger = setup_console(__name__)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_task.start()
        self.queues = {}
        self.db = Database(
            host=os.getenv("HOST"),
   			user=os.getenv("UTILISATEUR"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            port=os.getenv("PORT")
        )
	  
    @tasks.loop(seconds=60)
    async def cleanup_task(self):
        """Vérifie et déconnecte les bots inactifs."""
        for vc in self.bot.voice_clients:
            if not vc.is_playing() and not vc.is_paused():
                await vc.disconnect()
                
    @commands.command(name="radio", help="Affiche la liste des radios ou joue une radio.")
    async def radio(self, ctx, radio_name: str = None):
        server_id = ctx.guild.id
        server_name = ctx.guild.name

        settings = self.db.get_server_settings(server_id)
        if not settings:
            settings = {"volume": 1.0, "last_radio": None}
            self.db.upsert_server_settings(server_id, server_name, 1.0, None)

        custom_radios = self.db.get_custom_radios(server_id)
        custom_radios_dict = {radio["name"]: radio["url"] for radio in custom_radios}

        if not radio_name:
            public_radios = "\n".join([f"🎧 **{name}**" for name in RADIOS.keys()])
            personal_radios = "\n".join([f"🛠️ **{name}**" for name in custom_radios_dict.keys()])

            embed = discord.Embed(
                title="📻 Radios disponibles",
                description="Sélectionnez une radio avec `!radio <nom_de_radio>`",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(
                name="🎧 Radios publiques",
                value=public_radios or "Aucune radio publique disponible.",
                inline=False
            )
            embed.add_field(
                name="🛠️ Radios personnalisées",
                value=personal_radios or "Aucune radio personnalisée ajoutée.",
                inline=False
            )
            embed.set_footer(text="Ajoutez vos radios !addradio <nom> <url>")
            await ctx.send(embed=embed)
            return

        all_radios = {**RADIOS, **custom_radios_dict}
        if radio_name not in all_radios:
            await ctx.send(f":x: La radio `{radio_name}` n'est pas disponible.")
            return

        if not ctx.author.voice:
            await ctx.send(":x: Vous devez être connecté à un canal vocal pour utiliser cette commande.")
            return

        voice_channel = ctx.author.voice.channel
        vc = ctx.voice_client

        if vc:
            if vc.channel != voice_channel:
                await vc.move_to(voice_channel)
        else:
            vc = await voice_channel.connect()

        try:
            url = all_radios[radio_name]
            if vc.is_playing():
                vc.stop()
            vc.play(discord.FFmpegPCMAudio(
                url,
                options=f"-filter:a 'volume={settings['volume']}'"
            ))
            self.db.upsert_server_settings(server_id, server_name, settings["volume"], radio_name)
            embed = discord.Embed(
            title="🎶 Radio en cours",
            description=f"La radio **{radio_name}** est en cours de lecture.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
            embed.set_thumbnail(url="https://img.freepik.com/vecteurs-libre/realiste-panneaux-aeriens_52683-52774.jpg?semt=ais_hybrid")  
            embed.set_author(
                name="NexuMusic",
                icon_url="https://cdn.discordapp.com/app-icons/1314655717814173716/3a1b13517b55c22b5c1b3740e9cd7154.png?size=256&quot"
            )
            embed.set_image(url="https://img.freepik.com/vecteurs-libre/cadre-neon-aerien-espace-vide_23-2148772472.jpg?semt=ais_hybrid")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(":x: Une erreur s'est produite lors de la lecture.")
            print(f"[ERREUR] !play : {e}")
    
    @commands.command(name="volume", help="Règle le volume pour ce serveur et relance la radio en cours.")
    async def volume(self, ctx, level: float):
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name

        if not 0.1 <= level <= 2.0:
            embed = discord.Embed(
                title=":x: Volume invalide",
                description="Le volume doit être compris entre `0.1` et `2.0`.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            return

        settings = self.db.get_server_settings(guild_id)
        last_radio = settings.get("last_radio") if settings else None

        self.db.upsert_server_settings(guild_id, guild_name, level, last_radio)

        embed = discord.Embed(
            title=":speaker: Volume mis à jour",
            description=f"Le volume a été réglé à **{level}x** pour ce serveur.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)
        if last_radio:
            try:
                vc = ctx.voice_client
                if not vc:
                    voice_channel = ctx.author.voice.channel
                    vc = await voice_channel.connect()

                if vc.is_playing():
                    vc.stop()
                vc.play(discord.FFmpegPCMAudio(
                    RADIOS[last_radio],
                    options=f"-filter:a 'volume={level}'"
                ))

                embed = discord.Embed(
                    title=":notes: Radio relancée",
                    description=f"La radio **{last_radio}** a été relancée avec le volume **{level}x**.",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
                await ctx.send(embed=embed)

            except Exception as e:
                embed = discord.Embed(
                    title=":x: Erreur",
                    description="Une erreur s'est produite lors de la relance de la radio.",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                await ctx.send(embed=embed)
                print(f"Impossible de relancer la radio pour {guild_name} : {e}")
        else:
            embed = discord.Embed(
                title=":warning: Pas de radio en cours",
                description="Aucune radio n'est en cours de lecture pour ce serveur.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)

    @commands.command(name="stop", help="Arrête la lecture et vide la file d'attente.")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc:
            vc.stop()
            await vc.disconnect()
            await ctx.send(":stop_button: Lecture arrêtée et file d'attente vidée.")
        else:
            await ctx.send(":x: Le bot n'est pas connecté à un canal vocal.")
            
    def cog_unload(self):
        """Ferme la connexion à la base de données lors du déchargement du cog."""
        self.db.close()

    @commands.command(name="addradio", help="Ajoute une radio personnalisée pour ce serveur.")
    async def addradio(self, ctx, name: str, url: str):
        """Ajoute une radio personnalisée."""
        server_id = ctx.guild.id
        if not re.match(r'^https?://', url):
            embed = discord.Embed(
                title=":x: URL invalide",
                description="L'URL fournie n'est pas valide. Veuillez fournir une URL commençant par `http://` ou `https://`.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            return
        success = self.db.add_custom_radio(server_id, name, url)
        if success:
            embed = discord.Embed(
                title=":white_check_mark: Radio ajoutée",
                description=f"La radio **{name}** a été ajoutée avec succès pour ce serveur.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=":x: Nom déjà utilisé",
                description=f"Une radio avec le nom **{name}** existe déjà pour ce serveur.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
            
    @commands.command(name="removeradio", help="Retire une radio personnalisée pour ce serveur.")
    async def removeradio(self, ctx, name: str):
        """Retire une radio personnalisée."""
        server_id = ctx.guild.id
        success = self.db.remove_custom_radio(server_id, name)
        if success:
            embed = discord.Embed(
                title=":white_check_mark: Radio retirée",
                description=f"La radio **{name}** a été retirée avec succès pour ce serveur.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=":x: Nom introuvable",
                description=f"Aucune radio avec le nom **{name}** n'existe pour ce serveur.",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))
