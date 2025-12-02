# charts.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_utils import AFFORDABILITY_COLORS, AFFORDABILITY_ORDER


# ---------- CHAPTER 1: MACRO TREND ----------

def composite_price_income_index_chart(comp: pd.DataFrame) -> go.Figure:
    """Composite price vs income, indexed to 2012 = 100."""
    long = comp.melt(
        id_vars="date",
        value_vars=["price_index", "income_index"],
        var_name="Series",
        value_name="Index (2012=100)",
    )
    fig = px.line(
        long,
        x="date",
        y="Index (2012=100)",
        color="Series",
        title="Composite Price vs Income (Indexed to 2012 = 100)",
    )
    fig.update_layout(legend_title_text="")
    return fig


def affordability_stack_chart(counts: pd.DataFrame) -> go.Figure:
    fig = px.area(
        counts,
        x="year",
        y="n_metros",
        color="affordability_rating",
        category_orders={"affordability_rating": AFFORDABILITY_ORDER},
        color_discrete_map=AFFORDABILITY_COLORS,
        labels={"n_metros": "# of Metros", "year": "Year"},
        title="Number of Metros by Affordability Category",
    )
    fig.update_layout(legend_title_text="Affordability Rating")
    return fig


# ---------- CHAPTER 2: METRO DIVERGENCE ----------

def metro_pti_lines(df: pd.DataFrame, focus_year: int) -> go.Figure:
    """
    Plot metro-level PTI trends over time, with the top/bottom 7 metros
    (by PTI in the focus_year) highlighted.

    df can be ZIP-level; we aggregate to metro-by-date first.
    """

    # 1) Aggregate ZIPs → metro-level series
    df_metro = (
        df.groupby(["city_full", "year", "date"], as_index=False)["price_to_income"]
        .mean()
        .dropna(subset=["price_to_income"])
    )

    # 2) Compute snapshot for the focus year (metro-level PTI)
    snapshot = (
        df_metro[df_metro["year"] == focus_year]
        .groupby("city_full", as_index=False)["price_to_income"]
        .mean()
        .dropna(subset=["price_to_income"])
    )

    top = snapshot.sort_values("price_to_income", ascending=False).head(7)["city_full"]
    bottom = snapshot.sort_values("price_to_income", ascending=True).head(7)["city_full"]

    def label_group(city: str) -> str:
        if city in top.values:
            return "Top 7 (Least Affordable)"
        if city in bottom.values:
            return "Bottom 7 (Most Affordable)"
        return "Other"

    df_plot = df_metro.copy()
    df_plot["group"] = df_plot["city_full"].apply(label_group)

    color_map = {
        "Top 7 (Least Affordable)": "#B71C1C",
        "Bottom 7 (Most Affordable)": "#1E88E5",
        "Other": "#B0BEC5",
    }

    fig = px.line(
        df_plot,
        x="date",
        y="price_to_income",
        line_group="city_full",
        color="group",
        color_discrete_map=color_map,
        labels={"price_to_income": "PTI", "date": "Date"},
        title=f"Metro Price-to-Income Trends (Top/Bottom 7 Highlighted for {focus_year})",
        hover_name="city_full",
    )
    fig.update_layout(legend_title_text="")

    return fig

def pti_ladder_bar(summary: pd.DataFrame, year_focus: int) -> go.Figure:
    sub = summary[summary["year"] == year_focus].dropna(subset=["price_to_income"])
    sub = sub.sort_values("price_to_income", ascending=True)

    fig = px.bar(
        sub,
        x="price_to_income",
        y="city_full",
        orientation="h",
        color="affordability_rating",
        color_discrete_map=AFFORDABILITY_COLORS,
        category_orders={"affordability_rating": AFFORDABILITY_ORDER},
        labels={"price_to_income": "PTI", "city_full": "Metro"},
        title=f"Affordability Ladder by Metro in {year_focus} (Lower PTI = More Affordable)",
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


def rating_heatmap(summary: pd.DataFrame) -> go.Figure:
    code_map = {name: i for i, name in enumerate(AFFORDABILITY_ORDER, start=1)}
    tmp = summary.copy()
    tmp["rating_code"] = tmp["affordability_rating"].map(code_map)

    pivot = tmp.pivot(index="city_full", columns="year", values="rating_code")

    colors = [AFFORDABILITY_COLORS[r] for r in AFFORDABILITY_ORDER]
    n = len(colors)
    scale = [(i / (n - 1), c) for i, c in enumerate(colors)]

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=scale,
        origin="lower",
        title="Metro Affordability Rating Over Time (Demographia Categories)",
    )

    fig.update_coloraxes(
        colorbar=dict(
            tickmode="array",
            tickvals=list(range(1, n + 1)),
            ticktext=AFFORDABILITY_ORDER,
            title="Rating",
        )
    )
    return fig


# ---------- CHAPTER 3: RENT BURDEN ----------

def composite_rent_to_income(summary: pd.DataFrame) -> go.Figure:
    comp = (
        summary.groupby("year", as_index=False)["rent_to_income"]
        .mean()
        .rename(columns={"rent_to_income": "composite_rti"})
    )

    fig = px.line(
        comp,
        x="year",
        y="composite_rti",
        markers=True,
        labels={"composite_rti": "Rent-to-Income"},
        title="Composite Rent-to-Income Ratio (Average Across Metros)",
    )

    max_rti = float(comp["composite_rti"].max())
    fig.update_yaxes(range=[0, max_rti * 1.1])  # little headroom above max

    return fig



def metro_rent_to_income(df: pd.DataFrame, metro: str) -> go.Figure:
    sub = df[df["city_full"] == metro].copy()
    fig = px.line(
        sub,
        x="date",
        y="rent_to_income",
        markers=True,
        labels={"rent_to_income": "Rent-to-Income", "date": "Date"},
        title=f"Rent-to-Income Over Time – {metro}",
    )
    return fig


def top_rent_burden(summary: pd.DataFrame, year_focus: int, n: int = 10) -> go.Figure:
    sub = summary[summary["year"] == year_focus].dropna(subset=["rent_to_income"])
    sub = sub.sort_values("rent_to_income", ascending=False).head(n)

    fig = px.bar(
        sub,
        x="rent_to_income",
        y="city_full",
        orientation="h",
        labels={"rent_to_income": "Rent-to-Income", "city_full": "Metro"},
        title=f"Highest Rental Burden Metros in {year_focus}",
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


# ---------- CHAPTER 4: Affordability Bands ----------

def composite_pti_bands_chart(comp: pd.DataFrame) -> go.Figure:
    """
    Composite PTI with Demographia-colored bands in the background.
    Light-theme only: labels/lines in black.
    """
    fig = go.Figure()

    text_color = "black"
    line_color = "black"

    # 1. COLORED ZONES (background)
    zones = [
        (0.0, 3.0,  "Affordable (≤3.0)",                  "#66BB6A"),
        (3.0, 4.0,  "Moderately Unaffordable (3.1–4.0)",  "#FBC02D"),
        (4.0, 5.0,  "Seriously Unaffordable (4.1–5.0)",   "#FF9800"),
        (5.0, 8.9,  "Severely Unaffordable (5.1–8.9)",    "#FF7043"),
        (8.9, 20.0, "Impossibly Unaffordable (≥9.0)",     "#D32F2F"),
    ]

    for (y0, y1, _label, color) in zones:
        fig.add_shape(
            type="rect",
            xref="paper", x0=0, x1=1,
            yref="y", y0=y0, y1=y1,
            fillcolor=color,
            opacity=0.30,
            layer="below",
            line_width=0,
        )

    # 2. THRESHOLD LINES
    for t in [3.0, 4.0, 5.0, 8.9, 9.0]:
        fig.add_hline(
            y=t,
            line_dash="dash",
            line_color=line_color,
            opacity=0.8,
            layer="above",
        )

    # 3. LABELS ON RIGHT
    label_positions = [
        (2.0,  "≤3.0: Affordable"),
        (3.5,  "3.1–4.0: Moderately Unaffordable"),
        (4.5,  "4.1–5.0: Seriously Unaffordable"),
        (6.8,  "5.1–8.9: Severely Unaffordable"),
        (9.8,  "≥9.0: Impossibly Unaffordable"),
    ]

    for y, text in label_positions:
        fig.add_annotation(
            xref="paper", x=0.98,
            y=y,
            text=text,
            showarrow=False,
            font=dict(size=12, color=text_color),
            xanchor="right",
            yanchor="middle",
        )

    # 4. PTI LINE
    fig.add_trace(go.Scatter(
        x=comp["date"],
        y=comp["composite_pti"],
        mode="lines",
        line=dict(color="#1976D2", width=3),
        name="Composite PTI",
    ))

    # 5. Layout
    fig.update_layout(
        title="Composite Price-to-Income Ratio with Demographia Zones",
        xaxis_title="Date",
        yaxis_title="Price-to-Income (PTI)",
        font=dict(color=text_color),
    )

    ymax = max(12, float(comp["composite_pti"].max()) + 1.0, 10.0)
    fig.update_yaxes(range=[0, ymax])

    return fig

# ---------- Not used: Covid Snapshot / Market Tightness ----------

def yoy_pti_change(summary: pd.DataFrame, y0: int, y1: int) -> go.Figure:
    base = summary[summary["year"] == y0][["city_full", "price_to_income"]].rename(
        columns={"price_to_income": "pti_base"}
    )
    follow = summary[summary["year"] == y1][["city_full", "price_to_income"]].rename(
        columns={"price_to_income": "pti_follow"}
    )

    merged = base.merge(follow, on="city_full", how="inner")
    merged["yoy_pct"] = (merged["pti_follow"] - merged["pti_base"]) / merged[
        "pti_base"
    ] * 100.0

    merged = merged.dropna(subset=["yoy_pct"]).sort_values("yoy_pct", ascending=False)

    fig = px.bar(
        merged.head(15),
        x="yoy_pct",
        y="city_full",
        orientation="h",
        labels={"yoy_pct": f"% Change in PTI ({y0}→{y1})", "city_full": "Metro"},
        title=f"Top PTI Surges During COVID Period ({y0}→{y1})",
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


def composite_dom_inventory(summary: pd.DataFrame) -> go.Figure:
    comp = (
        summary.groupby("year", as_index=False)[["dom", "inventory"]]
        .mean()
        .rename(columns={"dom": "Median DOM", "inventory": "Inventory"})
    )

    fig = px.line(
        comp.melt(id_vars="year", var_name="Metric", value_name="Value"),
        x="year",
        y="Value",
        color="Metric",
        markers=True,
        title="Composite Market Tightness – DOM and Inventory",
    )
    return fig


def composite_sale_to_list(summary: pd.DataFrame) -> go.Figure:
    comp = (
        summary.groupby("year", as_index=False)["sale_to_list_ratio"]
        .mean()
        .rename(columns={"sale_to_list_ratio": "sale_to_list"})
    )

    fig = px.line(
        comp,
        x="year",
        y="sale_to_list",
        markers=True,
        labels={"sale_to_list": "Sale-to-List Ratio"},
        title="Composite Sale-to-List Ratio (Market Competition Signal)",
    )
    return fig


# ---------- CHAPTER 5: SNAPSHOT ----------

def metro_snapshot_bar(summary):
    """
    Build the horizontal bar chart for the latest year,
    colored by affordability rating.
    """
    year_latest = summary["year"].max()

    summary_latest = (
        summary[summary["year"] == year_latest]
        .dropna(subset=["price_to_income"])
        .copy()
    )

    summary_latest = summary_latest.sort_values("price_to_income", ascending=True)

    bottom5 = summary_latest.head(5)
    top5 = summary_latest.tail(5)

    import plotly.express as px
    import plotly.graph_objects as go

    fig = px.bar(
        summary_latest,
        x="price_to_income",
        y="city_full",
        orientation="h",
        color="affordability_rating",
        color_discrete_map={
            "Affordable": "#66BB6A",          # green
            "Moderately Unaffordable": "#FBC02D",  # soft amber
            "Seriously Unaffordable": "#FF9800",   # orange
            "Severely Unaffordable": "#FF7043",    # coral red
            "Impossibly Unaffordable": "#D32F2F",  # deep red
        },

        labels={
            "price_to_income": "Price-to-Income Ratio (PTI)",
            "city_full": "Metro",
            "affordability_rating": "Affordability Rating",
        },
        title=f"Metro PTI Levels in {year_latest} (Colored by Affordability Rating)",
    )

    fig.update_layout(
        yaxis=dict(title=""),
        xaxis=dict(title="Price-to-Income Ratio (PTI)"),
        legend_title_text="Affordability Rating",
        bargap=0.25,
        height=max(700, 20 * len(summary_latest)),
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>PTI: %{x:.1f}x<br>%{marker.color}<extra></extra>"
    )

    for _, row in bottom5.iterrows():
        fig.add_annotation(
            x=row["price_to_income"],
            y=row["city_full"],
            xanchor="left",
            yanchor="middle",
            text=" Most Affordable",
            showarrow=False,
            font=dict(size=10),
        )

    for _, row in top5.iterrows():
        fig.add_annotation(
            x=row["price_to_income"],
            y=row["city_full"],
            xanchor="right",
            yanchor="middle",
            text=" Least Affordable",
            showarrow=False,
            font=dict(size=10, color="white"),
        )
        
    return fig