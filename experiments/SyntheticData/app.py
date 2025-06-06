# File        : app.py
# Author      : Jérémy Chaverot
# Description : Main page of the Streamlit app with task selection.

import streamlit as st
import utils


# === Page Configuration ===
st.set_page_config(page_title="ScholéAI Data Generator", layout="centered")
utils.display_header()
utils.spacer()

# === Page Content ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🧬\nSynthetization"):
        st.switch_page("pages/1_🧬_Data_Synthetization.py")
    st.caption("Generate synthetic student preference and behavioral data for Scholé.")

with col2:
    if st.button("➕\nAugmentation"):
        st.switch_page("pages/2_➕_Data_Augmentation.py")
    st.caption("Augment existing data samples with artificial preferences.")

with col3:
    if st.button("📚\nCurriculum"):
        st.switch_page("pages/3_📚_Curriculum_Generation.py")
    st.caption("Create chosen vs. rejected learning plan pairs for each student profile.")

with col4:
    if st.button("🔍\nEvaluation"):
        st.switch_page("pages/4_🔍_Synthetic_Evaluation.py")
    st.caption("Review and rate synthetic datasets sample-by-sample.")
