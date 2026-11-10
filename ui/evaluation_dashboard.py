
import json
from pathlib import Path

import pandas as pd
import streamlit as st


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CustomerCare AI | Quality Dashboard",
    page_icon="📊",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_ROOT / "reports" / "quality_report.json"


# ==========================================
# 2. LOAD EVALUATION REPORT
# ==========================================

st.title("📊 CustomerCare AI – Quality Dashboard")
st.caption("AI Customer Support | RAG Evaluation | DeepEval")

if not REPORT_FILE.exists():
    st.error("Evaluation report not found. Run the evaluation first.")
    st.stop()

with open(REPORT_FILE, "r", encoding="utf-8") as file:
    report = json.load(file)

scenarios = report.get("test_results", [])

if not scenarios:
    st.warning("No test scenarios found in the report.")
    st.stop()


# ==========================================
# 3. PREPARE METRIC DATA
# ==========================================

metric_rows = []

for index, scenario in enumerate(scenarios):

    scenario_name = (
        scenario.get("test_name")
        or scenario.get("scenario")
        or scenario.get("name")
        or f"Test Scenario {index + 1}"
    )

    question = (
        scenario.get("question")
        or scenario.get("input")
        or scenario.get("test_case")
        or "Question not available"
    )

    answer = (
        scenario.get("answer")
        or scenario.get("actual_output")
        or scenario.get("response")
        or "Answer not available"
    )

    metrics = (
        scenario.get("metric_results")
        or scenario.get("metrics")
        or []
    )

    for metric in metrics:

        metric_name = (
            metric.get("metric_name")
            or metric.get("metric")
            or metric.get("name")
            or "Unknown Metric"
        )

        score = metric.get("score", 0)

        metric_rows.append({
            "Scenario": scenario_name,
            "Question": question,
            "Answer": answer,
            "Metric": metric_name,
            "Score": float(score),
            "Threshold": float(metric.get("threshold", 0.7)),
            "Status": metric.get("status", "UNKNOWN"),
            "Reason": metric.get("reason", "No explanation available")
        })

df = pd.DataFrame(metric_rows)

if df.empty:
    st.error("No metric results found in the report.")
    st.stop()

df["Metric"] = df["Metric"].replace({
    "AnswerRelevancyMetric": "Answer Relevancy",
    "FaithfulnessMetric": "Faithfulness",
    "HallucinationMetric": "Hallucination"
})

# Convert scores to percentages for display
df["Score (%)"] = df["Score"] * 100


# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Dashboard Filters")

selected_metrics = st.sidebar.multiselect(
    "Select metrics",
    options=sorted(df["Metric"].unique()),
    default=sorted(df["Metric"].unique())
)

selected_status = st.sidebar.multiselect(
    "Select status",
    options=sorted(df["Status"].unique()),
    default=sorted(df["Status"].unique())
)

filtered_df = df[
    df["Metric"].isin(selected_metrics)
    & df["Status"].isin(selected_status)
]

if filtered_df.empty:
    st.warning("No results match your selected filters.")
    st.stop()


# ==========================================
# 5. OVERALL QUALITY SUMMARY
# ==========================================

st.subheader("Overall Quality Summary")

total_scenarios = df["Scenario"].nunique()
total_checks = len(df)
passed = (df["Status"] == "PASS").sum()
failed = (df["Status"] == "FAIL").sum()

pass_rate = (passed / total_checks * 100) if total_checks else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Test Scenarios", total_scenarios)
col2.metric("Metric Checks", total_checks)
col3.metric("Passed", passed)
col4.metric("Failed", failed)

st.progress(pass_rate / 100)

st.caption(f"Overall Pass Rate: {pass_rate:.1f}%")

st.divider()


# ==========================================
# 6. DASHBOARD TABS
# ==========================================

overview_tab, metrics_tab, explorer_tab = st.tabs([
    "📊 Overview",
    "📈 Metric Performance",
    "🔍 Test Scenario Explorer"
])


# ==========================================
# 7. OVERVIEW TAB
# ==========================================

with overview_tab:

    st.subheader("Quality Metric Performance")

    metric_summary = (
        filtered_df.groupby("Metric")["Score (%)"]
        .mean()
        .reset_index()
    )

    col1, col2, col3 = st.columns(3)

    metric_cards = [
        "Answer Relevancy",
        "Faithfulness",
        "Hallucination"
    ]

    for column, metric_name in zip(
        [col1, col2, col3],
        metric_cards
    ):

        values = metric_summary[
            metric_summary["Metric"] == metric_name
        ]["Score (%)"]

        with column:
            if not values.empty:
                st.metric(
                    metric_name,
                    f"{values.iloc[0]:.1f}%"
                )
            else:
                st.metric(metric_name, "N/A")

    st.subheader("Metric Score Comparison")

    st.bar_chart(
        metric_summary.set_index("Metric"),
        y="Score (%)"
    )

    st.subheader("Scenario Performance")

    scenario_summary = (
        filtered_df.groupby("Scenario")
        .agg(
            Average_Score=("Score (%)", "mean"),
            Passed=("Status", lambda x: (x == "PASS").sum()),
            Failed=("Status", lambda x: (x == "FAIL").sum())
        )
        .reset_index()
    )

    st.dataframe(
        scenario_summary,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 8. METRIC PERFORMANCE TAB
# ==========================================

with metrics_tab:

    st.subheader("Detailed Metric Analysis")

    chosen_metric = st.selectbox(
        "Choose a metric",
        options=sorted(filtered_df["Metric"].unique())
    )

    metric_data = filtered_df[
        filtered_df["Metric"] == chosen_metric
    ]

    st.metric(
        f"Average {chosen_metric} Score",
        f"{metric_data['Score (%)'].mean():.1f}%"
    )

    st.bar_chart(
        metric_data.set_index("Scenario"),
        y="Score (%)"
    )

    st.subheader("Metric Results")

    st.dataframe(
        metric_data[
            ["Scenario", "Score (%)", "Threshold", "Status"]
        ],
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 9. TEST SCENARIO EXPLORER
# ==========================================

with explorer_tab:

    st.subheader("Explore Individual Test Scenarios")

    available_scenarios = sorted(
        filtered_df["Scenario"].unique()
    )

    selected_scenario = st.selectbox(
        "Select a test scenario",
        options=available_scenarios
    )

    scenario_data = filtered_df[
        filtered_df["Scenario"] == selected_scenario
    ]

    first_result = scenario_data.iloc[0]

    st.markdown("#### Customer Question")
    st.info(first_result["Question"])

    st.markdown("#### Chatbot Answer")
    st.success(first_result["Answer"])

    st.markdown("#### Evaluation Results")

    for _, result in scenario_data.iterrows():

        with st.expander(
            f"{result['Metric']} – {result['Status']}"
        ):

            col1, col2 = st.columns(2)

            col1.metric(
                "Score",
                f"{result['Score']:.2f}"
            )

            col2.metric(
                "Threshold",
                f"{result['Threshold']:.2f}"
            )

            st.write("**Evaluation explanation:**")
            st.write(result["Reason"])

    st.markdown("#### Scenario Metric Comparison")

    st.bar_chart(
        scenario_data.set_index("Metric"),
        y="Score (%)"
    )


# ==========================================
# 10. FOOTER
# ==========================================

st.divider()

st.caption(
    "CustomerCare AI | Python | Streamlit | Groq | RAG | DeepEval"
)
