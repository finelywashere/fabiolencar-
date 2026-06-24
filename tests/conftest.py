import pytest
import discord
from unittest.mock import AsyncMock, MagicMock, patch
from discord.ext import commands


@pytest.fixture
def bot():
    """Create a mock bot instance."""
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.user = MagicMock()
    mock_bot.user.name = "TestBot"
    mock_bot.tree = MagicMock()
    mock_bot.tree.sync = AsyncMock()
    return mock_bot


@pytest.fixture
def guild():
    """Create a mock guild."""
    mock_guild = MagicMock(spec=discord.Guild)
    mock_guild.channels = []
    mock_guild.roles = []
    mock_guild.kick = AsyncMock()
    mock_guild.create_role = AsyncMock()
    mock_guild.create_text_channel = AsyncMock()
    return mock_guild


@pytest.fixture
def member():
    """Create a mock member."""
    mock_member = MagicMock(spec=discord.Member)
    mock_member.bot = False
    mock_member.id = 12345
    mock_member.name = "TestUser"
    mock_member.mention = "<@12345>"
    mock_member.add_roles = AsyncMock()
    return mock_member


@pytest.fixture
def channel(guild):
    """Create a mock text channel."""
    mock_channel = MagicMock(spec=discord.TextChannel)
    mock_channel.guild = guild
    mock_channel.send = AsyncMock()
    mock_channel.set_permissions = AsyncMock()
    mock_channel.mention = "#test-channel"
    return mock_channel
