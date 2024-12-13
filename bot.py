import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import Database  
from commands.help import CustomHelp
from discord.ext import tasks
from console_config import setup_console 
import signal
import asyncio

logger = setup_console(__name__)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
db = Database(
    host=os.getenv("HOST"),
    user=os.getenv("UTILISATEUR"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    port=os.getenv("PORT")
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=CustomHelp())

async def load_extensions():
    try:
        db.setup_database()
        db.setup_radio_database()
        db.setup_invites_database()

        logger.info("La base de données est configurée.")
        await bot.load_extension("commands.music")
        await bot.load_extension("commands.server")
        await bot.load_extension("commands.setup")
        await bot.load_extension("commands.invite")    
        logger.info("Extensions commands chargées avec succès.")
        await bot.load_extension("events.errors")
        await bot.load_extension("events.ready")
        await bot.load_extension("events.logger")
        await bot.load_extension("events.join")
        await bot.load_extension("events.leave")
        await bot.load_extension("events.invitetracker")
        logger.info("Extensions events chargées avec succès.")
    except Exception as e:
        logger.error(f"Impossible de charger les extensions : {e}")
                
if __name__ == "__main__":
    async def main():        
        async def shutdown(signal, loop):
            print(f'Recu du signale {signal.name}...')
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            [task.cancel() for task in tasks]
            await asyncio.gather(*tasks, return_exceptions=True)
            loop.stop()

        loop = asyncio.get_running_loop()
        for sig in [signal.SIGTERM, signal.SIGINT]:
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))

        try:
            await load_extensions()
            logger.info("Démarrage du bot Discord...")
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            logger.info("Arrêt du bot...")
            await bot.close()
        finally:
            logger.info("Bot arrêté proprement.")

    asyncio.run(main())
