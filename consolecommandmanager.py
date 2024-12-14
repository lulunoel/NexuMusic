import threading
import asyncio
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text

class ConsoleCommandManager:
    def __init__(self, bot):
        self.bot = bot
        self.console = Console()
        self.commands = {
            "stop": self.stop_bot,
            "list_guilds": self.list_guilds,
            "send_message": self.send_message,
            "list_members": self.list_members,
            "reload_cog": self.reload_cog,
            "help": self.show_help,
        }

    def start(self):
        """Démarre l'écoute des commandes console dans un thread séparé."""
        threading.Thread(target=self.listen_to_console, daemon=True).start()

    def listen_to_console(self):
        """Écoute les commandes saisies dans la console."""
        self.console.print("[bold green]Console Command Manager démarré.[/bold green] Tapez 'help' pour la liste des commandes.")
        while True:
            command = Prompt.ask("> ", console=self.console)
            self.execute_command(command)

    def execute_command(self, command):
        """Exécute une commande console."""
        args = command.split()
        if not args:
            return

        cmd_name = args[0]
        cmd_args = args[1:]

        if cmd_name in self.commands:
            try:
                self.commands[cmd_name](*cmd_args)
            except Exception as e:
                self.console.print(f"[red]Erreur lors de l'exécution de la commande '{cmd_name}': {e}[/red]")
        else:
            self.console.print(f"[yellow]Commande inconnue : {cmd_name}.[/yellow] Tapez 'help' pour voir la liste des commandes.")

    def stop_bot(self):
        """Arrête le bot."""
        self.console.print("[red bold]Arrêt du bot...[/red bold]")
        asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot.loop)

    def list_guilds(self):
        """Affiche la liste des serveurs (guilds) où le bot est présent."""
        table = Table(title="Liste des Serveurs", show_lines=True)
        table.add_column("Nom du Serveur", style="cyan", no_wrap=True)
        table.add_column("ID", style="magenta")

        for guild in self.bot.guilds:
            table.add_row(guild.name, str(guild.id))

        self.console.print(table)

    def list_members(self, guild_id: str):
        """Affiche les membres d'un serveur spécifique."""
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            table = Table(title=f"Membres de {guild.name}", show_lines=True)
            table.add_column("Nom", style="cyan")
            table.add_column("Discriminant", style="yellow")
            table.add_column("ID", style="magenta")

            for member in guild.members:
                table.add_row(member.name, f"#{member.discriminator}", str(member.id))

            self.console.print(table)
        else:
            self.console.print(f"[red]Serveur introuvable pour l'ID : {guild_id}[/red]")

    def send_message(self, channel_id: str, *message_parts):
        """Envoie un message à un canal spécifique."""
        try:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                message = " ".join(message_parts)
                asyncio.run_coroutine_threadsafe(channel.send(message), self.bot.loop)
                self.console.print(f"[green]Message envoyé à [cyan]{channel.name}[/cyan]: {message}[/green]")
            else:
                self.console.print(f"[red]Canal introuvable pour l'ID : {channel_id}[/red]")
        except ValueError:
            self.console.print("[red]ID du canal invalide.[/red]")

    def reload_cog(self, cog_name: str):
        """Recharge un Cog."""
        try:
            asyncio.run_coroutine_threadsafe(self.bot.reload_extension(cog_name), self.bot.loop)
            self.console.print(f"[green]Cog {cog_name} rechargé.[/green]")
        except Exception as e:
            self.console.print(f"[red]Erreur lors du rechargement du Cog {cog_name}: {e}[/red]")

    def show_help(self):
        """Affiche la liste des commandes disponibles."""
        table = Table(title="Commandes Disponibles", show_lines=True)
        table.add_column("Commande", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")

        table.add_row("stop", "Arrête le bot.")
        table.add_row("list_guilds", "Affiche la liste des serveurs où le bot est présent.")
        table.add_row("list_members <guild_id>", "Affiche la liste des membres d'un serveur spécifique.")
        table.add_row("send_message <channel_id> <message>", "Envoie un message dans un canal spécifique.")
        table.add_row("reload_cog <cog_name>", "Recharge un Cog spécifique.")
        table.add_row("help", "Affiche la liste des commandes disponibles.")

        self.console.print(table)
