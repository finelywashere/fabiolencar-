import discord
from discord.ext import commands

class TicketView(discord.ui.View):
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}")

        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="ticketpanel")
    async def ticketpanel(self, interaction: discord.Interaction):
        await interaction.channel.send("Click to open ticket", view=TicketView())
        await interaction.response.send_message("Ticket panel sent", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
