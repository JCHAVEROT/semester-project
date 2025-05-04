import streamlit as st
import json
import os
import re
import datetime
from openai import OpenAI

# Helper function
def strip_json_markers(data: str) -> str:
    return re.sub(r"^```(?:json)?\n|```$", "", data.strip())


# --- Streamlit UI ---
st.set_page_config(page_title="ScholéAI Data Generator", layout="centered")
st.title("ScholéAI: Data Synthetizer & Augmentor")

# Step 1: API key input
api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
if not api_key:
    st.warning("Please enter your API key.")
    st.stop()

# Reset success if API key is modified
if "last_api_key" not in st.session_state or st.session_state.last_api_key != api_key:
    st.session_state.task_successful = False
    st.session_state.last_api_key = api_key

# Step 2: Task type
task_type = st.selectbox("🎯 Select the task type", ["Data Synthetization", "Data Augmentation"])
if "last_task_type" not in st.session_state or st.session_state.last_task_type != task_type:
    # Reset the prompt when the task type changes
    st.session_state.task_successful = False
    st.session_state.last_task_type = task_type

    # Load the corresponding prompt
    prompt_file = os.path.join("prompt", "data-synthetization.json") if task_type == "Data Synthetization" else os.path.join("prompt", "data-augmentation.json")

    try:
        with open(prompt_file, "r") as f:
            prompt_data = json.load(f)
            original_prompt = prompt_data["prompt"]
    except Exception as e:
        st.error(f"Failed to load prompt: {e}")
        st.stop()

    # Store the original prompt in session state
    st.session_state.original_prompt = original_prompt

# Step 3: Select model
model = st.selectbox("🧠 Select the model", ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"])
if "last_model" not in st.session_state or st.session_state.last_model != model:
    st.session_state.task_successful = False
    st.session_state.last_model = model

# Step 4: Load and edit prompt
edited_prompt = st.text_area("📝 Prompt (editable)", value=st.session_state.original_prompt, height=300)
if edited_prompt != st.session_state.original_prompt:
    st.session_state.task_successful = False
    st.session_state.original_prompt = edited_prompt

# Step 5: Input JSON path (only for Data Augmentation)
input_json_path = None
input_json_data = None
num_samples = 5  # Default number of samples for synthesis
if task_type == "Data Augmentation":
    input_json_path = st.text_input("📁 Path to input JSON file for augmentation", value="")
    
    if input_json_path:
        try:
            # Load the input JSON for augmentation
            with open(input_json_path, "r") as f:
                input_json_data = json.load(f)
            
            # Infer the number of samples based on the loaded JSON (assume it's a list)
            num_samples = len(input_json_data)
            # Display the content of the input JSON
            st.markdown("📝 **Input JSON**")
            st.code(json.dumps(input_json_data, indent=2), language="json")

        except Exception as e:
            st.error(f"Failed to load input JSON file: {e}")
            st.stop()

    # Disable number of samples input for augmentation
    st.write(f"🔢 Number of samples (inferred from JSON): {num_samples}")
else:
    # Step 6: Number of samples (enabled for Synthetization)
    num_samples = st.number_input("🔁 Number of samples", min_value=1, max_value=100, value=5, step=1)
    if "last_num_samples" not in st.session_state or st.session_state.last_num_samples != num_samples:
        st.session_state.task_successful = False
        st.session_state.last_num_samples = num_samples

# Step 7: Send request
if st.button("🚀 Send prompt to ChatGPT"):
    st.session_state.task_successful = False
    try:
        client = OpenAI(api_key=api_key)

        if task_type == "Data Augmentation" and input_json_data:
            input = json.dumps(input_json_data, indent=2)
        else:
            input = f"Generate {num_samples} sample(s)."

        with st.spinner("Generating response..."):
            response = client.responses.create(
                instructions=edited_prompt,
                model=model,
                input=input,
            )
            result = response.to_dict()["output"][0]["content"][0]["text"]
            result = strip_json_markers(result)
            st.success("✅ Data received!")
            st.code(result, language="json")

            st.session_state.generated_result = result
            st.session_state.task_successful = True

    except Exception as e:
        st.error(f"OpenAI API call failed: {e}")
        st.session_state.task_successful = False
        st.stop()

# Step 8: Save output only if generation was successful
if st.session_state.get("task_successful", False):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    if task_type == "Data Augmentation" and input_json_path:
        # Extract file name from input JSON path for augmentation
        input_json_filename = os.path.basename(input_json_path).split(".")[0]
        default_filename = f"output/{input_json_filename}_augmented.json"
    else:
        plural_s = "s" if num_samples > 1 else ""
        default_filename = f"output/synth_{num_samples}-sample{plural_s}_{model}_{timestamp}.json"

    save_path = st.text_input("💾 Path to save JSON output", value=default_filename)

    if save_path and st.button("📥 Save to file"):
        try:
            parsed_result = json.loads(st.session_state.generated_result)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "w") as f:
                json.dump(parsed_result, f, indent=2)
            st.success(f"Saved output to {save_path}")
        except Exception as e:
            st.error(f"Failed to save file: {e}")
