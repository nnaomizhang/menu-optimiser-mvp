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
