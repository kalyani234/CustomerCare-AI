from chatbot.llm import generate_response
import pytest

def test_chatbot_returns_response(): 
    # Test that the chatbot returns a non-empty response for a valid question

    question = "What is software testing?"

    answer = generate_response(question)

    assert answer is not None
    assert len(answer.strip()) > 0  


def test_chatbot_response_is_relevant():

    question = "How much does express delivery cost?"

    answer = generate_response(question)

    assert "7.99" in answer


def test_chatbot_handles_empty_question():

    question = ""

    with pytest.raises(
        ValueError,
        match="Question cannot be empty"
    ):
        generate_response(question)

def test_chatbot_handles_different_questions():
    # Test that the chatbot can handle different questions and return relevant responses

    questions = [
        "What is software testing?",
        "What is automation testing?",
        "What is regression testing?"
    ]

    for question in questions:

        answer = generate_response(question)

        assert answer is not None
        assert len(answer.strip()) > 0