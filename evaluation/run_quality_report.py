
import json
from datetime import datetime
from pathlib import Path

from chatbot.llm import generate_response
from chatbot.rag_pipeline import (
    load_documents,
    split_into_chunks,
    retrieve_relevant_chunks
)

from evaluation.groq_judge import GroqJudge
from evaluation.ground_truth import GROUND_TRUTH

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric
)

from deepeval.test_case import LLMTestCase


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"


def run_quality_report():

    documents = load_documents()
    chunks = split_into_chunks(documents)

    judge = GroqJudge()

    all_results = []

    for index, test in enumerate(GROUND_TRUTH, start=1):

        question = test["question"]

        print(f"\nTEST {index}: {question}")
        print("-" * 50)

        # Generate chatbot response
        context = retrieve_relevant_chunks(
            question,
            chunks,
            top_k=3
        )

        answer = generate_response(question)

        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=context,
            context=context
        )

        # Initialize evaluation metrics
        metrics = [
            AnswerRelevancyMetric(
                threshold=0.7,
                model=judge,
                include_reason=True
            ),
            FaithfulnessMetric(
                threshold=0.7,
                model=judge,
                include_reason=True
            ),
            HallucinationMetric(
                threshold=0.7,
                model=judge,
                include_reason=True
            )
        ]

        metric_results = []

        for metric in metrics:

            metric.measure(test_case)

            result = {
                "metric": metric.__class__.__name__,
                "score": metric.score,
                "threshold": 0.7,
                "reason": metric.reason,
                "status": (
                    "PASS" if metric.score >= 0.7 else "FAIL"
                )
            }

            metric_results.append(result)

            print(
                f"{result['metric']}: "
                f"{result['score']:.2f} - {result['status']}"
            )

        all_results.append({
            "test_number": index,
            "question": question,
            "chatbot_answer": answer,
            "evaluation_results": metric_results
        })

    # Calculate overall results
    total_metrics = sum(
        len(test["evaluation_results"])
        for test in all_results
    )

    passed_metrics = sum(
        1
        for test in all_results
        for metric in test["evaluation_results"]
        if metric["status"] == "PASS"
    )

    # Create final JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_scenarios": len(all_results),
        "total_metric_checks": total_metrics,
        "passed_metric_checks": passed_metrics,
        "failed_metric_checks": total_metrics - passed_metrics,
        "overall_pass_rate": (
            passed_metrics / total_metrics
            if total_metrics else 0
        ),
        "test_results": all_results
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report_path = REPORT_DIR / "quality_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\n" + "=" * 50)
    print("CUSTOMERCARE AI - EVALUATION SUMMARY")
    print("=" * 50)
    print("Total scenarios:", len(all_results))
    print("Total metric checks:", total_metrics)
    print("Passed:", passed_metrics)
    print("Failed:", total_metrics - passed_metrics)
    print(f"Pass rate: {report['overall_pass_rate']:.0%}")
    print("\nJSON report saved:", report_path)


if __name__ == "__main__":
    run_quality_report()
