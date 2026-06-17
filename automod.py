import discord
from discord.ext import commands
import re

BAD_WORDS = ["fuck", "shit", "bitch", "nigga", "nigger"]

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mute_user(self, guild, member):
        role = discord.utils.get(guild.roles, name="Muted")
        if not role:
            role = await guild.create_role(name="Muted")
            for channel in guild.channels:
                await channel.set_permissions(role, send_messages=False)

        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        # profanity filter
        if any(word in content for word in BAD_WORDS):
            await message.delete()
            await self.mute_user(message.guild, message.author)
            await message.channel.send(f"{message.author.mention} Auto-muted for bad language.")

        # spam / caps detection
        if len(content) > 10 and content.isupper():
            await message.delete()

async def setup(bot):
    await bot.add_cog(Automod(bot))
