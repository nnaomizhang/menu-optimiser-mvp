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

# Header
st.title("Restaurant Menu Optimiser")
st.caption("Upload your menu data to get AI-powered pricing recommendations and margin optimisation.")

# Sidebar 

api_key = None
if hasattr(st, "secrets"):
    api_key = st.secrets.get("OPENAI_API_KEY")
if not api_key:
    api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")

model = st.sidebar.selectbox("Model", ["gpt-4o-mini"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)

llm = ChatOpenAI(
    model=model,
    temperature=temperature,
    api_key=api_key
) if api_key else None

st.sidebar.markdown("---")
st.sidebar.markdown("### Required CSV Columns")
st.sidebar.markdown("""
- `item_name`
- `category`
- `current_price`
- `food_cost`
- `monthly_units_sold`
""")