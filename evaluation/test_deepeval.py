from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

from evaluation.groq_judge import GroqJudge


def test_answer_relevancy():

    judge = GroqJudge()

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=judge,
        include_reason=True
    )

    test_case = LLMTestCase(
        input="How much does express delivery cost?",
        actual_output="Express delivery costs £7.99."
    )

    metric.measure(test_case)

    print("\nANSWER RELEVANCY EVALUATION")
    print("Score:", metric.score)
    print("Reason:", metric.reason)

    assert metric.score >= 0.7