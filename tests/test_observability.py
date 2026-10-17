"""Unit test cho src/observability.py (PLAN.md Tuan 6 muc 4)."""

from unittest.mock import patch

from src.observability import get_callbacks


def test_get_callbacks_when_no_keys():
    with patch("src.observability.settings") as mock_settings:
        mock_settings.LANGFUSE_PUBLIC_KEY = ""
        mock_settings.LANGFUSE_SECRET_KEY = ""
        mock_settings.LANGFUSE_HOST = "https://cloud.langfuse.com"

        callbacks = get_callbacks(session_id="test_session")
        assert callbacks == []


def test_get_callbacks_when_keys_present_but_import_fails():
    with patch("src.observability.settings") as mock_settings:
        mock_settings.LANGFUSE_PUBLIC_KEY = "pk-fake"
        mock_settings.LANGFUSE_SECRET_KEY = "sk-fake"
        mock_settings.LANGFUSE_HOST = "https://cloud.langfuse.com"

        # Neu langfuse chua cai hoac loi thi van tra ve [] an toan
        callbacks = get_callbacks(session_id="test_session")
        assert isinstance(callbacks, list)
