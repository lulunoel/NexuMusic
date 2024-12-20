import discord
import yt_dlp as youtube_dl
import os
import re
import datetime
import asyncio
from console_config import setup_console
from discord import FFmpegPCMAudio
from discord.ext import commands
from database import Database 
from radios import RADIOS
from discord import ButtonStyle, ui, Embed
from discord.ext import tasks
from discord.ui import Button, View
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv("CLIENT"), client_secret=os.getenv("SECRET")))

logger = setup_console(__name__)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.current_track = {}
        self.db = Database(
            host=os.getenv("HOST"),
   			user=os.getenv("UTILISATEUR"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DATABASE"),
            port=os.getenv("PORT")
        )

    def cog_unload(self):
        """Ferme la connexion à la base de données et nettoie les files d'attente lors du déchargement du cog."""
        self.db.close()
        for key in list(self.queues.keys()):
            self.queues[key] = []
        print("Toutes les files d'attente ont été vidées et la base de données a été fermée.")
        
    def update_current_track(self, guild_id, track_info):
        if track_info:
            self.current_track[guild_id] = track_info
        else:
            self.current_track.pop(guild_id, None)
            
    def set_queue(self, ctx, queue):
        """Met à jour la file d'attente pour le serveur."""
        guild_id = ctx.guild.id
        self.queues[guild_id] = queue

    def get_queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]
                
    @commands.command(name="play", help="Joue une musique depuis une URL YouTube ou Spotify.")
    async def play(self, ctx, *, url: str):
        vc = ctx.voice_client
        queue = self.get_queue(ctx)

        if "spotify.com" in url:
            try:
                track_info = self.get_spotify_track_info(url)
                search_query = f"{track_info['artist']} {track_info['title']}"
                youtube_url = self.search_youtube(search_query)
                if youtube_url:
                    url = youtube_url  
                else:
                    await ctx.send("Impossible de trouver cette musique sur YouTube.")
                    return
            except Exception as e:
                await ctx.send(f"Erreur lors de la récupération des informations Spotify : {e}")
                return

        if vc and (vc.is_playing() or vc.is_paused()):
            queue.append(url)
            await ctx.send(f"Musique ajoutée à la file d'attente. Position: {len(queue)}")
        else:
            if not vc:
                if ctx.author.voice:
                    vc = await ctx.author.voice.channel.connect()
                else:
                    await ctx.send("Vous devez être connecté à un canal vocal.")
                    return
            await self.start_play(ctx, url)
            
    def get_spotify_track_info(self, url):
        track = sp.track(url)
        return {
            "title": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "thumbnail": track["album"]["images"][0]["url"]
        }

    def search_youtube(self, query):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
                return info['webpage_url']
            except Exception as e:
                print(f"Erreur lors de la recherche YouTube : {e}")
                return None
            
    async def start_play(self, ctx, url):
        guild = ctx.guild
        vc = guild.voice_client

        if not vc:
            if ctx.author.voice:
                vc = await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Vous devez être connecté à un canal vocal.")
                return

        track_info = self.extract_audio_info(url)
        if track_info:
            audio_url = track_info.get('audio_url')
            if audio_url:
                source = FFmpegPCMAudio(
                    audio_url,
                    executable="ffmpeg",
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -reconnect_at_eof 1 -http_persistent 0",
                    options="-vn"
                )
                vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                self.update_current_track(guild.id, track_info)
                embed = discord.Embed(
                    title="Lecture en cours",
                    description=f"**[{track_info.get('title', 'Titre inconnu')}]({url})**",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=track_info.get('thumbnail', ''))
                embed.add_field(name="Chaîne", value=track_info.get('channel', 'Inconnue'), inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Impossible de trouver un flux audio valide pour cette URL.")
        else:
            await ctx.send("Erreur lors de l'extraction des informations de la piste.")

            
    async def play_next(self, ctx):
        queue = self.get_queue(ctx)
        vc = ctx.voice_client

        if queue:
            next_url = queue[0]
            await self.start_play(ctx, next_url)
            queue.pop(0)
            self.set_queue(ctx, queue)
        else:
            await ctx.send("La file d'attente est vide. Ajoutez plus de musiques pour continuer la lecture.")

            
    def extract_audio_info(self, url):
        ydl_opts = {
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), None)
                if audio_url:
                    return {
                        'audio_url': audio_url,
                        'title': info.get('title'),
                        'thumbnail': info.get('thumbnail'),
                        'channel': info.get('uploader')
                    }
            except Exception as e:
                print(f"Erreur lors de l'extraction de l'audio : {e}")
        return None
    
    @commands.command(name="playlist", help="Affiche les vidéos d'une playlist YouTube.")
    async def playlist(self, ctx, *, url: str):
        playlist_info = self.extract_playlist_info(url)
        if playlist_info:
            embed = Embed(title="Playlist YouTube", description="Voici les vidéos dans la playlist :", color=discord.Color.blue())
            view = PlaylistPages(playlist_info, embed, self)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("Impossible de récupérer les informations de la playlist ou la playlist est vide.")

    def extract_playlist_info(self, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': False,
            'extract_flat': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    return [{
                        'title': entry.get('title', 'Titre inconnu'),
                        'url': f"https://www.youtube.com/watch?v={entry['id']}" if 'id' in entry else 'URL inconnue'
                    } for entry in info['entries']]
            except Exception as e:
                print(f"Erreur lors de l'extraction de la playlist : {e}")
        return []



    @commands.command(name="queue", help="Affiche la file d'attente des musiques.")
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in self.queues and self.queues[guild_id]:
            embed = discord.Embed(title="File d'attente des musiques", color=discord.Color.blue())
            view = QueuePages(self.queues[guild_id], embed)
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("La file d'attente est actuellement vide.")

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
            
    @commands.command(name="pause", help="Met en pause la lecture en cours.")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            track_info = self.current_track.get(ctx.guild.id, {})
            embed = discord.Embed(title="Lecture mise en pause", description=f"**{track_info.get('title', 'Aucun titre disponible')}**", color=discord.Color.orange())
            embed.set_thumbnail(url=track_info.get('thumbnail', ''))
            embed.add_field(name="Chaîne", value=track_info.get('channel', 'Inconnu'), inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(description=":x: Aucune lecture en cours à mettre en pause.", color=discord.Color.red()))

    @commands.command(name="resume", help="Reprend la lecture mise en pause.")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            track_info = self.current_track.get(ctx.guild.id, {})
            embed = discord.Embed(title="Lecture reprise", description=f"**{track_info.get('title', 'Aucun titre disponible')}**", color=discord.Color.green())
            embed.set_thumbnail(url=track_info.get('thumbnail', ''))
            embed.add_field(name="Chaîne", value=track_info.get('channel', 'Inconnu'), inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(description=":x: Aucune lecture en pause à reprendre.", color=discord.Color.red()))

    @commands.command(name="stop", help="Arrête la lecture et vide la file d'attente.")
    async def stop(self, ctx):
        vc = ctx.voice_client
        guild_id = ctx.guild.id
        if vc:
            queue_length = len(self.queues.get(guild_id, []))
            track_info = self.current_track.get(guild_id, {})
            vc.stop()
            await vc.disconnect()
            self.queues[guild_id] = []
            self.update_current_track(guild_id, None)
            embed = discord.Embed(title="Lecture arrêtée", description="La lecture et la file d'attente ont été vidées.", color=discord.Color.red())
            embed.add_field(name="Dernière musique jouée", value=track_info.get('title', 'Aucune musique'), inline=False)
            embed.add_field(name="Musiques retirées de la file d'attente", value=str(queue_length), inline=False)
            if track_info.get('thumbnail'):
                embed.set_thumbnail(url=track_info.get('thumbnail'))
            await ctx.send(embed=embed)
        else:
            await ctx.send(":x: Le bot n'est pas connecté à un canal vocal.")
            
    @commands.command(name="skipto", help="Saute à la chanson spécifique dans la file d'attente.")
    async def skipto(self, ctx, index: int):
        vc = ctx.voice_client
        queue = self.get_queue(ctx)
        if not vc:
            await ctx.send("Le bot n'est pas connecté à un canal vocal.")
            return
        if index > len(queue) or index < 1:
            await ctx.send(f"L'index spécifié est hors des limites de la file d'attente. La file contient {len(queue)} chansons.")
            return
        upcoming_song = queue[index - 1]
        queue = queue[index:]
        self.set_queue(ctx, queue)
        await ctx.send(f"Saut à la chanson numéro {index}. Lecture en cours...")
        vc.stop()
        await self.start_play(ctx, upcoming_song)

            
    @commands.command(name="skip", help="Passe à la prochaine musique dans la file d'attente.")
    async def skip(self, ctx):
        vc = ctx.voice_client
        queue = self.get_queue(ctx)
        if not vc:
            await ctx.send("Le bot n'est pas connecté à un canal vocal.")
            return
        if len(queue) == 0:
            await ctx.send("Il n'y a pas d'autres chansons dans la file d'attente.")
            return
        upcoming_song = queue.pop(0)
        self.set_queue(ctx, queue)
        await ctx.send(f"Saut d'une chanson. Lecture en cours...")
        vc.stop()
        await self.start_play(ctx, upcoming_song)




class QueuePages(View):
    def __init__(self, queue, embed):
        super().__init__()
        self.queue = queue
        self.embed = embed
        self.page = 0
        self.update_content()

    def update_content(self):
        self.embed.clear_fields()
        start = self.page * 5
        end = start + 5
        for i, url in enumerate(self.queue[start:end], start=start + 1):
            self.embed.add_field(name=f"Chanson {i}", value=url, inline=False)

    @discord.ui.button(label="Précédent", style=ButtonStyle.grey)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            self.update_content()
            await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="Suivant", style=ButtonStyle.grey)
    async def next(self, interaction: discord.Interaction, button: Button):
        if (self.page + 1) * 5 < len(self.queue):
            self.page += 1
            self.update_content()
            await interaction.response.edit_message(embed=self.embed, view=self)
            
class PlaylistPages(View):
    def __init__(self, playlist, embed, music_instance):
        super().__init__()
        self.playlist = playlist
        self.embed = embed
        self.page = 0
        self.items_per_page = 5
        self.update_content()
        self.music_instance = music_instance
        
    def get_queue(self, ctx):
        return self.music_instance.get_queue(ctx)

    async def start_play(self, ctx, url):
        await self.music_instance.start_play(ctx, url)
        
    def update_content(self):
        self.embed.clear_fields()
        start = self.page * self.items_per_page
        end = min(start + self.items_per_page, len(self.playlist))
        for i, video in enumerate(self.playlist[start:end], start=start + 1):
            self.embed.add_field(name=f"{i}. {video['title']}", value=video['url'], inline=False)

    @discord.ui.button(label="Précédent", style=ButtonStyle.grey)
    async def previous(self, interaction: discord.Interaction, button: Button):
        if self.page > 0:
            self.page -= 1
            self.update_content()
            await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="Suivant", style=ButtonStyle.grey)
    async def next(self, interaction: discord.Interaction, button: Button):
        if (self.page + 1) * self.items_per_page < len(self.playlist):
            self.page += 1
            self.update_content()
            await interaction.response.edit_message(embed=self.embed, view=self)
            
    @discord.ui.button(label="Play All", style=ButtonStyle.green, row=1)
    async def play_all(self, interaction: discord.Interaction, button: Button):
        queue = self.get_queue(interaction)

        for video in self.playlist:
            queue.append(video['url'])

        await interaction.response.send_message(f"Toutes les musiques ont été ajoutées à la file d'attente. Total : {len(queue)}")

        if queue:
            await self.start_play(interaction, queue.pop(0))
        else:
            await interaction.followup.send("La playlist est vide.")


async def setup(bot):
    await bot.add_cog(Music(bot))
