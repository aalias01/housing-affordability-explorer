# app.py
import streamlit as st

from data_utils import (
    load_raw_data,
    add_derived_columns,
    composite_series,
    yearly_metro_summary,
    affordability_counts_by_year,
    latest_year,
    AFFORDABILITY_ORDER,
    AFFORDABILITY_COLORS,
)
from charts import (
    composite_price_income_index_chart,
    #composite_pti_bands_chart,
    metro_pti_lines,
    composite_rent_to_income,
    metro_snapshot_bar,
    affordability_bands_with_us_ratio,
)

# ----- GLOBAL STYLE FIXES -----
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.2rem !important;
    }
    h1 {
        margin-top: 0rem !important;
        margin-bottom: 0.0rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# with st.sidebar:
#     st.title("🏠 Project Navigation")

#     st.markdown("### 📑 Jump To")
   

st.set_page_config(
    page_title="Housing Affordability Story",
    layout="wide",
)

st.title("Housing Affordability Explorer - Overview")

st.markdown(
    """
    ### Why this matters

    Since the early 2010s, **home prices in many U.S. metros have grown much faster
    than incomes**. This app explores:

    - How **home prices vs incomes** have moved over time (composite U.S. series)
    - How **Price-to-Income (PTI)** varies across metros and diverges over time
    - Why **owning** a home has become less affordable even while **rent burden** looks more stable

    Use the tabs below to move through the story, or jump straight to a specific chapter.
    """
)


# ---- load & prep data ----
raw = load_raw_data()
df = add_derived_columns(raw)
comp = composite_series(df)
summary = yearly_metro_summary(df)
counts = affordability_counts_by_year(summary)
year_latest = latest_year(summary)

# ---- tabs / chapters ----
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Prices vs Incomes (Macro Trend)",
    "2. Metro Affordability Divergence",
    "3. Affordability Bands",
    "4. Rent Burden vs Ownership Burden",
    "5. 2023 Metro Snapshot",
])
        
with tab1:
    st.subheader("1. Prices vs Incomes (Macro Trend)")

    st.markdown(
        """
        Home prices and household incomes do not move together. This chapter compares both series indexed to **2012 = 100**.

        The macro trend answers the first big question: **Is the U.S. housing affordability problem structural?**  
        The answer is: Yes, prices have consistently pulled away from incomes.
        """
    )

    
    with st.container(border=True):
        st.plotly_chart(
            composite_price_income_index_chart(comp),
            use_container_width=True,
        )
    
    with st.container(border=True):

        st.markdown(
            """
            ### What We notice
            - If home prices and incomes grew at the same rate, the lines would stay close.  
            - **Home prices outpaced incomes throughout the last decade.**  
            - This widening gap sets the foundation for today’s affordability pressures.
            """
        )

with tab2:
    
    col_left, col_right = st.columns([2.3, 1])   # wider left column, narrower right

    with col_left:
        st.subheader("2. Metro Affordability Divergence")
        st.markdown(
            """
            Even though national averages show prices growing faster than incomes,
            the **severity varies dramatically across metros**.

            This chapter ranks metros by **Price-to-Income ratio (PTI)** and
            traces their affordability trajectories over time.
            """
        )

    with col_right:
        with st.container(border=True):
            st.markdown("#### What is PTI?")
            st.markdown(
                """
                PTI is a simple measure:  
                **PTI = Median Home Price / Median Household Income**

                - Higher PTI → **less affordable**  
                - Lower PTI → **more attainable**
                """
            )

        focus_year = 2023

    # Chart in a bordered container
    with st.container(border=True):
        st.plotly_chart(
            metro_pti_lines(df, focus_year=focus_year),
            use_container_width=True,
        )

    # --- compute top/bottom 7 metros for that year using `summary` ---
    summary_year = (
        summary[summary["year"] == focus_year]
        .dropna(subset=["price_to_income"])
    )

    top7 = (
        summary_year.sort_values("price_to_income", ascending=False)
        .head(7)["city_full"]
        .tolist()
    )

    bottom7 = (
        summary_year.sort_values("price_to_income", ascending=True)
        .head(7)["city_full"]
        .tolist()
    )

    # --- list in a card-style container ---
    with st.container(border=True):
        st.markdown(
            """
            ### What We Notice
            - Which metros have become “outliers” (extreme PTI)  
            - Whether affordable metros stayed affordable or caught up to expensive ones

            The story:  
            **Housing affordability is not evenly distributed—metros are splitting into different trajectories.**
            """
        )
        st.markdown(f"### Metros Highlighted in {focus_year}")
        st.markdown(f"**Top 7 (Least Affordable – highest PTI):** {', '.join(top7)}")
        st.markdown(f"**Bottom 7 (Most Affordable – lowest PTI):** {', '.join(bottom7)}")

# ----- CHAPTER 3 -----
with tab3:
    st.subheader("3. Affordability Bands")

    st.markdown(
        """
        PTI ratios become even more meaningful when grouped into **affordability categories**.  

        ### PTI Affordability Categories
        - **Affordable**: PTI ≤ 3.0  
        - **Moderately Unaffordable**: PTI 3.1–4.0  
        - **Seriously Unaffordable**: PTI 4.1–5.0  
        - **Severely Unaffordable**: PTI 5.1-8.9  
        - **Impossibly Unaffordable**: PTI ≥ 9.0
        """
    )

    year_focus = latest_year(summary)
    
    with st.container(border=True):
        st.plotly_chart(
        affordability_bands_with_us_ratio(counts, comp),
        use_container_width=True,
        )

    with st.container(border=True):
        st.markdown(
            """
        ### What We Notice
        - Each year, fewer metros remain in the Affordable category, while more are moving into higher PTI ranges.
        - This indicates a structural and widespread drift toward unaffordability, rather than short-term volatility or isolated market spikes.

        In short:  
        A decade ago, many metros were still reasonably affordable for median-income households.
        Today, a growing share has moved into seriously, severely, or even impossibly unaffordable territory.
        """
        )

# ----- CHAPTER 4 -----
with tab4:
    st.subheader("4. Rent Burden vs Ownership Burden")

    st.markdown(
        """
        The affordability crisis looks very different depending on whether
        a household is **renting** or **buying**.
        """
    )

    with st.container(border=True):
        st.plotly_chart(
            composite_rent_to_income(summary),
            use_container_width=True,
        )
        
    with st.container(border=True):
        st.markdown(
            """
            ### Key insight
            Earlier chapters showed that home prices have pulled far ahead of incomes, pushing ownership burden sharply upward.  
            This chart adds another dimension: rent burden hasn’t moved much at all.

            Together, these trends reveal that:
            - The affordability crisis is not uniform.
            - For renters, costs have grown slowly and predictably relative to income.
            - For buyers, costs have surged far faster than incomes can keep up with.

            Bottom Line:
            Renting still looks affordable in the data, but the leap to homeownership is becoming increasingly unattainable.
            """
        )

# ----- CHAPTER 5 -----
with tab5:
    st.subheader("5. 2023 Metro Snapshot")

    st.markdown(
        """
        This final chapter provides a **recent snapshot** of affordability conditions.
        """
    )

    fig = metro_snapshot_bar(summary)

    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)

    with st.container(border=True):
        st.markdown(
        """
        ### What you can see here

        - PTI levels for all metros in the most recent year  
        - Which metros are currently the **least affordable**  
        - Which metros remain relatively **more attainable**  
        - How these map into our affordability bands
        """
        )