import discord
from discord.ext import commands
from discord.ui import View, Button

class HelpView(View):
    def __init__(self, help_command, context, mapping):
        super().__init__(timeout=None)
        self.help_command = help_command
        self.context = context
        self.mapping = mapping
        exclude_cogs = ['ErrorHandler', 'LoggerHandler', 'ReadyHandler', 'JoinHandler', 'LeaveHandler', 'InviteTracker']
        for cog in mapping.keys():
            if cog and cog.qualified_name not in exclude_cogs:
                self.add_item(HelpButton(label=cog.qualified_name, help_command=help_command, context=context, mapping=mapping, cog=cog))

class HelpButton(Button):
    def __init__(self, label, help_command, context, mapping, cog):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.cog = cog
        self.help_command = help_command
        self.context = context
        self.mapping = mapping

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Commandes dans {self.cog.qualified_name}", color=discord.Color.gold())
        commands = self.mapping[self.cog]
        filtered = await self.help_command.filter_commands(commands, sort=True)
        command_list = '\n'.join([f'`{self.help_command.get_command_signature(c)}`: {c.short_doc}' for c in filtered if c.enabled])
        embed.add_field(name="Commandes", value=command_list or "Aucune commandes disponible.")
        await interaction.response.edit_message(embed=embed, view=self.view)

class CustomHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Commandes disponible", color=discord.Color.blue())
        embed.description = "Choisis une catégorie:"
        
        view = HelpView(self, self.context, mapping)
        await self.context.send(embed=embed, view=view)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=discord.Color.green())
        embed.add_field(name="Help", value=command.help or "Aucun help disponible")
        await self.context.send(embed=embed)
