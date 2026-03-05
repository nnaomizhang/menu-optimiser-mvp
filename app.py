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

#Page Configuration
st.set_page_config(
    page_title="Restaurant Menu Optimiser",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)


