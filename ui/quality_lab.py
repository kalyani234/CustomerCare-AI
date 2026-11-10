
import json
from datetime import datetime
from multiprocessing import context
from pathlib import Path

import pandas as pd
import streamlit as st

from chatbot.llm import generate_response
from chatbot.rag_pipeline import (
    load_documents,
    split_into_chunks,
    retrieve_relevant_chunks
)

from evaluation.groq_judge import GroqJudge

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric
)

from deepeval.test_case import LLMTestCase


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CustomerCare AI Quality Lab",
    page_icon="🧪",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORT_DIR / "quality_report.json"

THRESHOLD = 0.7


# ==========================================
# TEST QUESTIONS
# ==========================================

POSITIVE_TESTS = [
    "How much does express delivery cost?",
    "How long does standard delivery take?",
    "How much is standard delivery?",
    "Is free delivery available?",
    "Will I receive a tracking link?"
]

NEGATIVE_TESTS = [
    "What is your London office address?",
    "Do you offer next-day delivery?",
    "Can I get a 50% discount?",
    "Can you guarantee delivery tomorrow?",
    "What is the CEO's name?"
]


# ==========================================
# RUN EVALUATION FOR ONE QUESTION
# ==========================================

def evaluate_question(question, judge, documents, chunks):

    context = retrieve_relevant_chunks(
        question,
        chunks,
        top_k=3
    )

    answer = generate_response(question,relevant_chunks=context)
    # print("\nQUESTION:", question)
    # print("RETRIEVED CONTEXT:", context)

    st.markdown("**Retrieved Context**")

    if context:
        for index, chunk in enumerate(context, start=1):
            st.write(f"Chunk {index}:")
            st.info(chunk)
    else:
        st.warning("No relevant context retrieved.")
    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=context,
        context=context
    )

    metrics = [
        AnswerRelevancyMetric(
            threshold=THRESHOLD,
            model=judge,
            include_reason=True
        ),
        FaithfulnessMetric(
            threshold=THRESHOLD,
            model=judge,
            include_reason=True
        ),
        HallucinationMetric(
            threshold=THRESHOLD,
            model=judge,
            include_reason=True
        )
    ]

    results = []

    for metric in metrics:

        metric.measure(test_case)

        results.append({
            "metric": metric.__class__.__name__,
            "score": metric.score,
            "threshold": THRESHOLD,
            "reason": metric.reason,
            "status": (
                "PASS"
                if metric.score >= THRESHOLD
                else "FAIL"
            )
        })

    return {
        "question": question,
        "chatbot_answer": answer,
        "evaluation_results": results
    }


# ==========================================
# SAVE REPORT
# ==========================================

def save_report(results):

    total_checks = sum(
        len(test["evaluation_results"])
        for test in results
    )

    passed = sum(
        1
        for test in results
        for metric in test["evaluation_results"]
        if metric["status"] == "PASS"
    )

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_scenarios": len(results),
        "total_metric_checks": total_checks,
        "passed_metric_checks": passed,
        "failed_metric_checks": total_checks - passed,
        "overall_pass_rate": (
            passed / total_checks if total_checks else 0
        ),
        "test_results": [
            {
                "test_number": index,
                **result
            }
            for index, result in enumerate(results, start=1)
        ]
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    return report


# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("🧪 CustomerCare AI – Quality Testing Lab")

st.caption(
    "Interactive chatbot testing and AI evaluation using DeepEval"
)


# ==========================================
# TEST SELECTION
# ==========================================

st.sidebar.header("Test Configuration")

test_type = st.sidebar.radio(
    "Choose test type",
    ["Positive Tests", "Negative Tests", "All Tests", "Custom Questions"]
)

if test_type == "Positive Tests":
    questions = POSITIVE_TESTS.copy()

elif test_type == "Negative Tests":
    questions = NEGATIVE_TESTS.copy()

elif test_type == "All Tests":
    questions = POSITIVE_TESTS + NEGATIVE_TESTS

else:
    questions = []

st.subheader("Test Questions")

if test_type == "Custom Questions":

    custom_text = st.text_area(
        "Enter one question per line",
        placeholder=(
            "How much does express delivery cost?\n"
            "Do you offer next-day delivery?"
        )
    )

    questions = [
        line.strip()
        for line in custom_text.splitlines()
        if line.strip()
    ]

else:

    selected_questions = st.multiselect(
        "Select questions to evaluate",
        options=questions,
        default=questions
    )

    questions = selected_questions


st.write(f"Selected questions: **{len(questions)}**")


# ==========================================
# RUN EVALUATION
# ==========================================

if st.button(
    "🚀 Run All Evaluations",
    type="primary",
    disabled=not questions
):

    all_results = []

    progress = st.progress(0)
    status = st.empty()

    try:

        status.info("Loading company documents...")

        documents = load_documents()
        chunks = split_into_chunks(documents)

        status.info("Connecting to evaluation model...")

        judge = GroqJudge()

        for index, question in enumerate(questions, start=1):

            status.info(
                f"Evaluating question {index} of {len(questions)}"
            )

            result = evaluate_question(
                question,
                judge,
                documents,
                chunks
            )

            all_results.append(result)

            progress.progress(index / len(questions))

        report = save_report(all_results)

        st.session_state["quality_report"] = report

        status.success("Evaluation completed successfully!")

    except Exception as error:

        status.error(f"Evaluation failed: {error}")


# ==========================================
# DISPLAY RESULTS
# ==========================================

report = st.session_state.get("quality_report")

if report:

    st.divider()

    st.header("Evaluation Results")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Test Scenarios",
        report["total_scenarios"]
    )

    col2.metric(
        "Metric Checks",
        report["total_metric_checks"]
    )

    col3.metric(
        "Passed",
        report["passed_metric_checks"]
    )

    col4.metric(
        "Failed",
        report["failed_metric_checks"]
    )

    pass_rate = report["overall_pass_rate"] * 100

    st.subheader("Overall Pass Rate")

    st.progress(report["overall_pass_rate"])

    st.metric("Quality Score", f"{pass_rate:.1f}%")

    # Build metric table
    rows = []

    for test in report["test_results"]:

        for metric in test["evaluation_results"]:

            rows.append({
                "Question": test["question"],
                "Metric": metric["metric"],
                "Score": metric["score"],
                "Threshold": metric["threshold"],
                "Status": metric["status"]
            })

    df = pd.DataFrame(rows)

    # Metric charts
    st.subheader("Metric Performance")

    metric_names = {
        "AnswerRelevancyMetric": "Answer Relevancy",
        "FaithfulnessMetric": "Faithfulness",
        "HallucinationMetric": "Hallucination"
    }

    df["Metric"] = df["Metric"].replace(metric_names)
    df["Score (%)"] = df["Score"] * 100

    summary = (
        df.groupby("Metric")["Score (%)"]
        .mean()
        .reset_index()
    )

    st.bar_chart(
        summary.set_index("Metric")
    )

    # Detailed results
    st.subheader("Individual Test Results")

    for index, test in enumerate(report["test_results"], start=1):

        with st.expander(
            f"Test {index}: {test['question']}"
        ):

            st.markdown("**Chatbot Answer**")

            st.write(test["chatbot_answer"])

            for metric in test["evaluation_results"]:

                st.markdown(
                    f"**{metric['metric']}**"
                )

                col1, col2 = st.columns(2)

                col1.metric(
                    "Score",
                    f"{metric['score']:.2f}"
                )

                col2.metric(
                    "Status",
                    metric["status"]
                )

                st.caption(
                    f"Threshold: {metric['threshold']:.2f}"
                )

                st.write(
                    metric["reason"] or "No explanation available."
                )

                st.divider()

    st.download_button(
        "Download Evaluation Report",
        data=json.dumps(report, indent=4),
        file_name="quality_report.json",
        mime="application/json"
    )

else:

    st.info(
        "Select positive, negative or custom questions "
        "and click Run All Evaluations to generate a report."
    )
