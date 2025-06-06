# pages/2_Data_Augmentation.py

import streamlit as st
import sys
import os
import json
import datetime

sys.path.append(os.path.abspath(".."))
import utils
import backend

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# === Page Configuration ===
st.set_page_config(page_title="Data Augmentation", layout="centered")
utils.display_small_header()

# === Header ===
st.title("Data Augmentation")
st.markdown("Augment existing data samples with artificial preferences.")
utils.spacer(45)

# === API Key and Model ===
api_key = st.text_input("🔑 OpenAI API Key", type="password")
utils.spacer()
model = st.selectbox("🤖 Model", ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"])
utils.spacer()

# === Prompt Editor ===
try:
    default_prompt = backend.load_prompt("Data Augmentation", base_dir=BASE_DIR)
except Exception as e:
    st.error(f"Failed to load default prompt: {e}")
    st.stop()

edited_prompt = st.text_area("📜 Prompt Template", value=default_prompt, height=300)
utils.spacer()

# === Input JSON Upload ===
input_json_file = st.file_uploader("📁 Upload JSON file to augment", type="json")
input_json_data = None
if input_json_file:
    try:
        input_json_data = json.load(input_json_file)
        with st.expander("Show input JSON preview"):
            st.caption(f"Number of detected samples: {len(input_json_data)}")
            st.code(json.dumps(input_json_data, indent=2), language="json")

    except Exception as e:
        st.error(f"Failed to load JSON: {e}")
        st.stop()
utils.spacer()

# === Generate Button ===
if st.button("🚀 Augment Your Data", use_container_width=True):
    utils.spacer(20)

    if not api_key:
        st.error("Please enter your OpenAI API key.")
        st.stop()

    if not input_json_data:
        st.error("Please upload a valid input JSON file.")
        st.stop()

    user_input = json.dumps(input_json_data, indent=2)

    with st.spinner("Contacting OpenAI API..."):
        try:
            result = backend.send_to_openai(api_key, model, edited_prompt, user_input)
            st.success("✅ Data augmentation successful!")
            st.code(result, language="json")

            try:
                result_json = json.loads(result)
                st.download_button(
                    label="📥 Download Augmented JSON",
                    data=json.dumps(result_json, indent=2),
                    file_name=f"augmented_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.json",
                    mime="application/json"
                )
            except Exception:
                st.warning("The result is not valid JSON.")
        except Exception as e:
            st.error(f"OpenAI API call failed: {e}")