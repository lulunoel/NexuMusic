import discord
from discord.ext import commands
import asyncio

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        target_channel_id = 1089468106088386600
        if after.channel and after.channel.id == target_channel_id:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=member.guild)

            if voice_client and voice_client.channel and voice_client.channel.id == target_channel_id:
                if voice_client.is_playing():
                    print(f"Le bot est déjà en train de jouer de l'audio dans le canal : {voice_client.channel.name}")
                    return

            if not voice_client or (voice_client.channel and voice_client.channel.id != target_channel_id):
                if voice_client:
                    await voice_client.disconnect()

                try:
                    voice_client = await after.channel.connect()
                    await asyncio.sleep(1)
                    voice_client.play(discord.FFmpegPCMAudio('audio.mp3'), after=lambda e: print('Audio fini !'))
                    while voice_client.is_playing():
                        await asyncio.sleep(1)
                    await voice_client.disconnect()
                except discord.ClientException as e:
                    print(f"Erreur lors de la connexion ou de la lecture : {e}")



async def setup(bot):
    await bot.add_cog(Voice(bot))
