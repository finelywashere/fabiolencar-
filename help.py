import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="help")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Help Menu")

        embed.add_field(name="Moderation", value="/ban /kick /warn")
        embed.add_field(name="Tickets", value="/ticketpanel")
        embed.add_field(name="Economy", value="/work /balance")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
