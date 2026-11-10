
import pytest
from unittest.mock import patch
from chatbot.config import validate_config


def test_validate_config_with_api_key():

    with patch("chatbot.config.GROQ_API_KEY", "test_api_key"):
        with patch("builtins.print") as mock_print:

            validate_config()

            mock_print.assert_any_call(
                "Configuration loaded successfully!"
            )


def test_validate_config_missing_api_key():

    with patch("chatbot.config.GROQ_API_KEY", None):

        with pytest.raises(
            ValueError,
            match="GROQ_API_KEY is missing"
        ):
            validate_config()



def test_default_groq_model():

    from chatbot.config import GROQ_MODEL

    assert GROQ_MODEL == "openai/gpt-oss-120b"


def test_default_app_environment():

    from chatbot.config import APP_ENV

    assert APP_ENV == "development"


def test_debug_is_boolean():

    from chatbot.config import DEBUG

    assert isinstance(DEBUG, bool)

