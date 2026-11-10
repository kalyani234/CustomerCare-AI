import pytest

from evaluation.metrics import (
    calculate_keyword_coverage,
    evaluate_ground_truth,
    find_unsupported_phrases,
    calculate_fact_coverage,
    calculate_unsupported_phrase_rate
)


def test_keyword_coverage_returns_full_score():
    answer = "Express delivery costs £7.99 and takes 1 to 2 business days."

    score = calculate_keyword_coverage(
        answer,
        ["£7.99", "1 to 2 business days"]
    )

    assert score == 1.0


def test_keyword_coverage_returns_partial_score():
    answer = "Express delivery costs £7.99."

    score = calculate_keyword_coverage(
        answer,
        ["£7.99", "1 to 2 business days"]
    )

    assert score == 0.5


def test_keyword_coverage_is_case_insensitive():
    answer = "Express delivery takes 1 to 2 business days."

    score = calculate_keyword_coverage(
        answer,
        ["EXPRESS DELIVERY", "business days"]
    )

    assert score == 1.0


def test_keyword_coverage_rejects_empty_keywords():
    with pytest.raises(ValueError):
        calculate_keyword_coverage("Some answer", [])


def test_unsupported_phrase_detection():
    answer = "Special arrangements are possible for next-day delivery."

    result = find_unsupported_phrases(
        answer,
        ["special arrangements are possible"]
    )

    assert result == ["special arrangements are possible"]


def test_unsupported_phrase_rate():
    answer = "Special arrangements are possible."

    score = calculate_unsupported_phrase_rate(
        answer,
        [
            "special arrangements are possible",
            "free next-day delivery"
        ]
    )

    assert score == 0.5


def test_unsupported_phrase_rate_rejects_empty_list():
    with pytest.raises(ValueError):
        calculate_unsupported_phrase_rate("Some answer", [])


def test_fact_coverage_returns_full_score():
    answer = "Express delivery costs £7.99."

    score = calculate_fact_coverage(
        answer,
        ["Express delivery costs £7.99"]
    )

    assert score == 1.0


def test_fact_coverage_returns_partial_score():
    answer = "Express delivery costs £7.99."

    score = calculate_fact_coverage(
        answer,
        [
            "Express delivery costs £7.99",
            "Express delivery takes 1 to 2 business days"
        ]
    )

    assert score == 0.5


def test_ground_truth_evaluation_passes():
    answer = "Express delivery costs £7.99."

    result = evaluate_ground_truth(
        answer,
        ["Express delivery costs £7.99"],
        ["Express delivery is free"]
    )

    assert result["passed"] is True
    assert result["fact_coverage"] == 1.0
    assert result["unsupported_facts"] == []


def test_ground_truth_evaluation_detects_unsupported_fact():
    answer = "Express delivery is free."

    result = evaluate_ground_truth(
        answer,
        ["Express delivery costs £7.99"],
        ["Express delivery is free"]
    )

    assert result["passed"] is False
    assert result["unsupported_facts"] == [
        "Express delivery is free"
    ]