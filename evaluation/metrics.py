import re

def calculate_keyword_coverage(answer, required_keywords):
    """
    Calculate the percentage of required keywords
    found in the chatbot's answer.
    """

    if not isinstance(answer, str):
        raise TypeError("Answer must be a string")

    if not required_keywords:
        raise ValueError("Required keywords cannot be empty")

    matched_keywords = [
        keyword
        for keyword in required_keywords
        if keyword.lower() in answer.lower()
    ]

    return len(matched_keywords) / len(required_keywords)


def find_unsupported_phrases(answer, unsupported_phrases):
    """
    Find phrases in the answer that are known to be unsupported.
    """

    if not isinstance(answer, str):
        raise TypeError("Answer must be a string")

    return [
        phrase
        for phrase in unsupported_phrases
        if phrase.lower() in answer.lower()
    ]


def calculate_unsupported_phrase_rate(answer, unsupported_phrases):
    """
    Calculate the proportion of known unsupported phrases
    that appear in the answer.
    """

    if not unsupported_phrases:
        raise ValueError("Unsupported phrases cannot be empty")

    found_phrases = find_unsupported_phrases(
        answer,
        unsupported_phrases
    )

    return len(found_phrases) / len(unsupported_phrases)

def calculate_fact_coverage(answer, expected_facts):

    if not isinstance(answer, str):
        raise TypeError("Answer must be a string")

    if not expected_facts:
        raise ValueError("Expected facts cannot be empty")

    # Remove Markdown formatting
    answer = re.sub(r"[*_`]", "", answer)

    # Normalise whitespace and apostrophes
    normalised_answer = " ".join(
        answer.lower()
        .replace("’", "'")
        .split()
    )

    matched_facts = 0

    for fact in expected_facts:

        alternatives = fact if isinstance(fact, list) else [fact]

        if any(
            " ".join(
                alternative.lower()
                .replace("’", "'")
                .split()
            ) in normalised_answer
            for alternative in alternatives
        ):
            matched_facts += 1

    return matched_facts / len(expected_facts)


def evaluate_ground_truth(answer, expected_facts, unsupported_facts):
    """
    Evaluate an answer against expected and unsupported facts.
    """

    coverage = calculate_fact_coverage(
        answer,
        expected_facts
    )

    unsupported = find_unsupported_phrases(
        answer,
        unsupported_facts
    )

    return {
        "fact_coverage": coverage,
        "unsupported_facts": unsupported,
        "passed": coverage == 1.0 and not unsupported
    }