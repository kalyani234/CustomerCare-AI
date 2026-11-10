from chatbot.llm import generate_response
from evaluation.ground_truth import GROUND_TRUTH

from evaluation.metrics import evaluate_ground_truth


def run_evaluation():

    total_tests = len(GROUND_TRUTH)
    passed_tests = 0
    total_coverage = 0

    print("\nCUSTOMERCARE AI - GROUND TRUTH EVALUATION")
    print("=" * 55)

    for index, test_case in enumerate(GROUND_TRUTH, start=1):

        question = test_case["question"]

        print(f"\nTest {index}: {question}")

        # Generate chatbot response
        answer = generate_response(question)

        # Evaluate against ground truth
        result = evaluate_ground_truth(
            answer,
            test_case["expected_facts"],
            test_case["unsupported_facts"]
        )

        total_coverage += result["fact_coverage"]

        if result["passed"]:
            passed_tests += 1

        print("Answer:", answer)
        print(f"Fact coverage: {result['fact_coverage']:.0%}")
        print("Unsupported facts:", result["unsupported_facts"])
        print("Result:", "PASS" if result["passed"] else "FAIL")

    average_coverage = total_coverage / total_tests

    print("\n" + "=" * 55)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Pass rate: {passed_tests / total_tests:.0%}")
    print(f"Average fact coverage: {average_coverage:.0%}")


if __name__ == "__main__":
    run_evaluation()