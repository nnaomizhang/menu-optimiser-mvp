#Environment Configuration 
import streamlit as st
import os
import json
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from fpdf import FPDF

# Page Configuration
st.set_page_config(
    page_title="Restaurant Menu Optimiser",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Progression Bar
steps_complete = sum([
    "df" in st.session_state,
    "classification" in st.session_state.get("df", {}).columns if "df" in st.session_state else False,
    "recommendations" in st.session_state,
    "pdf" in st.session_state
])
st.progress(steps_complete / 4, text=f"Progress: {steps_complete}/4 steps complete")

# Page Styling
st.markdown("""
<style>
    .main { background-color: #FAFAF8; }
    .block-container { padding-top: 2rem; }
    h1 { color: #1A1A2E; font-family: Georgia, serif; }
    h2, h3 { color: #2C3E50; }
    .step-header {
        background: linear-gradient(135deg, #1A1A2E, #16213E);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-weight: bold;
        font-size: 1rem;
    }
    .metric-card {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)
