import discord
from discord.ext import commands
import time

class AntiNuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.actions = {}

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            user = entry.user

            now = time.time()
            self.actions[user.id] = self.actions.get(user.id, []) + [now]

            # if 3 deletes in 10 sec → punish
            self.actions[user.id] = [t for t in self.actions[user.id] if now - t < 10]

            if len(self.actions[user.id]) >= 3:
                await channel.guild.kick(user, reason="Anti-nuke triggered")

async def setup(bot):
    await bot.add_cog(AntiNuke(bot))
