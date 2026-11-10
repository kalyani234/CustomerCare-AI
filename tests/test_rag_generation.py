import pytest
import re
from chatbot.llm import generate_response


def test_llm_returns_correct_express_delivery_price():

    answer = generate_response(
        "How much does express delivery cost?"
    )

    assert "7.99" in answer



def test_llm_returns_correct_express_delivery_time():

    answer = generate_response(
        "How long does express delivery take?"
    )

    normalised_answer = re.sub(r"\s+", " ", answer.lower())

    assert "1 to 2 business days" in normalised_answer


def test_llm_does_not_invent_next_day_delivery():

    answer = generate_response(
        "Do you offer next-day delivery?"
    )

    assert "special arrangements are possible" not in answer.lower()


def test_llm_returns_standard_delivery_price():

    answer = generate_response(
        "How much does standard delivery cost?"
    )

    assert "3.99" in answer
