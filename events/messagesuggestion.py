from discord.ext import commands, tasks
import discord
from database import Database
import os

db = Database(
    host=os.getenv("HOST"),
    user=os.getenv("UTILISATEUR"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    port=int(os.getenv("PORT"))
)

class MessageSuggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_expired_reactions.start()

    def cog_unload(self):
        self.check_expired_reactions.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return

        settings = db.get_server_settings(message.channel.guild.id)
        target_channel_id = settings['server_suggestion_id']

        if message.channel.id != target_channel_id:
            return

        if message.author.bot:
            return

        embed = discord.Embed(title="Suggestion:", description=message.content, color=discord.Color.purple(), timestamp=message.created_at)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
        embed.set_thumbnail(url=message.author.avatar.url)
        embed.set_footer(text=f"Suggestion de {message.author.display_name}")
        await message.delete()

        view = discord.ui.View()
        button_oui = discord.ui.Button(label="Oui", style=discord.ButtonStyle.primary, custom_id="oui_button")
        button_non = discord.ui.Button(label="Non", style=discord.ButtonStyle.primary, custom_id="non_button")
        button_force_oui = discord.ui.Button(label="Force Oui", style=discord.ButtonStyle.success, custom_id="oui_button_force")
        button_force_non = discord.ui.Button(label="Force Non", style=discord.ButtonStyle.danger, custom_id="non_button_force")
        
        view.add_item(button_oui)
        view.add_item(button_non)
        view.add_item(button_force_oui)
        view.add_item(button_force_non)
        sent_message = await message.channel.send(embed=embed, view=view)
        
    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type == discord.InteractionType.component:
            settings = db.get_server_settings(interaction.guild.id)
            target_channel_id = settings['server_suggestion_id']

            if interaction.channel_id == target_channel_id:
                message_id = interaction.message.id
                channel_id = interaction.channel_id
                user_id = interaction.user.id
                default_color = discord.Color.purple()
                color = default_color

                reaction_counts = db.count_reactions(message_id)
                oui_count = reaction_counts.get("oui", 0)
                non_count = reaction_counts.get("non", 0)
                emoji_oui = discord.utils.get(interaction.guild.emojis, name='oui')
                original_message_content = interaction.message.embeds[0].description.split(f'\n\n {emoji_oui} Oui:')[0]
                update_text = ""
                reaction_type = None

                if interaction.data['custom_id'] in ["oui_button_force", "non_button_force"]:
                    if interaction.user.guild_permissions.administrator:
                        forced_action = "approuvée" if interaction.data['custom_id'] == "oui_button_force" else "rejetée"
                        color = discord.Color.green() if forced_action == "approuvée" else discord.Color.red()
                        update_text = f"\n\nLa suggestion a été définitivement {forced_action} par {interaction.user.display_name}."
                        reaction_type = "force"
                    else:
                        await interaction.response.send_message("Vous n'avez pas la permission de forcer une réponse sur cette suggestion.", ephemeral=True)
                        return

                elif interaction.data['custom_id'] in ["oui_button", "non_button"]:
                    reaction_type = "oui" if interaction.data['custom_id'] == "oui_button" else "non"
                    if db.user_already_reacted(message_id, user_id):
                        await interaction.response.send_message("Vous avez déjà voté sur cette suggestion!", ephemeral=True)
                        return
                    db.add_reaction(message_id, channel_id, user_id, reaction_type)
                    if reaction_type == "oui":
                        oui_count += 1
                    else:
                        non_count += 1

                emoji_oui = discord.utils.get(interaction.guild.emojis, name='oui')
                emoji_non = discord.utils.get(interaction.guild.emojis, name='non')
                new_description = f"{original_message_content}\n\n {emoji_oui} Oui: {oui_count} \n {emoji_non} Non: {non_count}{update_text}"
                embed = interaction.message.embeds[0]
                embed.description = new_description
                embed.color = color

                if update_text:
                    for component in interaction.message.components:
                        for button in component.children:
                            button.disabled = True
                    await interaction.message.edit(embed=embed, view=None)
                else:
                    await interaction.message.edit(embed=embed)

                if reaction_type:
                    await interaction.response.send_message(f"Vous avez réagi {reaction_type} pour la suggestion! **( +4 Points )**", ephemeral=True)
                else:
                    await interaction.response.send_message("Action réalisée avec succès.", ephemeral=True)
                
    @tasks.loop(minutes=30)
    async def check_expired_reactions(self):
        expired_messages = db.get_expired_reactions()
        for msg in expired_messages:
            channel = self.bot.get_channel(msg['channel_id'])
            if channel:
                try:
                    message = await channel.fetch_message(msg['message_id'])
                    reaction_counts = db.count_reactions(msg['message_id'])
                    oui_count = reaction_counts.get("oui", 0)
                    non_count = reaction_counts.get("non", 0)

                    if oui_count > non_count:
                        color = discord.Color.green()
                    elif non_count > oui_count:
                        color = discord.Color.red()
                    else:
                        color = discord.Color.orange()

                    embed = message.embeds[0]
                    embed.color = color
                    embed.description += f"\n\n Oui: {oui_count} \n Non: {non_count} \n\n *La suggestion est terminée ! Les Nexuriens ont fait leur choix !*"
                    for component in message.components:
                        for button in component.children:
                            button.disabled = True

                    await message.edit(embed=embed, view=message.components)
                except discord.NotFound:
                    continue

async def setup(bot):
    await bot.add_cog(MessageSuggestion(bot))