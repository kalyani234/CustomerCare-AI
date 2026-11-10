from unittest.mock import patch
from chatbot.llm import generate_response
from chatbot.llm import generate_response, validate_api_key
import pytest
from groq import RateLimitError
from groq import APIConnectionError
from groq import APITimeoutError
from groq import InternalServerError

import httpx


def test_validate_api_key_missing():

    with pytest.raises(
        ValueError,
        match="Groq API key is missing"
    ):
        validate_api_key(None)

@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_with_mock(mock_groq):
    # Test that the generate_response function returns the expected response

    mock_groq.return_value.choices = [
        type(
            "Choice",
            (),
            {
                "message": type(
                    "Message",
                    (),
                    {"content": "Software testing checks software quality."}
                )()
            }
        )()
    ]

    answer = generate_response("What is software testing?")

    assert answer == "Software testing checks software quality."
    mock_groq.assert_called_once()


@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_api_failure(mock_groq):
    # Test that the generate_response function raises an exception on API failure

    mock_groq.side_effect = Exception("API connection failed")

    try:
        generate_response("What is software testing?")
    except Exception as error:
        assert str(error) == "API connection failed"    


@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_empty_response(mock_groq):

    mock_groq.return_value.choices = []

    with pytest.raises(ValueError, match="API returned no choices"):
        generate_response("What is software testing?")


@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_rejects_empty_question(mock_groq):

    with pytest.raises(ValueError, match="Question cannot be empty"):
        generate_response("")

    mock_groq.assert_not_called()

@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_rejects_whitespace_question(mock_groq):
    with pytest.raises(ValueError, match="Question cannot be empty"):
        generate_response("   ")

    mock_groq.assert_not_called()


@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_rejects_invalid_input_type(mock_groq):
    # Test that the generate_response function raises an exception for non-string input
    with pytest.raises(TypeError, match="Question must be a string"):
        generate_response(12345)  # Passing an integer instead of a string

    mock_groq.assert_not_called()


def test_generate_response_rejects_oversized_question():

    with patch("chatbot.llm.client.chat.completions.create") as mock_api:

        question = "A" * 5001

        with pytest.raises(
            ValueError,
            match="Question must not exceed 5000 characters"
        ):
            generate_response(question)

        mock_api.assert_not_called()

def test_generate_response_accepts_maximum_question_length():

    with patch("chatbot.llm.client.chat.completions.create") as mock_api:

        mock_message = type(
            "Message", (), {"content": "Mocked response"}
        )()

        mock_choice = type(
            "Choice", (), {"message": mock_message}
        )()

        mock_response = type(
            "Response", (), {"choices": [mock_choice]}
        )()

        mock_api.return_value = mock_response

        question = "A" * 5000

        answer = generate_response(question)

        assert answer == "Mocked response"
        mock_api.assert_called_once()    


    
def test_generate_response_returns_string():

    with patch("chatbot.llm.client.chat.completions.create") as mock_api:

        mock_message = type(
            "Message", (), {"content": "Your order has been shipped."}
        )()

        mock_choice = type(
            "Choice", (), {"message": mock_message}
        )()

        mock_response = type(
            "Response", (), {"choices": [mock_choice]}
        )()

        mock_api.return_value = mock_response

        answer = generate_response("Where is my order?")

        assert isinstance(answer, str)


def test_generate_response_rejects_none_content():

    with patch("chatbot.llm.client.chat.completions.create") as mock_api:

        mock_message = type(
            "Message", (), {"content": None}
        )()

        mock_choice = type(
            "Choice", (), {"message": mock_message}
        )()

        mock_response = type(
            "Response", (), {"choices": [mock_choice]}
        )()

        mock_api.return_value = mock_response

        with pytest.raises(ValueError, match="API returned empty content"):
            generate_response("Where is my order?") 

@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_rejects_none_choices(mock_groq):

    mock_groq.return_value.choices = None

    with pytest.raises(ValueError, match="API returned no choices"):
        generate_response("What is software testing?")

@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_connection_timeout(mock_groq):

    mock_groq.side_effect = TimeoutError("Connection timed out")

    with pytest.raises(TimeoutError, match="Connection timed out"):
        generate_response("Where is my order?")

@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_rate_limit(mock_groq):

    mock_groq.side_effect = Exception("Rate limit exceeded")

    with pytest.raises(Exception, match="Rate limit exceeded"):
        generate_response("Where is my order?")

@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_server_error(mock_groq):

    mock_groq.side_effect = Exception("Internal Server Error")

    with pytest.raises(Exception, match="Internal Server Error"):
        generate_response("Where is my order?")

@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_groq_rate_limit(mock_groq):

    request = httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions"
    )

    response = httpx.Response(
        429,
        request=request
    )

    mock_groq.side_effect = RateLimitError(
        "Rate limit exceeded",
        response=response,
        body=None
    )

    with pytest.raises(RateLimitError):
        generate_response("Where is my order?")


@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_groq_connection_error(mock_groq):

    request = httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions"
    )

    mock_groq.side_effect = APIConnectionError(request=request)

    with pytest.raises(APIConnectionError):
        generate_response("Where is my order?")


@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_groq_timeout(mock_groq):

    request = httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions"
    )

    mock_groq.side_effect = APITimeoutError(request=request)

    with pytest.raises(APITimeoutError):
        generate_response("Where is my order?")


@patch("chatbot.llm.client.chat.completions.create")
def test_generate_response_groq_server_error(mock_groq):

    request = httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions"
    )

    response = httpx.Response(
        500,
        request=request
    )

    mock_groq.side_effect = InternalServerError(
        "Internal Server Error",
        response=response,
        body=None
    )

    with pytest.raises(InternalServerError):
        generate_response("Where is my order?")