import base64
import streamlit as st
import os
import datetime
import json
from backend import (
    load_json_dict,
    load_prompt,
    send_to_openai,
)

BASE_DIR = os.path.dirname(__file__)
PROMPT_PATH = "prompts"
RESOURCE_PATH = "resources"
image_path = os.path.join(BASE_DIR, RESOURCE_PATH, "scholeai.png")
url = "https://schole.ai"

def spacer(height=30):
    st.markdown(f"<div style='height: {height}px;'></div>", unsafe_allow_html=True)

# Initialize session state for steps tracking
if "step" not in st.session_state:
    st.session_state.step = 1
if "task_type" not in st.session_state:
    st.session_state.task_type = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "model" not in st.session_state:
    st.session_state.model = None
if "original_prompt" not in st.session_state:
    st.session_state.original_prompt = ""
if "edited_prompt" not in st.session_state:
    st.session_state.edited_prompt = ""
if "input_json_data" not in st.session_state:
    st.session_state.input_json_data = None
if "num_samples" not in st.session_state:
    st.session_state.num_samples = None
if "generated_result" not in st.session_state:
    st.session_state.generated_result = None
if "task_successful" not in st.session_state:
    st.session_state.task_successful = False

st.set_page_config(page_title="ScholéAI Data Generator", layout="centered")

# Header image & title
st.markdown(
    f"""
    <a href="{url}" target="_blank">
        <img src="data:image/png;base64,{base64.b64encode(open(image_path, "rb").read()).decode()}" 
             style="width: 100%;" />
    </a>
    """,
    unsafe_allow_html=True
)
st.markdown("<h3 style='text-align: center;'>A New Vision for Learning AI!</h3>", unsafe_allow_html=True)
spacer(100)

# === Step 1: Task Type Selection ===
if st.session_state.step == 1:
    task_types = ["Data Synthetization", "Data Augmentation", "Curriculum Generation"]
    st.markdown("🎯 **Select the task type**")
    cols = st.columns(len(task_types))
    for i, task in enumerate(task_types):
        if cols[i].button(task):
            st.session_state.task_type = task
            st.session_state.step = 2  # unlock next step
            # Reset downstream states on task change
            st.session_state.api_key = None
            st.session_state.model = None
            st.session_state.original_prompt = ""
            st.session_state.edited_prompt = ""
            st.session_state.input_json_data = None
            st.session_state.num_samples = None
            st.session_state.generated_result = None
            st.session_state.task_successful = False
            st.rerun()

# Show current selection if already chosen
if st.session_state.task_type and st.session_state.step > 1:
    st.write(f"**Current task:** {st.session_state.task_type}")

if st.session_state.step > 1:
    if st.button("Change Task"):
        # Reset relevant session state keys
        keys_to_reset = [
            "step", "task_type", "api_key", "model", "original_prompt", 
            "edited_prompt", "input_json_data", "num_samples", "generated_result", "task_successful",
            "learning_text", "profile_text"
        ]
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.step = 1
        st.rerun()

spacer(25)

# === Step 2: API Key Input ===
if st.session_state.step >= 2:
    api_key = st.text_input("\U0001F511 Enter your OpenAI API key", type="password", value=st.session_state.api_key or "")
    if api_key:
        st.session_state.api_key = api_key
        if st.session_state.step == 2:
            st.session_state.step = 3
    else:
        st.warning("Please enter your API key.")
        st.stop()

spacer(25)

# === Step 3: Model Selection ===
if st.session_state.step >= 3:
    model = st.selectbox("\U0001F9E0 Select the model", ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"], index=["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"].index(st.session_state.model) if st.session_state.model else 0)
    if model != st.session_state.model:
        st.session_state.model = model
        if st.session_state.step == 3:
            st.session_state.step = 4

spacer(25)

# === Step 4: Load and Edit Prompt ===
if st.session_state.step >= 4:
    # Load prompt once when we first reach this step
    if not st.session_state.original_prompt:
        try:
            st.session_state.original_prompt = load_prompt(st.session_state.task_type, base_dir=BASE_DIR)
            st.session_state.edited_prompt = st.session_state.original_prompt
        except Exception as e:
            st.error(f"Failed to load prompt: {e}")
            st.stop()

    edited_prompt = st.text_area("\U0001F4DD Prompt (editable)", value=st.session_state.edited_prompt, height=300)
    if edited_prompt != st.session_state.edited_prompt:
        st.session_state.edited_prompt = edited_prompt
        st.session_state.task_successful = False

    if st.session_state.step == 4:
        st.session_state.step = 5

spacer(25)

# === Step 5: Input / Configuration ===
if st.session_state.step >= 5:
    task_type = st.session_state.task_type
    input_json_data = None
    num_samples = 5 if task_type == "Data Synthetization" else 2
    learning_text = ""
    profile_text = ""
    num_samples_input = 0

    if task_type == "Data Augmentation":
        input_json_file = st.file_uploader("\U0001F4C1 Upload input JSON file for augmentation", type="json")
        if input_json_file:
            try:
                input_json_data = json.load(input_json_file)
                num_samples_input = len(input_json_data)
                st.markdown("\U0001F4DD **Input JSON**")
                st.code(json.dumps(input_json_data, indent=2), language="json")
            except Exception as e:
                st.error(f"Failed to load input JSON: {e}")
                st.stop()
        st.markdown(f"<span style='font-size: 13px;'>Number of detected samples in the input JSON: {num_samples_input}</span>", unsafe_allow_html=True)

    elif task_type == "Curriculum Generation":
        num_samples = st.slider("Select the number of learning curriculum pairs per sample", min_value=1, max_value=20, value=2, step=1)

        spacer(25)

        input_json_file = st.file_uploader("\U0001F4C1 Upload input JSON file for Curriculum Generation", type="json")

        if input_json_file:
            spacer(25)
            try:
                input_json_data = json.load(input_json_file)
                num_samples_input = len(input_json_data)
                st.markdown("\U0001F4DD **Input JSON**")
                st.code(json.dumps(input_json_data, indent=2), language="json")
            except Exception as e:
                st.error(f"Failed to load input JSON: {e}")
                st.stop()
        st.markdown(f"<span style='font-size: 13px;'>Number of detected samples in the input JSON: {num_samples_input}</span>", unsafe_allow_html=True)

    elif task_type == "Data Synthetization":
        learning_modalities = load_json_dict(os.path.join(BASE_DIR, "prompts", "learning_modalities.json"))
        student_profiles = load_json_dict(os.path.join(BASE_DIR, "prompts", "student_profiles.json"))

        learning_style_keys = ["random"] + list(learning_modalities.keys())
        selected_learning_style = st.selectbox("\U0001F4D8 Select a Learning Style", learning_style_keys)

        if selected_learning_style == "random":
            learning_text = "Assign each user one learning style at random from the list below, and generate data accordingly.\n"
            learning_text += "\n".join(f"{key}: {value}" for key, value in learning_modalities.items())
            st.info("One learning style will be randomly selected per data sample.")
        else:
            learning_text = learning_modalities[selected_learning_style]
            st.info(learning_text)

        spacer(25)

        profile_keys = ["random"] + list(student_profiles.keys())
        selected_student_profile = st.selectbox("\U0001F464 Select a Student Profile", profile_keys)

        if selected_student_profile == "random":
            profile_text = "Assign each user one student profile at random from the list below, and generate data accordingly.\n"
            profile_text += "\n".join(f"{key}: {value}" for key, value in student_profiles.items())
            st.info("One student profile will be randomly selected per data sample.")
        else:
            profile_text = student_profiles[selected_student_profile]
            st.info(profile_text)

        spacer(25)
        num_samples = st.slider("\U0001F501 Number of samples", min_value=1, max_value=50, value=5, step=1)

    # Save inputs in session state to keep consistent later
    st.session_state.input_json_data = input_json_data
    st.session_state.num_samples = num_samples
    st.session_state.learning_text = learning_text
    st.session_state.profile_text = profile_text

    if st.session_state.step == 5:
        st.session_state.step = 6

spacer(25)

# === Step 6: Send to OpenAI ===
if st.session_state.step >= 6:
    if st.button("\U0001F680 Send prompt to ChatGPT", use_container_width=True):
        st.session_state.task_successful = False
        try:
            if st.session_state.task_type == "Data Augmentation" and st.session_state.input_json_data:
                user_input = json.dumps(st.session_state.input_json_data, indent=2)

            elif st.session_state.task_type == "Curriculum Generation" and st.session_state.input_json_data:
                input_data = json.dumps(st.session_state.input_json_data, indent=2)
                user_input = f"Generate exactly {st.session_state.num_samples} learning curriculum pair(s) per user. Below is the input data:\n\n{input_data}"
            elif st.session_state.task_type == "Data Synthetization":
                user_input = (
                    f"Generate {st.session_state.num_samples} sample(s).\n\n"
                    f"[Learning Style]\n{st.session_state.learning_text}\n\n"
                    f"[Student Profile]\n{st.session_state.profile_text}"
                )
            else:
                user_input = ""

            with st.spinner("Generating response..."):
                result = send_to_openai(st.session_state.api_key, st.session_state.model, st.session_state.edited_prompt, user_input)
                st.session_state.generated_result = result
                st.session_state.task_successful = True
                st.session_state.step = 7
        except Exception as e:
            st.error(f"OpenAI API call failed: {e}")
            st.stop()

spacer(25)

# === Step 7: Display Result ===
if st.session_state.step >= 7 and st.session_state.generated_result:
    st.success("\u2705 Data received!")
    st.code(st.session_state.generated_result, language="json")
    st.session_state.step = 8

spacer(25)

# === Step 8: Download JSON ===
if st.session_state.step >= 8 and st.session_state.task_successful:
    try:
        result_json = json.loads(st.session_state.generated_result)
        st.download_button(
            label="\U0001F4E5 Download the generated JSON",
            data=json.dumps(result_json, indent=2),
            file_name=f"generated_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Failed to prepare download: {e}")

