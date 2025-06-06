import streamlit as st
import sys
import os
import json
import pandas as pd
import datetime
from collections import defaultdict
import plotly.graph_objects as go
import time
import hashlib

sys.path.append(os.path.abspath(".."))
import utils
import backend

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

module_set = {
                "confidence intervals",
                "model evaluation metrics",
                "regression",
                "bias-variance tradeoff",
                "model evaluation",
                "mean squared error",
                "linear regression",
                "stochastic gradient descent",
                "neural networks",
                "data visualization",
                "data analysis",
                "exploratory data analysis",
                "support vector machine",
                "support vector",
                "classification",
                "logistic regression",
                "parameter estimation",
                "cross-validation",
                "model evaluation and selection",
                "predictive modeling",
                "data science",
                "hypothesis testing",
                "randomized experiment",
                "statistical significance"
}


# === Page Configuration ===
st.set_page_config(page_title="Synthetic Data Evaluation", layout="centered")
utils.display_small_header()

# === Header ===
st.title("Synthetic Data Evaluation")
st.markdown("Review and rate synthetic datasets sample-by-sample.")
utils.spacer(45)

# === Upload Data and Questions ===
synthetic_json_file = st.file_uploader("\U0001F4C1 Upload synthetic data JSON", type="json", key="eval_data")
questions = backend.load_questions(base_dir=BASE_DIR)

# Store hash to detect new file uploads
st.session_state.setdefault("last_file_hash", None)

if synthetic_json_file and questions:
    st.markdown("---")
    utils.spacer()
    st.markdown("### Automated Checks")

    automated_tests = [
        {"question_id": "A1", "question": "Is the output in a valid JSON parsable format?"},
        {"question_id": "A2", "question": "Does each user object have a unique integer 'user_id'?"},
        {"question_id": "A3", "question": "Does each user object contain both 'explicit_data' and 'implicit_data' sections?"},
        {"question_id": "A4", "question": "Are all keys in each user object strictly limited to the schema fields provided?"},
        {"question_id": "A5", "question": "Are all string fields non-empty where applicable (e.g., learning goals)?"},
        {"question_id": "A6", "question": "Are all timestamps formatted using ISO 8601?"},
        {"question_id": "A7", "question": "Do all ratings fall within the valid range (e.g., 1–5)?"},
        {"question_id": "A8", "question": "Are all modules referenced valid nodes from the knowledge graph?"},
        {"question_id": "A9", "question": "Are the indices in curriculum edits valid given the initial curriculum?"},
        {"question_id": "A10", "question": "Are statuses limited to 'approved' or 'rejected'?"},
        {"question_id": "A11", "question": "Is the preferred content format one of the allowed types (video, quiz, etc.)?"},
        {"question_id": "A12", "question": "Is scroll speed one of: 'slow', 'medium', or 'fast'?"},
        {"question_id": "A13", "question": "Do quiz interactions contain valid retries and response times?"},
        {"question_id": "A14", "question": "Is the completion rate an integer between 0 and 100?"},
        {"question_id": "A15", "question": "Are 'active_minutes' non-negative integers?"},
        {"question_id": "A16", "question": "Are memory stats (notes, recalls) valid non-negative integers?"},
        {"question_id": "A17", "question": "Do drop-off events have valid timestamps and modules?"},
        {"question_id": "A18", "question": "Are skipped modules valid (present in curriculum or graph)?"},
        {"question_id": "A19", "question": "Are skill self-assessment scores between 1 and 5?"},
        {"question_id": "A20", "question": "Do tutor interactions include both a question and a response?"}
    ]


    with st.expander("Breakdown of the **automated validation tests**"):

        for test in automated_tests:
            st.markdown(
                f"""<div style="margin-top: 10px; margin-bottom: 10px;">
                    <span style="font-weight: bold; color: #9811B6;">{test['question_id']}</span> — {test['question']}
                </div><hr style="margin-top: 5px; margin-bottom: 5px;">""",
                unsafe_allow_html=True
            )

    file_content = synthetic_json_file.read()
    current_hash = utils.get_file_hash(file_content)
    synthetic_json_file.seek(0)

    try:
        data = json.load(synthetic_json_file)

        if current_hash != st.session_state.last_file_hash:  # In case the uploaded file changed according to hash, reset session states
            st.session_state.update({
                "synthetic_data": data,
                "evaluation_questions": questions,
                "current_sample_index": 0,
                "eval_answers": {},
                "step": 1,
                "last_file_hash": current_hash
            })

    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

    if st.button("🚀 Run", use_container_width=True):
        with st.spinner("Analyzing synthetic data..."):
            time.sleep(3)
            validation_per_sample = []

            def is_iso8601(s):
                try:
                    datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
                    return True
                except:
                    return False

            def check_all():
                valid_user_ids = set()
                allowed_formats = {"video", "podcast", "text", "chatbot interactions", "quiz", "ai roleplay"}
                scroll_speeds = {"slow", "medium", "fast"}
                data = st.session_state.synthetic_data

                for i, sample in enumerate(data):
                    uid = sample.get("user_id")
                    explicit = sample.get("explicit_data", {})
                    implicit = sample.get("implicit_data", {})
                    result = {"Sample ID": i, "user_id": uid}

                    result.update({
                        "A1": True,
                        "A2": isinstance(uid, int) and uid not in valid_user_ids,
                        "A3": "explicit_data" in sample and "implicit_data" in sample,
                        "A4": set(sample.keys()).issubset({"user_id", "explicit_data", "implicit_data"}),
                        "A5": all(isinstance(explicit.get(k), str) and explicit.get(k).strip() for k in ["explicit_learning_goals", "reflection_inputs"]),
                        "A6": all(is_iso8601(ts) for ts in sum([
                                                                [click.get("timestamp") for click in implicit.get("timestamped_clicks", [])],
                                                                [d.get("timestamp") for d in implicit.get("drop_off_events", [])],
                                                                [r.get("timestamp") for r in implicit.get("content_adaptation_requests", [])],
                                                                [t.get("timestamp") for t in implicit.get("interactions_with_tutor", [])]
                                                            ], []) if ts),
                        "A7": all(isinstance(r, int) and 1 <= r <= 5 for r in explicit.get("ratings_on_modules", {}).values()),
                        "A8": all(m in module_set for m in implicit.get("time_on_task_per_module", {}).keys()),
                        "A9": all(e.get("from_index") < len(explicit.get("initial_curriculum_state", [])) and e.get("to_index") < len(explicit.get("initial_curriculum_state", [])) for e in explicit.get("drag_and_drop_curriculum_edits", []) if isinstance(e, dict)),
                        "A10": all(s.get("status") in {"approved", "rejected"} for s in explicit.get("approval_of_content_modifications", []) if isinstance(s, dict)),
                        "A11": explicit.get("preferred_content_format") in allowed_formats,
                        "A12": implicit.get("scrolling_behavior", {}).get("scroll_speed") in scroll_speeds,
                        "A13": all(isinstance(qz.get("retries"), int) and qz.get("retries") >= 0 and isinstance(qz.get("response_time"), int)
                                    for module in implicit.get("quiz_interactions", {}).values()
                                    for qz in module.values()),
                        "A14": isinstance(implicit.get("engagement_metrics", {}).get("completion_rate"), int) and 0 <= implicit.get("engagement_metrics", {}).get("completion_rate") <= 100,
                        "A15": isinstance(implicit.get("engagement_metrics", {}).get("active_minutes"), int) and implicit.get("engagement_metrics", {}).get("active_minutes") >= 0,
                        "A16": all(isinstance(implicit.get("memory_usage_patterns", {}).get(k), int) and implicit.get("memory_usage_patterns", {}).get(k) >= 0 for k in ["personal_notes_added", "memory_recalls"]),
                        "A17": all(is_iso8601(d.get("timestamp", "")) and d.get("module") in module_set for d in implicit.get("drop_off_events", []) if isinstance(d, dict)),
                        "A18": all(m in module_set or m in explicit.get("initial_curriculum_state", []) for m in implicit.get("skipped_modules", [])),
                        "A19": all(isinstance(explicit.get("skill_self_assessments", {}).get(k), int) and 1 <= explicit.get("skill_self_assessments", {}).get(k) <= 5 for k in ["before_training", "after_training"]),
                        "A20": all(i.get("question") and i.get("response") for i in implicit.get("interactions_with_tutor", []) if isinstance(i, dict))
                    })

                    valid_user_ids.add(uid)
                    validation_per_sample.append(result)

            check_all()

            df_val = pd.DataFrame(validation_per_sample)
            df_summary = df_val[[col for col in df_val.columns if col.startswith("A")]].sum().reset_index()
            df_summary.columns = ["Question ID", "Pass"]
            df_summary["Fail"] = len(df_val) - df_summary["Pass"]
            df_summary["Total"] = len(df_val)
            df_summary.sort_values(
                by="Question ID",
                key=lambda col: col.str.extract(r'([A-Z]+)(\d+)').astype({0: str, 1: int}).apply(tuple, axis=1),
                inplace=True)
            df_summary.reset_index(drop=True)

            st.session_state.update({
                "validation_results": df_val,
                "validation_summary": df_summary
            })

        if "validation_summary" in st.session_state:
            fig = go.Figure(data=[
                go.Bar(name="Pass", x=st.session_state.validation_summary["Question ID"], y=st.session_state.validation_summary["Pass"], marker_color="#4CAF50"),
                go.Bar(name="Fail", x=st.session_state.validation_summary["Question ID"], y=st.session_state.validation_summary["Fail"], marker_color="#F44336")
            ])
            fig.update_layout(
                title= "Bar Chart Summary of Automated Checks", 
                barmode="group", 
                xaxis_title="Question ID", 
                yaxis_title="Count"
            )
            st.plotly_chart(fig)

            st.download_button(
                "Download Automated Checks Results",
                data=st.session_state.validation_results.to_csv(index=False),
                file_name="automated_evaluation.csv",
                mime="text/csv"
            )

# === Evaluation UI ===
if "synthetic_data" in st.session_state and "evaluation_questions" in st.session_state:
    utils.spacer()
    st.markdown("---")
    st.markdown("### Expert Evaluation")
    st.info("Please answer the following questions based on the current sample. Select **YES** if the condition applies, or **NO** otherwise. Use your best judgment to assess each case.")
    utils.spacer(15)

    data = st.session_state.synthetic_data
    questions = st.session_state.evaluation_questions
    answers = st.session_state.eval_answers

    def go_previous():
        if st.session_state.current_sample_index > 0:
            st.session_state.current_sample_index -= 1

    def go_next():
        if st.session_state.current_sample_index < len(st.session_state.synthetic_data) - 1:
            st.session_state.current_sample_index += 1

    # UI layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("⬅️ Previous", on_click=go_previous, disabled=st.session_state.current_sample_index == 0)
    with col2:
        st.write(f"Sample {st.session_state.current_sample_index + 1} / {len(data)}")
    with col3:
        st.button("Next ➡️", on_click=go_next, disabled=st.session_state.current_sample_index == len(data) - 1)


    with st.expander(f"Expand sample {st.session_state.current_sample_index + 1} of {len(data)}"):
        st.code(json.dumps(data[st.session_state.current_sample_index], indent=2), language="json")

    utils.spacer()

    for q in questions:
        key = f"{q['question_id']}_sample_{st.session_state.current_sample_index}"
        answers[key] = st.radio(f"{q['question_id']}: {q['question']}", ["Yes", "No"], key=key)
        utils.spacer(10)


    if st.button("✅ Finish Evaluation"):
        st.session_state.step = 2

utils.spacer(50)

# === Summary ===
if st.session_state.get("step") == 2:
    answers = st.session_state.eval_answers
    count_by_question = defaultdict(lambda: {"Yes": 0, "No": 0})

    per_sample_records = []
    for q in st.session_state.evaluation_questions:
        qid = q["question_id"]
        for i in range(len(st.session_state.synthetic_data)):
            key = f"{qid}_sample_{i}"
            ans = answers.get(key)
            if ans:
                count_by_question[qid][ans] += 1
            per_sample_records.append({"Sample ID": i, "Question ID": qid, "Answer": "True" if ans == "Yes" else ("False" if ans == "No" else "")})


    # Build dataframe
    df = pd.DataFrame([
        {"Question ID": qid, "Yes": count["Yes"], "No": count["No"]}
        for qid, count in count_by_question.items()
    ])

    # Plot
    fig = go.Figure(data=[
        go.Bar(name="Yes", x=df["Question ID"], y=df["Yes"], marker_color="#4CAF50"),
        go.Bar(name="No", x=df["Question ID"], y=df["No"], marker_color="#F44336")
    ])
    fig.update_layout(
        title = "Bar Chart Summary of Automated Checks",
        barmode="group",
        xaxis_title="Question ID",
        yaxis_title="Response Count"
    )
    st.plotly_chart(fig)

    df_detailed = pd.DataFrame(per_sample_records)
    st.download_button(
        label="Download Expert Evaluation Results",
        data=df_detailed.to_csv(index=False),
        file_name="human_evaluation.csv",
        mime="text/csv"
    )
