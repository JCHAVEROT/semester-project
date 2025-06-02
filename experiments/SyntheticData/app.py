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

# Define paths
BASE_DIR = os.path.dirname(__file__)
PROMPT_PATH = "prompts"
RESOURCE_PATH = "resources"
image_path = os.path.join(BASE_DIR, RESOURCE_PATH, "scholeai.png")
url = "https://schole.ai"

# Helper function for UI
def spacer(height=30):
    st.markdown(f"<div style='height: {height}px;'></div>", unsafe_allow_html=True)

# WebApp header
st.set_page_config(page_title="ScholéAI Data Generator", layout="centered")
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

# Step 1: API key input
api_key = st.text_input("\U0001F511 Enter your OpenAI API key", type="password")
if not api_key:
    st.warning("Please enter your API key.")
    st.stop()

if "last_api_key" not in st.session_state or st.session_state.last_api_key != api_key:
    st.session_state.task_successful = False
    st.session_state.last_api_key = api_key

spacer(25)

# Step 2: Task type
task_type = st.selectbox("\U0001F3AF Select the task type", ["Data Synthetization", "Data Augmentation", "Learning Curriculums Generation"])
if "last_task_type" not in st.session_state or st.session_state.last_task_type != task_type:
    st.session_state.task_successful = False
    st.session_state.last_task_type = task_type
    st.session_state.generated_result = None
    try:
        st.session_state.original_prompt = load_prompt(task_type, base_dir=BASE_DIR)
    except Exception as e:
        st.error(f"Failed to load prompt: {e}")
        st.stop()

spacer(25)

# Step 3: Model selection
model = st.selectbox("\U0001F9E0 Select the model", ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"])
if "last_model" not in st.session_state or st.session_state.last_model != model:
    st.session_state.task_successful = False
    st.session_state.last_model = model
    st.session_state.generated_result = None

spacer(25)

# Step 4: Prompt
edited_prompt = st.text_area("\U0001F4DD Prompt (editable)", value=st.session_state.original_prompt, height=300)
if edited_prompt != st.session_state.original_prompt:
    st.session_state.task_successful = False
    st.session_state.original_prompt = edited_prompt

spacer(25)

# Step 5: Input / configuration
input_json_data = None
num_samples = 5 if task_type == "Data Synthetization" else 0
learning_text = ""
profile_text = ""

if task_type == "Data Augmentation":
    input_json_file = st.file_uploader("\U0001F4C1 Upload input JSON file for augmentation", type="json")
    if input_json_file:
        try:
            input_json_data = json.load(input_json_file)
            num_samples = len(input_json_data)
            st.markdown("\U0001F4DD **Input JSON**")
            st.code(json.dumps(input_json_data, indent=2), language="json")
        except Exception as e:
            st.error(f"Failed to load input JSON: {e}")
            st.stop()
    st.write(f"\U0001F522 Number of samples: {num_samples}")

elif task_type == "Learning Curriculums Generation":
    input_json_file = st.file_uploader("\U0001F4C1 Upload input JSON file for learning curriculums generation", type="json")
    if input_json_file:
        try:
            input_json_data = json.load(input_json_file)
            num_samples = len(input_json_data)
            st.markdown("\U0001F4DD **Input JSON**")
            st.code(json.dumps(input_json_data, indent=2), language="json")
        except Exception as e:
            st.error(f"Failed to load input JSON: {e}")
            st.stop()
    st.write(f"\U0001F522 Number of samples: {num_samples}")

elif task_type == "Data Synthetization":
    learning_styles = load_json_dict(os.path.join(BASE_DIR, "prompts", "learning_styles.json"))
    student_profiles = load_json_dict(os.path.join(BASE_DIR, "prompts", "student_profiles.json"))

    learning_style_keys = ["random"] + list(learning_styles.keys())
    selected_learning_style = st.selectbox("\U0001F4D8 Select a Learning Style", learning_style_keys)

    if selected_learning_style == "random":
        learning_text = "Assign each user one learning style at random from the list below, and generate data accordingly.\n"
        learning_text += "\n".join(f"{key}: {value}" for key, value in learning_styles.items())
        st.info("One learning style will be randomly selected per data sample.")
    else:
        learning_text = learning_styles[selected_learning_style]
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
    if "last_num_samples" not in st.session_state or st.session_state.last_num_samples != num_samples:
        st.session_state.task_successful = False
        st.session_state.last_num_samples = num_samples

spacer(25)

# Step 6: Send to OpenAI
if st.button("\U0001F680 Send prompt to ChatGPT", use_container_width=True):
    st.session_state.task_successful = False
    try:
        if (task_type == "Data Augmentation" or task_type == "Learning Curriculums Generation") and input_json_data:
            user_input = json.dumps(input_json_data, indent=2)

        elif task_type == "Data Synthetization":
            user_input = f"Generate {num_samples} sample(s).\n\n[Learning Style]\n{learning_text}\n\n[Student Profile]\n{profile_text}"

        with st.spinner("Generating response..."):
            result = send_to_openai(api_key, model, edited_prompt, user_input)
            st.session_state.generated_result = result
            st.session_state.task_successful = True

    except Exception as e:
        st.error(f"OpenAI API call failed: {e}")
        st.stop()

spacer(25)

# Step 7: Display result
if "generated_result" in st.session_state and st.session_state.generated_result:
    st.success("\u2705 Data received!")
    st.code(st.session_state.generated_result, language="json")

spacer(25)

# Step 8: Download JSON
if st.session_state.get("task_successful", False):
    result_json = json.loads(st.session_state.generated_result)
    st.download_button(
        label="\U0001F4E5 Download the generated JSON",
        data=json.dumps(result_json, indent=2),
        file_name=f"generated_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.json",
        mime="application/json"
    )