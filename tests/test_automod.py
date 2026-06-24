import pytest
import discord
from unittest.mock import AsyncMock, MagicMock, patch
from automod import Automod, BAD_WORDS


@pytest.fixture
def automod_cog(bot):
    return Automod(bot)


@pytest.fixture
def message(channel, member):
    """Create a mock message."""
    msg = MagicMock(spec=discord.Message)
    msg.author = member
    msg.author.bot = False
    msg.guild = channel.guild
    msg.channel = channel
    msg.delete = AsyncMock()
    return msg


class TestAutomodInit:
    def test_cog_stores_bot_reference(self, automod_cog, bot):
        assert automod_cog.bot is bot


class TestBadWordsFilter:
    def test_bad_words_list_is_defined(self):
        assert isinstance(BAD_WORDS, list)
        assert len(BAD_WORDS) > 0

    @pytest.mark.asyncio
    async def test_clean_message_not_deleted(self, automod_cog, message):
        """Clean messages should not be deleted or muted."""
        message.content = "hello everyone, how are you?"

        await automod_cog.on_message(message)

        message.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_bad_word_triggers_delete(self, automod_cog, message, guild):
        """Messages containing bad words should be deleted."""
        message.content = "this is a fuck test"

        # Mock mute_user since we're testing profanity detection
        automod_cog.mute_user = AsyncMock()

        await automod_cog.on_message(message)

        message.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_bad_word_triggers_mute(self, automod_cog, message, guild, member):
        """Messages with bad words should trigger user mute."""
        message.content = "this is shit"

        role = MagicMock(spec=discord.Role)
        role.name = "Muted"
        guild.roles = [role]
        discord.utils.get = MagicMock(return_value=role)

        await automod_cog.on_message(message)

        member.add_roles.assert_called_once_with(role)

    @pytest.mark.asyncio
    async def test_bad_word_sends_warning(self, automod_cog, message, channel, guild, member):
        """A warning message should be sent when a user is muted."""
        message.content = "what the fuck"

        role = MagicMock(spec=discord.Role)
        role.name = "Muted"
        guild.roles = [role]
        discord.utils.get = MagicMock(return_value=role)

        await automod_cog.on_message(message)

        channel.send.assert_called_once()
        sent_text = channel.send.call_args[0][0]
        assert member.mention in sent_text

    @pytest.mark.asyncio
    async def test_bad_word_case_insensitive(self, automod_cog, message, guild):
        """Bad word detection should be case insensitive."""
        message.content = "FUCK YOU"

        automod_cog.mute_user = AsyncMock()

        await automod_cog.on_message(message)

        message.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_bot_messages_ignored(self, automod_cog, message):
        """Bot messages should be completely ignored."""
        message.author.bot = True
        message.content = "fuck shit bitch"

        await automod_cog.on_message(message)

        message.delete.assert_not_called()


class TestSpamDetection:
    """Tests for spam/caps detection.

    Note: The current implementation has a bug where content is lowercased
    before checking isupper(), making caps detection unreachable. These tests
    document the actual behavior.
    """

    @pytest.mark.asyncio
    async def test_all_caps_long_message_not_caught_due_to_lowering(self, automod_cog, message):
        """All-caps messages are not caught because content is lowered first.

        Bug: content.lower().isupper() is always False.
        """
        message.content = "THIS IS SPAM AND SHOULD BE DELETED"

        await automod_cog.on_message(message)

        # Due to the bug, the message is NOT deleted
        message.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_short_caps_message_not_deleted(self, automod_cog, message):
        """Short all-caps messages (<=10 chars) should not be deleted."""
        message.content = "HELLO"

        await automod_cog.on_message(message)

        message.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_long_lowercase_message_not_deleted(self, automod_cog, message):
        """Long messages that aren't all caps should not be deleted."""
        message.content = "this is a perfectly normal message that is quite long"

        await automod_cog.on_message(message)

        message.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_mixed_case_not_deleted(self, automod_cog, message):
        """Mixed case messages should not trigger spam detection."""
        message.content = "Hello Everyone How Are You Doing Today"

        await automod_cog.on_message(message)

        message.delete.assert_not_called()


class TestMuteUser:
    @pytest.mark.asyncio
    async def test_mute_user_existing_role(self, automod_cog, guild, member):
        """Should use existing Muted role if available."""
        role = MagicMock(spec=discord.Role)
        role.name = "Muted"

        with patch("discord.utils.get", return_value=role):
            await automod_cog.mute_user(guild, member)

        member.add_roles.assert_called_once_with(role)
        guild.create_role.assert_not_called()

    @pytest.mark.asyncio
    async def test_mute_user_creates_role_if_missing(self, automod_cog, guild, member):
        """Should create Muted role if it doesn't exist."""
        new_role = MagicMock(spec=discord.Role)
        guild.create_role.return_value = new_role

        with patch("discord.utils.get", return_value=None):
            await automod_cog.mute_user(guild, member)

        guild.create_role.assert_called_once_with(name="Muted")
        member.add_roles.assert_called_once_with(new_role)

    @pytest.mark.asyncio
    async def test_mute_role_sets_permissions_on_channels(self, automod_cog, guild, member):
        """When creating a Muted role, it should set permissions on all channels."""
        new_role = MagicMock(spec=discord.Role)
        guild.create_role.return_value = new_role

        ch1 = MagicMock()
        ch1.set_permissions = AsyncMock()
        ch2 = MagicMock()
        ch2.set_permissions = AsyncMock()
        guild.channels = [ch1, ch2]

        with patch("discord.utils.get", return_value=None):
            await automod_cog.mute_user(guild, member)

        ch1.set_permissions.assert_called_once_with(new_role, send_messages=False)
        ch2.set_permissions.assert_called_once_with(new_role, send_messages=False)


class TestAutomodSetup:
    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, bot):
        from automod import setup
        bot.add_cog = AsyncMock()
        await setup(bot)
        bot.add_cog.assert_called_once()
        args = bot.add_cog.call_args[0]
        assert isinstance(args[0], Automod)
