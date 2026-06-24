import pytest
from unittest.mock import patch
import os


class TestConfig:
    def test_prefix_is_slash(self):
        from config import PREFIX
        assert PREFIX == "/"

    def test_database_name(self):
        from config import DATABASE
        assert DATABASE == "database.db"

    def test_mute_role_name(self):
        from config import MUTE_ROLE_NAME
        assert MUTE_ROLE_NAME == "Muted"

    def test_token_reads_from_env(self):
        with patch.dict(os.environ, {"TOKEN": "test-token-value"}):
            # Re-import to pick up the patched env
            import importlib
            import config
            importlib.reload(config)
            assert config.TOKEN == "test-token-value"

    def test_token_is_none_when_env_not_set(self):
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.TOKEN is None
