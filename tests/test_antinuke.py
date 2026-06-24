import pytest
import time
import discord
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from antinuke import AntiNuke


@pytest.fixture
def antinuke_cog(bot):
    return AntiNuke(bot)


class TestAntiNukeInit:
    def test_cog_initializes_with_empty_actions(self, antinuke_cog):
        assert antinuke_cog.actions == {}

    def test_cog_stores_bot_reference(self, antinuke_cog, bot):
        assert antinuke_cog.bot is bot


class TestAntiNukeChannelDelete:
    @pytest.mark.asyncio
    async def test_single_delete_does_not_trigger_kick(self, antinuke_cog, guild):
        """A single channel delete should not trigger anti-nuke."""
        channel = MagicMock(spec=discord.TextChannel)
        channel.guild = guild

        user = MagicMock(spec=discord.Member)
        user.id = 99999

        entry = MagicMock()
        entry.user = user

        async def mock_audit_logs(*args, **kwargs):
            yield entry

        guild.audit_logs = mock_audit_logs

        await antinuke_cog.on_guild_channel_delete(channel)

        guild.kick.assert_not_called()

    @pytest.mark.asyncio
    async def test_two_deletes_does_not_trigger_kick(self, antinuke_cog, guild):
        """Two channel deletes within 10 seconds should not trigger anti-nuke."""
        channel = MagicMock(spec=discord.TextChannel)
        channel.guild = guild

        user = MagicMock(spec=discord.Member)
        user.id = 99999

        entry = MagicMock()
        entry.user = user

        async def mock_audit_logs(*args, **kwargs):
            yield entry

        guild.audit_logs = mock_audit_logs

        await antinuke_cog.on_guild_channel_delete(channel)
        await antinuke_cog.on_guild_channel_delete(channel)

        guild.kick.assert_not_called()

    @pytest.mark.asyncio
    async def test_three_deletes_triggers_kick(self, antinuke_cog, guild):
        """Three channel deletes within 10 seconds should trigger anti-nuke kick."""
        channel = MagicMock(spec=discord.TextChannel)
        channel.guild = guild

        user = MagicMock(spec=discord.Member)
        user.id = 99999

        entry = MagicMock()
        entry.user = user

        async def mock_audit_logs(*args, **kwargs):
            yield entry

        guild.audit_logs = mock_audit_logs

        await antinuke_cog.on_guild_channel_delete(channel)
        await antinuke_cog.on_guild_channel_delete(channel)
        await antinuke_cog.on_guild_channel_delete(channel)

        guild.kick.assert_called_once_with(user, reason="Anti-nuke triggered")

    @pytest.mark.asyncio
    async def test_old_actions_expire_after_10_seconds(self, antinuke_cog, guild):
        """Actions older than 10 seconds should be expired and not count."""
        channel = MagicMock(spec=discord.TextChannel)
        channel.guild = guild

        user = MagicMock(spec=discord.Member)
        user.id = 99999

        entry = MagicMock()
        entry.user = user

        async def mock_audit_logs(*args, **kwargs):
            yield entry

        guild.audit_logs = mock_audit_logs

        # Manually set old timestamps
        antinuke_cog.actions[user.id] = [time.time() - 15, time.time() - 12]

        # This is only the first "recent" delete
        await antinuke_cog.on_guild_channel_delete(channel)

        guild.kick.assert_not_called()

    @pytest.mark.asyncio
    async def test_different_users_tracked_separately(self, antinuke_cog, guild):
        """Each user's actions should be tracked independently."""
        channel = MagicMock(spec=discord.TextChannel)
        channel.guild = guild

        user1 = MagicMock(spec=discord.Member)
        user1.id = 11111
        user2 = MagicMock(spec=discord.Member)
        user2.id = 22222

        entry1 = MagicMock()
        entry1.user = user1
        entry2 = MagicMock()
        entry2.user = user2

        call_count = [0]

        async def mock_audit_logs(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                yield entry1
            else:
                yield entry2

        guild.audit_logs = mock_audit_logs

        # User1 deletes twice
        await antinuke_cog.on_guild_channel_delete(channel)
        await antinuke_cog.on_guild_channel_delete(channel)
        # User2 deletes once
        await antinuke_cog.on_guild_channel_delete(channel)

        guild.kick.assert_not_called()
        assert len(antinuke_cog.actions[user1.id]) == 2
        assert len(antinuke_cog.actions[user2.id]) == 1


class TestAntiNukeSetup:
    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, bot):
        from antinuke import setup
        bot.add_cog = AsyncMock()
        await setup(bot)
        bot.add_cog.assert_called_once()
        args = bot.add_cog.call_args[0]
        assert isinstance(args[0], AntiNuke)
