from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from evaluation.groq_judge import GroqJudge


def test_faithfulness():

    judge = GroqJudge()

    metric = FaithfulnessMetric(
        threshold=0.7,
        model=judge,
        include_reason=True
    )

    test_case = LLMTestCase(
        input="How much does express delivery cost?",
        actual_output="Express delivery costs £7.99.",
        retrieval_context=[
            "Express delivery costs £7.99."
        ]
    )

    metric.measure(test_case)

    print("\nFAITHFULNESS EVALUATION")
    print("Score:", metric.score)
    print("Reason:", metric.reason)

    assert metric.score >= 0.7

def test_unfaithful_response():

    judge = GroqJudge()

    metric = FaithfulnessMetric(
        threshold=0.7,
        model=judge,
        include_reason=True
    )

    test_case = LLMTestCase(
        input="How much does express delivery cost?",
        actual_output="Express delivery costs £9.99.",
        retrieval_context=[
            "Express delivery costs £7.99."
        ]
    )

    metric.measure(test_case)

    print("\nHALLUCINATION DETECTION")
    print("Score:", metric.score)
    print("Reason:", metric.reason)

    assert metric.score < 0.7