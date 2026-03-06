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

# Step 0: Set-up ─────────────────────────────────────────────────────────────

# Page Configuration
st.set_page_config(
    page_title="MenuMind",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Progression Bar
steps_complete = sum([
    "df" in st.session_state,
    "classification" in st.session_state.get("df", {}).columns if "df" in st.session_state else False,
    "recommendations" in st.session_state,
    "pdf" in st.session_state
])
st.progress(steps_complete / 4, text=f"Progress: {steps_complete}/4 steps complete")

# Sidebar 
api_key = st.secrets.get("OPENAI_API_KEY")
model = "gpt-4o-mini"
temperature = 0

llm = ChatOpenAI(
    model=model,
    temperature=temperature,
    api_key=api_key
) if api_key else None

# Custom Styling ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:          #F2F0EC;
    --bg-2:        #F2F0EC;
    --bg-3:        #DDD8CE;
    --navy:        #22314C;
    --navy-light:  #DDD8CE;
    --navy-dim:    rgba(34,49,76,0.08);
    --ink:         #1A1A1A;
    --muted:       #7A7060;
    --green:       #3A7D5C;
    --amber:       #B5703A;
    --red:         #A04040;
    --blue:        #2E5F8A;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stDecoration"] {display: none;}

.stApp { background-color: var(--bg); }
.main  { background-color: transparent; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem;
    max-width: 1080px;
}

h1, h2, h3, h4 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--navy) !important;
}
p, li, label {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--ink);
}

.step-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.9rem 1.4rem;
    background: var(--bg-3);
    border-left: 3px solid var(--amber);
    border-radius: 0 8px 8px 0;
    margin-bottom: 1.5rem;
}
.step-number {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.2rem;
    color: #EFE7D5;
    font-weight: 700;
    min-width: 28px;
    opacity: 0.5;
}
.step-title {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem;
    color: #EFE7D5 !important;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.step-desc {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem;
    color: #8A9BB0 !important;
    margin-top: 2px;
}

.stButton > button {
    background: var(--bg-3) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.55rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--navy-light) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(34,49,76,0.25) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}
.stDownloadButton > button {
    background: transparent !important;
    color: var(--bg-3) !important;
    border: 1px solid var(--bg-3) !important;
    border-radius: 6px !important;
    padding: 0.55rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: var(--navy-dim) !important;
    box-shadow: 0 4px 16px rgba(34,49,76,0.15) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stFileUploader"] {
    background: var(--bg-2) !important;
    border: 1px dashed rgba(34,49,76,0.3) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(---bg-3) !important;
    background: var(--bg-3) !important;
}

[data-testid="stMetric"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--bg-3) !important;
    border-top: 2px solid var(--bg-3) !important;
    border-radius: 8px !important;
    padding: 1.2rem !important;
    transition: box-shadow 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 20px rgba(34,49,76,0.12) !important;
}
[data-testid="stMetricLabel"] > div {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] > div {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: var(--bg-3) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--bg-3) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

[data-testid="stAlert"] {
    background: var(--bg-2) !important;
    border-radius: 8px !important;
    border: 1px solid var(--bg-3) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
}
.stSuccess > div { border-left: 3px solid var(--green) !important; }
.stInfo    > div { border-left: 3px solid var(--blue) !important; }
.stWarning > div { border-left: 3px solid var(--amber) !important; }
.stError   > div { border-left: 3px solid var(--red) !important; }

[data-testid="stExpander"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--bg-3) !important;
    border-radius: 8px !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"] summary {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] summary:hover {
    color: var(--bg-3) !important;
}

hr {
    border: none !important;
    height: 1px !important;
    background: var(--bg-3) !important;
    margin: 2rem 0 !important;
}

.stSpinner > div > div {
    border-top-color: var(--bg-3) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    background: #22314C;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    border-radius: 0 0 12px 12px;
">
    <div style="font-size:0.7rem; letter-spacing:4px; text-transform:uppercase;
                color:#8A9BB0; margin-bottom:0.8rem; font-family:'DM Sans',sans-serif;">
        AI-Powered Restaurant Intelligence
    </div>
    <div style="font-family:'DM Sans',sans-serif; font-size:2.8rem; letter-spacing:-1px;
                color:#EFE7D5; font-weight:700; margin-bottom:0.6rem;">
        MenuMind
    </div>
    <div style="
    font-size: 0.55rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #8A9BB0;
    font-family: 'DM Sans', sans-serif;
    margin: 0 auto;
    line-height: 1.6;
">
    Transform your menu data into precision pricing strategy
</div>

</div>
""", unsafe_allow_html=True)

# Introduce Context
if "restaurant_name" not in st.session_state:
    st.markdown("""
<div style="
    max-width: 580px;
    margin: 0 auto 2rem auto;
    text-align: center;
">
    <p style="font-size: 0.8rem; color: #7A7060; line-height: 1.8; font-family: 'DM Sans', sans-serif;">
        MenuMind applies institutional-grade menu engineering methodology to your data — 
        delivering precise pricing intelligence and a boardroom-ready report, 
        without the consultant fees.
    </p>
    <p style="font-size: 0.7rem; color: #A09880; font-family: 'DM Sans', sans-serif;">
        You'll need a spreadsheet with your item names, prices, food costs, and monthly sales. 
        The whole process takes under 2 minutes.
    </p>
</div>
""", unsafe_allow_html=True)

    restaurant_name = st.text_input(
        "Enter your restaurant name to get started",
        placeholder="e.g. The Paradosiako",
    )

    if st.button("Enter →"):
        if not restaurant_name:
            st.warning("Please enter your restaurant name to continue.")
            st.stop()
        else:
            st.session_state["restaurant_name"] = restaurant_name
            st.rerun()

    st.stop()

# PDF Generator 
def clean_text(text: str) -> str:
    """Replace special characters that fpdf2 can't handle in built-in fonts."""
    replacements = {
        "\u2014": "-",   # em dash —
        "\u2013": "-",   # en dash –
        "\u2018": "'",   # left single quote '
        "\u2019": "'",   # right single quote '
        "\u201c": '"',   # left double quote "
        "\u201d": '"',   # right double quote "
        "\u2022": "-",   # bullet •
        "\u00a3": "GBP", # £ sign
        "\u00e9": "e",   # é
        "\u00e8": "e",   # è
        "\u00ea": "e",   # ê
        "\u00e0": "a",   # à
        "\u00e2": "a",   # â
        "\u00f4": "o",   # ô
        "\u00fb": "u",   # û
        "\u00ee": "i",   # î
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def generate_pdf(df, recommendations, summary):
    pdf = FPDF()
    pdf.add_page()

    # ── Title ─────────────────────────────────────────────────────────────
    pdf.set_font("Times", "B", 18)
    restaurant = st.session_state.get("restaurant_name", "Your Restaurant")
    pdf.cell(0, 12, clean_text(f"{restaurant} — Menu Optimisation Report"), ln=True, align="C")
    pdf.set_font("Times", size=9)
    pdf.cell(0, 6, "Generated by MenuMind", ln=True, align="C") 
    pdf.ln(4)

    # ── Performance Overview ──────────────────────────────────────────────
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 8, "Performance Overview", ln=True)
    pdf.set_font("Times", size=10)
    pdf.cell(0, 6, f"Total Monthly Revenue:  £{df['monthly_revenue'].sum():,.2f}", ln=True)
    pdf.cell(0, 6, f"Total Monthly Profit:   £{df['monthly_profit'].sum():,.2f}", ln=True)
    pdf.cell(0, 6, f"Average Margin:         {df['margin_pct'].mean():.1f}%", ln=True)
    pdf.cell(0, 6, f"Total Menu Items:       {len(df)}", ln=True)
    pdf.ln(4)

    # ── Classification Summary ────────────────────────────────────────────
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 8, "Classification Summary", ln=True)
    pdf.set_font("Times", size=10)
    counts = df["classification"].value_counts()
    for label in ["Signature", "Speciality", "Staple", "Marginal"]:
        pdf.cell(0, 6, f"  {label}: {counts.get(label, 0)} items", ln=True)
    pdf.ln(4)

    # ── Executive Summary ─────────────────────────────────────────────────
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 8, "Executive Summary", ln=True)
    pdf.set_font("Times", size=10)
    pdf.multi_cell(0, 6, clean_text(summary))
    pdf.ln(4)

    # ── Menu Engineering Table ────────────────────────────────────────────
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 8, "Menu Engineering Classifications", ln=True)
    pdf.set_font("Times", "B", 9)
    headers = ["Item",  "Category", "Price",  "Food Cost", "Margin%", "Units/Mo", "Classification"]
    widths  = [42,       22,         18,        20,          18,        20,          33]
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1)
    pdf.ln()
    pdf.set_font("Times", size=9)
    for _, row in df.iterrows():
        pdf.cell(42, 6, clean_text(str(row["item_name"]))[:22],      border=1)
        pdf.cell(22, 6, clean_text(str(row["category"]))[:12],       border=1)
        pdf.cell(18, 6, f"GBP {row['current_price']:.2f}",           border=1)
        pdf.cell(20, 6, f"GBP {row['food_cost']:.2f}",               border=1)
        pdf.cell(18, 6, f"{row['margin_pct']:.1f}%",                 border=1)
        pdf.cell(20, 6, str(int(row["monthly_units_sold"])),          border=1)
        pdf.cell(33, 6, clean_text(str(row["classification"]))[:18],  border=1)
        pdf.ln()
    pdf.ln(4)

    # ── Pricing Recommendations ───────────────────────────────────────────
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 8, "AI Pricing Recommendations", ln=True)
    for rec in recommendations:
        pdf.set_font("Times", "B", 10)
        item   = clean_text(str(rec.get("item_name", "")))
        action = clean_text(str(rec.get("action", "")))
        pdf.cell(0, 7, f"{item} - {action}", ln=True)
        pdf.set_font("Times", size=9)
        curr  = rec.get("current_price", 0)
        recp  = rec.get("recommended_price", 0)
        impact = clean_text(str(rec.get("projected_monthly_impact", "N/A")))
        pdf.cell(0, 6,
                 f"  Price: GBP {curr:.2f} to GBP {recp:.2f}  |  Impact: {impact}",
                 ln=True)
        reasoning = clean_text(str(rec.get("reasoning", "")))
        pdf.multi_cell(0, 6, f"  {reasoning}")
        pdf.ln(1)
    
    # Fixed
    output = pdf.output(dest="S")
    if isinstance(output, (bytes, bytearray)):
        return bytes(output)
    return output.encode("latin-1")

# Step 1: Manual Entry OR Upload ───────────────────────────────

st.markdown('<div class="step-header">Step 1 — Enter Your Menu Data</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Enter Manually", "Upload Spreadsheet"])

# ── TAB 1: Manual Entry ───────────────────────────────────────────────────────
with tab1:
    st.markdown("""
<p style="font-size:0.85rem; color:#7A7060; font-family:'DM Sans',sans-serif; margin-bottom:1rem;">
    Type your menu items directly below. Add as many rows as you need.
</p>
""", unsafe_allow_html=True)

    if "manual_items" not in st.session_state:
        st.session_state["manual_items"] = [
            {"item_name": "", "category": "Mains", "current_price": 0.0,
             "food_cost": 0.0, "monthly_units_sold": 0}
        ]

    CATEGORIES = ["Starters", "Mains", "Sides", "Desserts", "Drinks", "Sharing", "Other"]

    for i, item in enumerate(st.session_state["manual_items"]):
        col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1.5, 1.5, 1.5, 0.5])
        with col1:
            st.session_state["manual_items"][i]["item_name"] = st.text_input(
                "Item Name" if i == 0 else " ",
                value=item["item_name"],
                placeholder="e.g. Grilled Halloumi",
                key=f"name_{i}",
                label_visibility="visible" if i == 0 else "collapsed"
            )
        with col2:
            st.session_state["manual_items"][i]["category"] = st.selectbox(
                "Category" if i == 0 else " ",
                CATEGORIES,
                index=CATEGORIES.index(item["category"]) if item["category"] in CATEGORIES else 0,
                key=f"cat_{i}",
                label_visibility="visible" if i == 0 else "collapsed"
            )
        with col3:
            st.session_state["manual_items"][i]["current_price"] = st.number_input(
                "Selling Price (£)" if i == 0 else " ",
                min_value=0.0, step=0.50,
                value=float(item["current_price"]),
                key=f"price_{i}",
                label_visibility="visible" if i == 0 else "collapsed"
            )
        with col4:
            st.session_state["manual_items"][i]["food_cost"] = st.number_input(
                "Food Cost (£)" if i == 0 else " ",
                min_value=0.0, step=0.50,
                value=float(item["food_cost"]),
                key=f"cost_{i}",
                label_visibility="visible" if i == 0 else "collapsed"
            )
        with col5:
            st.session_state["manual_items"][i]["monthly_units_sold"] = st.number_input(
                "Monthly Sales" if i == 0 else " ",
                min_value=0, step=1,
                value=int(item["monthly_units_sold"]),
                key=f"units_{i}",
                label_visibility="visible" if i == 0 else "collapsed"
            )
        with col6:
            st.markdown("<div style='margin-top: 1.8rem;'>", unsafe_allow_html=True)
            if st.button("✕", key=f"del_{i}", help="Remove this item"):
                st.session_state["manual_items"].pop(i)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("+ Add Item"):
            st.session_state["manual_items"].append(
                {"item_name": "", "category": "Mains", "current_price": 0.0,
                 "food_cost": 0.0, "monthly_units_sold": 0}
            )
            st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button("Validate Data", key="validate_manual"):
        items = st.session_state["manual_items"]
        empty = [i+1 for i, item in enumerate(items) if not item["item_name"].strip()]
        if empty:
            st.error(f"Please enter a name for row(s): {empty}")
        elif len(items) < 4:
            st.warning("Add at least 4 items for a meaningful analysis.")
        else:
            df_raw = pd.DataFrame(items)
            df_raw["gross_margin"]    = df_raw["current_price"] - df_raw["food_cost"]
            df_raw["margin_pct"]      = (df_raw["gross_margin"] / df_raw["current_price"]) * 100
            df_raw["monthly_revenue"] = df_raw["current_price"] * df_raw["monthly_units_sold"]
            df_raw["monthly_profit"]  = df_raw["gross_margin"]  * df_raw["monthly_units_sold"]
            st.session_state["df"] = df_raw
            st.session_state.pop("recommendations", None)
            st.session_state.pop("summary", None)
            st.success(f"Data validated — {len(df_raw)} menu items loaded.")
            
# ── TAB 2: Upload ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
<p style="font-size:0.85rem; color:#7A7060; font-family:'DM Sans',sans-serif; margin-bottom:1rem;">
    Download the template, fill it in, and upload it here.
    Works with Excel and CSV files.
</p>
""", unsafe_allow_html=True)

    with st.expander("Download starter template"):
        st.markdown("""
| Column | What to enter |
|---|---|
| **Item Name** | e.g. Grilled Halloumi |
| **Category** | e.g. Starters, Mains, Drinks |
| **Selling Price** | What you charge the customer in £ |
| **Food Cost** | What the ingredients cost you in £ |
| **Monthly Sales** | How many you sell in a typical month |
""")
        template_df = pd.DataFrame([
            {"Item Name": "Grilled Halloumi",   "Category": "Starters", "Selling Price": 8.50,  "Food Cost": 3.20, "Monthly Sales": 120},
            {"Item Name": "Chicken Souvlaki",   "Category": "Mains",    "Selling Price": 14.50, "Food Cost": 4.80, "Monthly Sales": 95},
            {"Item Name": "Greek Salad",        "Category": "Sides",    "Selling Price": 7.00,  "Food Cost": 1.80, "Monthly Sales": 150},
            {"Item Name": "Baklava",            "Category": "Desserts", "Selling Price": 6.50,  "Food Cost": 1.80, "Monthly Sales": 60},
            {"Item Name": "House Wine (Glass)", "Category": "Drinks",   "Selling Price": 7.50,  "Food Cost": 2.20, "Monthly Sales": 180},
        ])
        st.download_button(
            label="Download Template (CSV)",
            data=template_df.to_csv(index=False),
            file_name="menumind_template.csv",
            mime="text/csv"
        )

    COLUMN_MAP = {
        "Item Name": "item_name", "Category": "category",
        "Selling Price": "current_price", "Food Cost": "food_cost",
        "Monthly Sales": "monthly_units_sold",
        "item_name": "item_name", "category": "category",
        "current_price": "current_price", "food_cost": "food_cost",
        "monthly_units_sold": "monthly_units_sold",
    }

    uploaded_file = st.file_uploader(
        "Upload your completed template",
        type=["csv", "xlsx"],
    )

    if st.button("Validate Data", key="validate_upload", disabled=uploaded_file is None):
        try:
            df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            df_raw = df_raw.rename(columns=COLUMN_MAP)
            required_cols = ["item_name", "category", "current_price", "food_cost", "monthly_units_sold"]
            missing = [c for c in required_cols if c not in df_raw.columns]
            if missing:
                st.error(f"Could not find these columns: {missing}. Please use the provided template.")
            else:
                df_raw["gross_margin"]    = df_raw["current_price"] - df_raw["food_cost"]
                df_raw["margin_pct"]      = (df_raw["gross_margin"] / df_raw["current_price"]) * 100
                df_raw["monthly_revenue"] = df_raw["current_price"] * df_raw["monthly_units_sold"]
                df_raw["monthly_profit"]  = df_raw["gross_margin"]  * df_raw["monthly_units_sold"]
                st.session_state["df"] = df_raw
                st.session_state.pop("recommendations", None)
                st.session_state.pop("summary", None)
                st.success(f"Data validated — {len(df_raw)} menu items loaded.")
        except Exception as e:
            st.error(f"Failed to read file: {e}")
       
# ── Shared metrics shown after either method validates ────────────────────────
if "df" in st.session_state:
    df = st.session_state["df"]
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Items",     len(df))
    col2.metric("Monthly Revenue", f"£{df['monthly_revenue'].sum():,.2f}")
    col3.metric("Monthly Profit",  f"£{df['monthly_profit'].sum():,.2f}")
    col4.metric("Avg Margin",      f"{df['margin_pct'].mean():.1f}%")

    st.dataframe(
        df[["item_name", "category", "current_price", "food_cost",
            "margin_pct", "monthly_units_sold", "monthly_profit"]]
        .rename(columns={
            "item_name": "Item", "category": "Category",
            "current_price": "Price (£)", "food_cost": "Food Cost (£)",
            "margin_pct": "Margin %", "monthly_units_sold": "Units/Month",
            "monthly_profit": "Monthly Profit (£)"
        }),
        use_container_width=True
    )

st.markdown("""
<p style="font-size:0.8rem; color:#7A7060; font-family:'DM Sans',sans-serif; 
   border-left: 3px solid #B5703A; padding-left: 0.8rem; margin-bottom: 1rem;">
   <strong>Food cost</strong> should reflect ingredients only — not labour or overheads. 
   If you are unsure, use your best estimate. The more accurate your figures, 
   the more reliable your recommendations will be.
</p>
""", unsafe_allow_html=True)

# Step 2: Menu Analysis ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="step-header">Step 2 — Menu Engineering Analysis</div>', unsafe_allow_html=True)

if "df" not in st.session_state:
    st.warning("Please complete Step 1 first.")
else:
    if st.button("Analyse Menu"):
        df = st.session_state["df"]

        median_margin = df["margin_pct"].median()
        median_units  = df["monthly_units_sold"].median()
        
        st.write(f"Thresholds — Margin: {median_margin:.2f}, Units: {median_units:.0f}")

        def classify(row):
            hm = row["margin_pct"]         >= median_margin
            hs = row["monthly_units_sold"] >= median_units
            if hm and hs:     return "Signature"
            if hm and not hs: return "Speciality"
            if not hm and hs: return "Staple"
            return "Marginal"

        df["classification"] = df.apply(classify, axis=1)
        st.session_state["df"] = df

    if "classification" in st.session_state["df"].columns:
        df = st.session_state["df"]

        # ── Classification Count Metrics ──────────────────────────────────
        counts = df["classification"].value_counts()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Signature",  counts.get("Signature",  0), help="High margin, high volume — your best performers")
        col2.metric("Speciality", counts.get("Speciality", 0), help="High margin, low volume — hidden potential")
        col3.metric("Staple",     counts.get("Staple",     0), help="Low margin, high volume — pricing opportunity")
        col4.metric("Marginal",   counts.get("Marginal",   0), help="Low margin, low volume — candidates for removal")

        # ── Color Map ─────────────────────────────────────────────────────
        color_map = {
            "Signature":  "#2D6A4F",
            "Speciality": "#22314C",
            "Staple":     "#C47B2B",
            "Marginal":   "#9B3A3A"
        }

        # ── Scatter Plot Matrix ───────────────────────────────────────────
        fig = px.scatter(
            df,
            x="monthly_units_sold",
            y="margin_pct",
            color="classification",
            color_discrete_map=color_map,
            text="item_name",
            size="monthly_profit",
            title="Menu Performance Matrix",
            labels={
                "monthly_units_sold": "Monthly Units Sold  (Popularity →)",
                "margin_pct":         "Gross Margin %  (Profitability ↑)",
                "classification":     "Classification"
            },
            template="plotly_white"
        )

        median_margin = df["margin_pct"].median()
        median_units  = df["monthly_units_sold"].median()

        fig.add_hline(
            y=median_margin,
            line_dash="dash",
            line_color="#AAAAAA",
            opacity=0.6,
            annotation_text="Median Margin",
            annotation_position="right"
        )
        fig.add_vline(
            x=median_units,
            line_dash="dash",
            line_color="#AAAAAA",
            opacity=0.6,
            annotation_text="Median Volume",
            annotation_position="top"
        )

        # Quadrant labels
        x_max = df["monthly_units_sold"].max() * 1.1
        y_max = df["margin_pct"].max() * 1.05
        x_min = df["monthly_units_sold"].min() * 0.9
        y_min = df["margin_pct"].min() * 0.95

        quadrant_labels = [
            dict(x=(x_min + median_units) / 2,  y=y_max * 0.97, text="SPECIALITY",  color="#3498DB"),
            dict(x=(median_units + x_max) / 2,  y=y_max * 0.97, text="SIGNATURE",   color="#2ECC71"),
            dict(x=(x_min + median_units) / 2,  y=y_min * 1.05, text="MARGINAL",    color="#E74C3C"),
            dict(x=(median_units + x_max) / 2,  y=y_min * 1.05, text="STAPLE",      color="#F39C12"),
        ]

        for ql in quadrant_labels:
            fig.add_annotation(
                x=ql["x"], y=ql["y"],
                text=ql["text"],
                showarrow=False,
                font=dict(size=11, color=ql["color"], family="Georgia, serif"),
                opacity=0.4
            )

        fig.update_traces(
            textposition="top center",
            marker=dict(opacity=0.85, line=dict(width=1, color="white")),
            textfont=dict(size=10)
        )
        fig.update_layout(
            height=520,
            legend_title="Classification",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(family="Georgia, serif"),
            plot_bgcolor="#FAFAF8",
            paper_bgcolor="#FAFAF8",
            title=dict(font=dict(size=16, family="Georgia, serif"))
        )

        st.plotly_chart(fig, use_container_width=True)

        # ── Classification Guide ──────────────────────────────────────────
        with st.expander("Classification Guide"):
            st.markdown("""
| Classification | Definition | Recommended Action |
|---|---|---|
| **Signature** | High margin + High volume | Protect price, feature prominently on menu |
| **Speciality** | High margin + Low volume | Reposition, improve description, consider promotion |
| **Staple** | Low margin + High volume | Review pricing, consider portion or cost adjustment |
| **Marginal** | Low margin + Low volume | Evaluate for removal or full rework |

*Based on Menu Engineering methodology — Kasavana & Smith (1982)*
            """)

        # ── Classification Table ──────────────────────────────────────────
        st.markdown("### Item Classifications")
        st.dataframe(
            df[["item_name", "category", "current_price",
                "margin_pct", "monthly_units_sold", "classification"]]
            .sort_values("classification")
            .rename(columns={
                "item_name":           "Item",
                "category":            "Category",
                "current_price":       "Price (£)",
                "margin_pct":          "Margin %",
                "monthly_units_sold":  "Units / Month",
                "classification":      "Classification"
            })
            .style.applymap(
                lambda v: f"color: {color_map.get(v, 'black')}; font-weight: bold"
                if v in color_map else "",
                subset=["Classification"]
            ),
            use_container_width=True,
            hide_index=True
        )

# Step 3: AI Pricing Recommendation
st.markdown("---")
st.markdown('<div class="step-header">Step 3 — AI Pricing Recommendations</div>', unsafe_allow_html=True)

if "df" not in st.session_state or "classification" not in st.session_state["df"].columns:
    st.warning("Please complete Step 2 first.")
else:
    with st.expander("Add context for better recommendations (optional)"):
        season = st.selectbox(
            "Current season / trading period",
            ["No preference", "Spring", "Summer", "Autumn", "Winter",
             "Christmas & New Year", "Valentine's Day", "Easter"]
        )
        cuisine_type = st.text_input(
            "Cuisine type",
            placeholder="e.g. Greek, Italian, Modern British",
        )
        avg_spend = st.number_input(
            "Average spend per head (£)",
            min_value=0.0, step=1.0, value=0.0,
            help="Leave at 0 if unknown"
        )
        competitors = st.text_input(
            "Local competition notes",
            placeholder="e.g. Two other Greek restaurants nearby, both charge £15-18 for mains",
        )
        other_context = st.text_area(
            "Anything else we should know?",
            placeholder="e.g. Planning a summer terrace menu, high wastage on fish dishes",
            height=80
        )

    if st.button("Generate Recommendations"):
        df = st.session_state["df"]
        restaurant = st.session_state.get("restaurant_name", "the restaurant")
        context_block = f"""
Additional context:
- Season / trading period: {season if season != 'No preference' else 'Not specified'}
- Cuisine type: {cuisine_type or 'Not specified'}
- Average spend per head: {'£' + str(int(avg_spend)) if avg_spend > 0 else 'Not specified'}
- Local competition: {competitors or 'Not specified'}
- Other notes: {other_context or 'None'}
"""
        menu_summary = df[["item_name", "category", "current_price",
                            "food_cost", "margin_pct",
                            "monthly_units_sold", "classification"]
                         ].to_string(index=False)

        with st.spinner("Analysing with MenuMind..."):
            messages = [
                SystemMessage(content=f"""You are an expert restaurant consultant 
specialising in menu engineering and pricing strategy for {restaurant}.

{context_block}

Use the above context to make recommendations seasonally and locally relevant.
Tailor every recommendation to this specific restaurant's situation.

Analyse the menu data and return ONLY a valid JSON array.
Each object must have exactly these fields:
{{
    "item_name": "<exact name from data>",
    "classification": "<classification from data>",
    "current_price": <number>,
    "recommended_price": <number>,
    "action": "<one of: Promote / Reprice / Reposition / Remove / Keep>",
    "reasoning": "<2 sentence plain English explanation>",
    "projected_monthly_impact": "<realistic range accounting for potential volume loss e.g. +GBP80 to +GBP160/month if volume holds, lower if price sensitive>"
}}

Rules:
"- Signature: keep price, action = Promote"
"- Speciality: reduce price slightly or reposition, action = Reposition"
"- Staple: increase price 10-20%, action = Reprice"
"- Marginal: recommend removal, action = Remove"
- Ideal food cost % is 28-35% of selling price
- Be specific with numbers in reasoning
- For any price increase, consider price sensitivity. If the item is a high-volume staple 
  or everyday dish, customers are likely price sensitive — flag this risk explicitly in reasoning.
- projected_monthly_impact must account for potential volume loss. Give a realistic range 
  e.g. "+£80 to +£160/month depending on volume retention" rather than assuming flat volume.
- If a price increase risks significant volume loss that could make the change net negative, 
  say so clearly and suggest a smaller incremental increase instead.

Return ONLY the JSON array. No markdown, no code fences, no explanation."""),
                HumanMessage(content=f"Analyse this menu:\n\n{menu_summary}")
            ]

            try:
                response = llm.invoke(messages).content.strip()
                response = re.sub(r"^```(?:json)?", "", response).strip()
                response = re.sub(r"```$", "", response).strip()
                recommendations = json.loads(response)
                st.session_state["recommendations"] = recommendations
                st.success("Recommendations generated!")
            except Exception as e:
                st.error(f"Failed to parse AI response: {e}")

    if "recommendations" in st.session_state:
        recommendations = st.session_state["recommendations"]

        action_colors = {
            "Promote":    "#2ECC71",
            "Reprice":    "#F39C12",
            "Reposition": "#3498DB",
            "Remove":     "#E74C3C",
            "Keep":       "#95A5A6"
        }

        for rec in recommendations:
            action = rec.get("action", "Keep")
            color  = action_colors.get(action, "#95A5A6")
            curr   = rec.get("current_price", 0)
            recp   = rec.get("recommended_price", 0)
            price_change = f"£{curr:.2f} → £{recp:.2f}" if curr != recp else f"£{curr:.2f} (no change)"

            with st.container():
                st.markdown(f"""
<div style="border-left: 4px solid {color}; padding: 0.6rem 1rem; 
            margin-bottom: 0.8rem; background: white; border-radius: 0 8px 8px 0;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06);">
    <strong>{rec.get('item_name', '')}</strong> &nbsp;
    <span style="background:{color}; color:white; padding:2px 8px; 
                 border-radius:4px; font-size:0.8rem;">{action}</span>
    &nbsp; <span style="color:#666; font-size:0.85rem;">{rec.get('classification','')}</span><br/>
    <span style="font-size:0.9rem;"> {price_change} &nbsp;|&nbsp; 
    {rec.get('projected_monthly_impact','N/A')}</span><br/>
    <span style="color:#555; font-size:0.85rem;">{rec.get('reasoning','')}</span>
</div>
""", unsafe_allow_html=True)
                
# Step 4: Generate a Report ──────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="step-header">Step 4 — Download Full Report</div>', unsafe_allow_html=True)

if "recommendations" not in st.session_state:
    st.warning("Please complete Step 3 first.")
else:
    if st.button("Download Report Here"):
        df = st.session_state["df"]
        recommendations = st.session_state["recommendations"]

        restaurant = st.session_state.get("restaurant_name", "this restaurant")

        with st.spinner("Generating your report..."):
            summary_messages = [
                SystemMessage(content=f"""You are a senior restaurant business consultant.
Write a concise 3-4 sentence executive summary of this menu analysis for {restaurant}.
Then write exactly 3 priority actions {restaurant} should take this week.
Be specific with numbers. Plain English. No jargon. No bullet symbols.
Use the terms Signature, Speciality, Staple and Marginal when referring to menu classifications."""),
                HumanMessage(content=f"""
Restaurant name: {restaurant}
Menu classifications: {df['classification'].value_counts().to_dict()}
Total monthly revenue: £{df['monthly_revenue'].sum():.2f}
Total monthly profit: £{df['monthly_profit'].sum():.2f}
Average margin: {df['margin_pct'].mean():.1f}%
Number of Marginal items: {len(df[df['classification'] == 'Marginal'])}
Number of Signature items: {len(df[df['classification'] == 'Signature'])}
Number of Speciality items: {len(df[df['classification'] == 'Speciality'])}
Number of Staple items: {len(df[df['classification'] == 'Staple'])}
Recommendations summary: {json.dumps(recommendations[:5])}

Write the executive summary and top 3 priority actions for {restaurant}.""")
            ]

            try:
                summary = llm.invoke(summary_messages).content.strip()
                st.session_state["summary"] = summary

                pdf_data = generate_pdf(df, recommendations, summary)
                st.session_state["pdf"] = pdf_data
                st.success("Report ready!")

            except Exception as e:
                st.error(f"Failed to generate report: {e}")

    if "pdf" in st.session_state:

        # Executive summary preview
        if "summary" in st.session_state:
            st.markdown("### Executive Summary")
            st.info(st.session_state["summary"])

        # Classification breakdown preview
        if "df" in st.session_state:
            df = st.session_state["df"]
            st.markdown("### Classification Breakdown")
            col1, col2, col3, col4 = st.columns(4)
            counts = df["classification"].value_counts()
            col1.metric("Signature",  counts.get("Signature",  0))
            col2.metric("Speciality", counts.get("Speciality", 0))
            col3.metric("Staple",     counts.get("Staple",     0))
            col4.metric("Marginal",   counts.get("Marginal",   0))

        # Download button
        st.download_button(
            label="Download Menu Optimisation Report (PDF)",
            data=st.session_state["pdf"],
            file_name="menu_optimisation_report.pdf",
            mime="application/pdf"
        )

