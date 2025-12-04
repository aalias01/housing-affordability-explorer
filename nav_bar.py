import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="wide")

st.markdown("""
<style>

html, body {
    margin: 0 !important;
    padding: 0 !important;
}

.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}

/* Optional: remove top padding of main content */
main .block-container {
    padding-top: 0rem !important;
}

</style>
""", unsafe_allow_html=True)


def navbar(active: str):
    css = """
    <style>

    .topnav {
        display: flex;
        justify-content: center;
        gap: 22px;
        padding: 12px 0;
        background: #ffffffcc;
        backdrop-filter: blur(6px);
        border-bottom: 1px solid #e5e5e5;
        position: sticky;
        top: 0;
        z-index: 999;
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI",
                     Roboto, Helvetica, Arial, sans-serif !important;
    }

    .nav-item {
        padding: 8px 16px;
        border-radius: 10px;
        font-weight: 500;
        font-size: 15px;
        text-decoration: none;
        color: #333;
        background: #f7f7f7;
        border: 1px solid #dcdcdc;
        transition: 0.18s;
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI",
                     Roboto, Helvetica, Arial, sans-serif !important;
    }

    .nav-item:hover {
        background: #e9f2ff;
        border-color: #4a90e2;
        color: #1a73e8;
    }

    .nav-item.active {
        background: #dce8ff;
        border-color: #4a90e2;
        color: #1a73e8;
        font-weight: 600;
        box-shadow: 0 0 4px rgba(74,144,226,0.4);
    }

    </style>
    """

    tabs = [
        ("Intro", "🏡 Intro"),
        ("Map", "🗺️ Interactive Map Explorer"),
        ("TimeSeries", "📊 Time Series Comparison"),
        ("PriceFinder", "💰 Price Affordability Finder"),
        ("Story", "📖 Housing Affordability Story"),
    ]

    html_items = ""
    for key, label in tabs:
        cls = "nav-item active" if key == active else "nav-item"
        html_items += f'<a class="{cls}" href="?page={key}">{label}</a>'

    html(css + f'<div class="topnav">{html_items}</div>', height=70)



# ------------------------------------------
# GET CURRENT PAGE (NEW API)
# ------------------------------------------

# st.query_params is a dict-like object
qp = st.query_params
current_page = qp.get("page", "Intro")

# Draw navbar
navbar(current_page)


# ------------------------------------------
# PAGE ROUTING
# ------------------------------------------

if current_page == "Intro":
    st.title("🏡 Intro Page")
    st.write("Your intro section here.")

elif current_page == "Map":
    st.title("🗺️ Interactive Map Explorer")
    st.write("Map code here.")

elif current_page == "TimeSeries":
    st.title("📊 Time Series Comparison")
    st.write("Your time series charts go here.")

elif current_page == "PriceFinder":
    st.title("💰 Price Affordability Finder")
    st.write("Income → affordable zip map, etc.")

elif current_page == "Story":
    st.title("📖 Housing Affordability Story")
    st.write("Story / narrative content.")
