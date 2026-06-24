import pytest
import discord
from unittest.mock import AsyncMock, MagicMock, patch
from tickets import Tickets, TicketView


@pytest.fixture
def tickets_cog(bot):
    return Tickets(bot)


class TestTicketsInit:
    def test_cog_stores_bot_reference(self, tickets_cog, bot):
        assert tickets_cog.bot is bot


class TestTicketView:
    def test_ticket_view_has_create_button(self):
        view = TicketView()
        # View should have children (buttons)
        assert len(view.children) > 0

    def test_create_button_label(self):
        view = TicketView()
        button = view.children[0]
        assert button.label == "Create Ticket"

    def test_create_button_style_is_green(self):
        view = TicketView()
        button = view.children[0]
        assert button.style == discord.ButtonStyle.green

    @pytest.mark.asyncio
    async def test_create_button_creates_channel(self, guild):
        """Clicking the button should create a ticket channel."""
        view = TicketView()

        interaction = MagicMock(spec=discord.Interaction)
        interaction.guild = guild
        interaction.user = MagicMock()
        interaction.user.name = "testuser"
        interaction.response = MagicMock()
        interaction.response.send_message = AsyncMock()

        new_channel = MagicMock()
        new_channel.mention = "#ticket-testuser"
        new_channel.set_permissions = AsyncMock()
        guild.create_text_channel = AsyncMock(return_value=new_channel)

        button = view.children[0]
        await button.callback(interaction)

        guild.create_text_channel.assert_called_once_with("ticket-testuser")

    @pytest.mark.asyncio
    async def test_create_button_sets_permissions(self, guild):
        """The ticket channel should have correct permissions for the user."""
        view = TicketView()

        interaction = MagicMock(spec=discord.Interaction)
        interaction.guild = guild
        interaction.user = MagicMock()
        interaction.user.name = "testuser"
        interaction.response = MagicMock()
        interaction.response.send_message = AsyncMock()

        new_channel = MagicMock()
        new_channel.mention = "#ticket-testuser"
        new_channel.set_permissions = AsyncMock()
        guild.create_text_channel = AsyncMock(return_value=new_channel)

        button = view.children[0]
        await button.callback(interaction)

        new_channel.set_permissions.assert_called_once_with(
            interaction.user, read_messages=True, send_messages=True
        )

    @pytest.mark.asyncio
    async def test_create_button_sends_ephemeral_response(self, guild):
        """The interaction response should be ephemeral."""
        view = TicketView()

        interaction = MagicMock(spec=discord.Interaction)
        interaction.guild = guild
        interaction.user = MagicMock()
        interaction.user.name = "testuser"
        interaction.response = MagicMock()
        interaction.response.send_message = AsyncMock()

        new_channel = MagicMock()
        new_channel.mention = "#ticket-testuser"
        new_channel.set_permissions = AsyncMock()
        guild.create_text_channel = AsyncMock(return_value=new_channel)

        button = view.children[0]
        await button.callback(interaction)

        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs["ephemeral"] is True

    @pytest.mark.asyncio
    async def test_response_mentions_channel(self, guild):
        """The response should contain a mention of the created ticket channel."""
        view = TicketView()

        interaction = MagicMock(spec=discord.Interaction)
        interaction.guild = guild
        interaction.user = MagicMock()
        interaction.user.name = "testuser"
        interaction.response = MagicMock()
        interaction.response.send_message = AsyncMock()

        new_channel = MagicMock()
        new_channel.mention = "#ticket-testuser"
        new_channel.set_permissions = AsyncMock()
        guild.create_text_channel = AsyncMock(return_value=new_channel)

        button = view.children[0]
        await button.callback(interaction)

        sent_text = interaction.response.send_message.call_args[0][0]
        assert "#ticket-testuser" in sent_text


class TestTicketsSetup:
    @pytest.mark.asyncio
    async def test_setup_adds_cog(self, bot):
        from tickets import setup
        bot.add_cog = AsyncMock()
        await setup(bot)
        bot.add_cog.assert_called_once()
        args = bot.add_cog.call_args[0]
        assert isinstance(args[0], Tickets)
