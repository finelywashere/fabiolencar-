import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestMainConfig:
    def test_initial_extensions_list(self):
        """Verify the INITIAL_EXTENSIONS list contains expected cog modules."""
        with patch("asyncio.run"):
            with patch("config.TOKEN", "fake-token"):
                import importlib
                import sys
                # Remove cached main module to re-import with mocked asyncio.run
                sys.modules.pop("main", None)
                import main
                assert "cogs.moderation" in main.INITIAL_EXTENSIONS
                assert "cogs.automod" in main.INITIAL_EXTENSIONS
                assert "cogs.tickets" in main.INITIAL_EXTENSIONS
                assert "cogs.economy" in main.INITIAL_EXTENSIONS
                assert "cogs.help" in main.INITIAL_EXTENSIONS
                assert "cogs.antinuke" in main.INITIAL_EXTENSIONS

    def test_initial_extensions_count(self):
        """Verify exactly 6 extensions are configured."""
        with patch("asyncio.run"):
            with patch("config.TOKEN", "fake-token"):
                import importlib
                import sys
                sys.modules.pop("main", None)
                import main
                assert len(main.INITIAL_EXTENSIONS) == 6

    def test_bot_command_prefix(self):
        """Verify bot uses '/' as command prefix."""
        with patch("asyncio.run"):
            with patch("config.TOKEN", "fake-token"):
                import importlib
                import sys
                sys.modules.pop("main", None)
                import main
                assert main.bot.command_prefix == "/"
