import discord
from discord.ext import commands
import random
import aiosqlite

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_balance(self, user_id):
        async with aiosqlite.connect("database.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS eco (user INTEGER, balance INTEGER)")
            await db.commit()

            cur = await db.execute("SELECT balance FROM eco WHERE user=?", (user_id,))
            row = await cur.fetchone()

            if not row:
                await db.execute("INSERT INTO eco VALUES (?, ?)", (user_id, 0))
                await db.commit()
                return 0

            return row[0]

    @discord.app_commands.command(name="work")
    async def work(self, interaction: discord.Interaction):
        earn = random.randint(50, 200)

        async with aiosqlite.connect("database.db") as db:
            await db.execute("INSERT OR IGNORE INTO eco VALUES (?, ?)", (interaction.user.id, 0))
            await db.execute("UPDATE eco SET balance = balance + ? WHERE user=?", (earn, interaction.user.id))
            await db.commit()

        await interaction.response.send_message(f"You earned ${earn}")

    @discord.app_commands.command(name="balance")
    async def balance(self, interaction: discord.Interaction):
        bal = await self.get_balance(interaction.user.id)
        await interaction.response.send_message(f"Balance: ${bal}")

async def setup(bot):
    await bot.add_cog(Economy(bot))
