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
from consolecommandmanager import ConsoleCommandManager

logger = setup_console('Bot')
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


async def load_extensions(bot):
    try:
        db.setup_database()
        db.setup_radio_database()
        db.setup_invites_database()
        db.setup_reactions_database()
        db.setup_economy_database()
        db.setup_daily_rewards_database()
        logger.info("La base de données est configurée.")
        exclude_files = ['__init__.py', 'help.py']

        extensions_path = ['commands', 'events']
        for path in extensions_path:
            for file in os.listdir(path):
                if file.endswith('.py') and file not in exclude_files:
                    extension = f"{path}.{file[:-3]}"
                    try:
                        await bot.load_extension(extension)
                        logger.info(f"Extension {extension} chargée avec succès.")
                    except Exception as e:
                        logger.error(f"Erreur lors du chargement de l'extension {extension}: {e}")

        console_manager = ConsoleCommandManager(bot)
        console_manager.start()
    except Exception as e:
        logger.error(f"Erreur globale lors du chargement des extensions : {e}")

                
async def shutdown(signal, loop):
    print(f'Reçu du signal {signal.name}...')
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main():
    loop = asyncio.get_running_loop()
    if os.name != 'nt':
        for sig in [signal.SIGTERM, signal.SIGINT]:
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))
    try:
        await load_extensions(bot)
        logger.info("Démarrage du bot Discord...")
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logger.info("Arrêt du bot par interruption clavier...")
        await bot.close()
    finally:
        logger.info("Bot arrêté proprement.")

if __name__ == "__main__":
    asyncio.run(main())
