# File        : utils.py
# Author      : Jérémy Chaverot
# Description : Utility functions for layout, styling, and shared logic used across Streamlit pages.

import streamlit as st
import base64
import hashlib
import os

BASE_DIR = os.path.dirname(__file__)
RESOURCE_PATH = os.path.join(BASE_DIR, "resources")
IMAGE_PATH = os.path.join(RESOURCE_PATH, "scholeai.png")
URL = "https://schole.ai"


def spacer(height=30):
    st.markdown(f"<div style='height: {height}px;'></div>", unsafe_allow_html=True)


def display_header():
    with open(IMAGE_PATH, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <a href="{URL}" target="_blank">
            <img src="data:image/png;base64,{img_data}" style="width: 100%;" />
        </a>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h3 style='text-align: center;'>A New Vision for Learning AI!</h3>", unsafe_allow_html=True)
    spacer(60)


def display_small_header():
    with open(IMAGE_PATH, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <div style="text-align: center;">
            <a href="{URL}" target="_blank">
                <img src="data:image/png;base64,{img_data}" style="width: 300px; max-width: 100%;" />
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    spacer(60)


def get_file_hash(file_bytes: bytes) -> str:
    return hashlib.md5(file_bytes).hexdigest()