from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase

from evaluation.groq_judge import GroqJudge


def test_correct_answer_has_no_hallucination():

    judge = GroqJudge()

    metric = HallucinationMetric(
        threshold=0.7,
        model=judge,
        include_reason=True
    )

    test_case = LLMTestCase(
        input="How much does express delivery cost?",
        actual_output="Express delivery costs £7.99.",
        context=[
            "Express delivery costs £7.99."
        ]
    )

    metric.measure(test_case)

    print("\nCORRECT ANSWER - HALLUCINATION CHECK")
    print("Score:", metric.score)
    print("Reason:", metric.reason)

    assert metric.score >= 0.7


def test_incorrect_answer_detects_hallucination():

    judge = GroqJudge()

    metric = HallucinationMetric(
        threshold=0.7,
        model=judge,
        include_reason=True
    )

    test_case = LLMTestCase(
        input="How much does express delivery cost?",
        actual_output="Express delivery costs £9.99.",
        context=[
            "Express delivery costs £7.99."
        ]
    )

    metric.measure(test_case)

    print("\nINCORRECT ANSWER - HALLUCINATION CHECK")
    print("Score:", metric.score)
    print("Reason:", metric.reason)

    assert metric.score < 0.7