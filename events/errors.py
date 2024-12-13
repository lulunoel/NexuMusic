from discord.ext import commands
from console_config import setup_console  # Importez la fonction de configuration de logger

logger = setup_console(__name__)
class ErrorHandler(commands.Cog):
    """Gestionnaire global des erreurs."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(":x: Une erreur s'est produite lors de l'exécution de la commande.")
            logger.error(f"CommandInvokeError : {error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(":x: Veuillez fournir tous les arguments nécessaires pour cette commande.")
        else:
            await ctx.send(f":x: Erreur: `{error}`.")
            logger.error(f"Erreur inconnue : {error}")
            
async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
