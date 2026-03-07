# MenuMind
An AI-powered restaurant menu optimisation tool for independent restaurants, built with Streamlit and GPT-4o.

## Setup
1. Clone the repo
2. Install dependencies:
pip install -r requirements.txt
3. Add your OpenAI API key to Streamlit secrets (`.streamlit/secrets.toml`):
OPENAI_API_KEY=sk-your-key-here
4. Run the app:
streamlit run app.py

## Usage
1. Enter your restaurant name to get started
2. Enter your menu data manually or upload a CSV/Excel file
3. Run the menu engineering analysis to classify your items
4. Generate AI pricing recommendations with optional context
5. Download your personalised PDF report

## Sample Data
A sample menu CSV (`sample_menu.csv`) is included in the repo to demo the full pipeline.

## CSV Upload Format
If uploading your own data, use these column headers:

| Column | Description |
|---|---|
| Item Name | Name of the dish |
| Category | e.g. Starters, Mains, Desserts |
| Selling Price | What you charge the customer (£) |
| Food Cost | Ingredient cost per dish (£) |
| Monthly Sales | Typical units sold per month |

## Tech Stack
- Streamlit
- GPT-4o via LangChain
- Pandas & Plotly
- fpdf2

## Module
MSIN0231 Machine Learning for Business — Group Coursework
