# pages/1_Data_Synthetization.py

import streamlit as st
import sys
import os
import json
import datetime

sys.path.append(os.path.abspath(".."))
import utils
import backend

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "prompts")


# === Page Configuration ===
st.set_page_config(page_title="Data Synthetization", layout="centered")
utils.display_small_header()

# === Header ===
st.title("Data Synthetization")
st.markdown("Generate synthetic student preference and behavioral data for Scholé.")
utils.spacer(45)

# === API Key and Model ===
api_key = st.text_input("🔑 OpenAI API Key", type="password")
utils.spacer()
model = st.selectbox("🤖 Model", ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"])
utils.spacer()

# === Prompt Editor ===
try:
    default_prompt = backend.load_prompt("Data Synthetization", base_dir=BASE_DIR)
except Exception as e:
    st.error(f"Failed to load default prompt: {e}")
    st.stop()
edited_prompt = st.text_area("📜 Prompt Template", value=default_prompt, height=300)
utils.spacer()

# === Learning Styles and Profiles ===
modalities = backend.load_json_dict(os.path.join(PROMPT_PATH, "learning_modalities.json"))
profiles = backend.load_json_dict(os.path.join(PROMPT_PATH, "student_profiles.json"))

selected_style = st.selectbox("📘 Learning Modality", ["random"] + list(modalities.keys()))
learning_text = modalities.get(selected_style, "") if selected_style != "random" else "\n".join(f"{k}: {v}" for k, v in modalities.items())
if selected_style != "" and selected_style != "random":
        st.info(f"{learning_text}")
utils.spacer()

selected_profile = st.selectbox("👤 Student Profile", ["random"] + list(profiles.keys()))
profile_text = profiles.get(selected_profile, "") if selected_profile != "random" else "\n".join(f"{k}: {v}" for k, v in profiles.items())
if selected_profile != "" and selected_profile != "random":
        st.info(f"{profile_text}")
    
utils.spacer()


num_samples = st.slider("🔁 Number of Samples", 1, 50, 5)
utils.spacer()

# === Submit Button ===
if st.button("🚀 Generate Synthetic Data", use_container_width=True):
    utils.spacer(20)
    
    if not api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()

    # If random modality or profile, give more instructions to the model
    modality_instruction = (
        "[Learning Style]\nChoose one learning modality randomly for each sample from the following:\n" + learning_text
        if selected_style == "random" else f"[Learning Style]\n{learning_text}"
    )

    profile_instruction = (
        "[Student Profile]\nChoose one student profile randomly for each sample from the following:\n" + profile_text
        if selected_profile == "random" else f"[Student Profile]\n{profile_text}"
    )

    user_input = f"Generate {num_samples} sample(s).\n\n{modality_instruction}\n\n{profile_instruction}"

    with st.spinner("Contacting OpenAI API..."):
        try:
            result = backend.send_to_openai(api_key, model, edited_prompt, user_input)
            st.success("✅ Data generation successful!")
            st.code(result, language="json")

            try:
                result_json = json.loads(result)
                st.download_button(
                    label="📥 Download JSON",
                    data=json.dumps(result_json, indent=2),
                    file_name=f"generated_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.json",
                    mime="application/json"
                )
            except Exception:
                st.warning("The result is not valid JSON.")
        except Exception as e:
            st.error(f"OpenAI API call failed: {e}")