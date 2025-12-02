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
    composite_pti_bands_chart,
    affordability_stack_chart,
    metro_pti_lines,
    pti_ladder_bar,
    rating_heatmap,
    composite_rent_to_income,
    metro_rent_to_income,
    top_rent_burden,
    yoy_pti_change,
    composite_dom_inventory,
    composite_sale_to_list,
    metro_snapshot_bar,
)

with st.sidebar:
    st.title("🏠 Project Navigation")

    st.markdown("### 📑 Jump To")
   

st.set_page_config(
    page_title="Housing Affordability Story - HouseTS",
    layout="wide",
)

st.title("Housing Affordability Explorer (HouseTS)")

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
    "3. Rent Burden vs Ownership Burden",
    "4. Affordability Bands (Demographia)",
    "5. 2023 Metro Snapshot",
])

# ----- CHAPTER 1 -----
with tab1:
    st.subheader("1. Prices vs Incomes (Macro Trend)")

    st.markdown(
        """
        Home prices and household incomes do not move together.  
        This chapter compares both series indexed to **2012 = 100**.

        ### What to notice
        - If home prices and incomes grew at the same rate, the lines would stay close.
        - Instead, **home prices outpaced incomes throughout the last decade.**
        - This widening gap sets the foundation for today’s affordability pressures.

        The macro trend answers the first big question:  
        **Is the U.S. housing affordability problem structural?**  
        The answer is yes—prices have consistently pulled away from incomes.
        """
    )

    st.plotly_chart(composite_price_income_index_chart(comp), use_container_width=True)



# ----- CHAPTER 2 -----
with tab2:
    st.subheader("2. Metro Affordability Divergence")

    st.markdown(
        """
        Even though national averages show prices growing faster than incomes,
        the **severity varies dramatically across metros**.

        This chapter ranks metros by **Price-to-Income ratio (PTI)** and
        traces their affordability trajectories over time.

        ### Why PTI matters
        PTI is a simple measure:
        **PTI = Median Home Price / Per Capita Income**

        - Higher PTI → **less affordable** (homes cost many multiples of income)
        - Lower PTI → **more attainable**

        ### What to explore
        - How metro rankings change depending on the chosen focus year  
        - Which metros have become “outliers” (extreme PTI)  
        - Whether affordable metros stayed affordable or caught up to expensive ones

        The story:  
        **Housing affordability is not evenly distributed—metros are splitting into different trajectories.**
        """
    )

    rank_year = st.slider(
        "Choose a year to rank metros by PTI:",
        int(summary["year"].min()),
        int(summary["year"].max()),
        latest_year(summary),
        key="rank_year_metros",
    )

    st.plotly_chart(metro_pti_lines(df, focus_year=rank_year), use_container_width=True)

    # --- compute top/bottom 7 metros for that year using `summary` ---
    summary_year = (
        summary[summary["year"] == rank_year]
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

    # --- list them under the chart ---
    st.markdown("### Metros Highlighted")
    st.markdown(f"**Top 7 (Least Affordable):** {', '.join(top7)}")
    st.markdown(f"**Bottom 7 (Most Affordable):** {', '.join(bottom7)}")

# ----- CHAPTER 3 -----
with tab3:
    st.subheader("3. Rent Burden vs Ownership Burden")

    st.markdown(
        """
        The affordability crisis looks very different depending on whether
        a household is **renting** or **buying**.

        ### Key insight
        - **PTI (ownership burden)** has risen sharply.
        - **Rent-to-Income ratio** has stayed **much flatter** by comparison.

        This contrast suggests:
        - The **cost of buying** has become disproportionately harder.
        - Renting has remained relatively stable for many households.
        - The affordability crisis is **more intense for would-be buyers** than for current renters.

        This chapter helps us understand why homeownership feels increasingly out of reach,
        even if renting seems manageable on paper.
        """
    )

    st.plotly_chart(
        composite_rent_to_income(summary),
        use_container_width=True,
    )

# ----- CHAPTER 4 -----
with tab4:
    st.subheader("4. Affordability Bands (Demographia)")

    st.markdown(
        """
        PTI ratios become even more meaningful when grouped into
        **Demographia-style affordability categories**.

        These bands summarize **how difficult it is to buy a median home** in each metro.

        ### PTI Affordability Categories
        - **Affordable**: PTI ≤ 3.0  
        - **Moderately Unaffordable**: PTI 3.1–4.0  
        - **Seriously Unaffordable**: PTI 4.1–5.0  
        - **Severely Unaffordable**: PTI 5.1-8.9  
        - **Impossibly Unaffordable**: PTI > 9.0 (extended category)

        ### Why this matters
        - Bands show **not just trends**, but **distribution shifts**.
        - More metros are moving into the **higher PTI categories**.
        - This reveals a **structural drift toward unaffordability**, not just short-term volatility.

        In short:  
        **Many metros have crossed from difficult… to severe… to nearly impossible for median-income households.**
        """
    )

    year_focus = latest_year(summary)

    st.plotly_chart(
        composite_pti_bands_chart(comp),
        use_container_width=True,
    )
    
    st.markdown(
        "*Affordability levels were provided by the Center for Demographics and Policy ([Demographia International Housing Affordability, 2025 Edition](https://www.chapman.edu/communication/_files/Demographia-International-Housing-Affordability-2025-Edition.pdf)).*"
        )

# ----- CHAPTER 5 -----
with tab5:
    st.subheader("5. 2023 Metro Snapshot")

    st.markdown(
        """
        This final chapter provides a **recent snapshot** of affordability conditions.

        ### What you can see here

        - PTI levels for all metros in the most recent year  
        - Which metros are currently the **least affordable**  
        - Which metros remain relatively **more attainable**  
        - How these map into our affordability bands
        """
    )

    fig = metro_snapshot_bar(summary)

    st.plotly_chart(fig, use_container_width=True)
