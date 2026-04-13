from __future__ import annotations

from datetime import date
from io import BytesIO, StringIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Spend and Applications across 2024 - 2025",
    layout="wide",
)


TITLE = "Spend and Applications across 2024 - 2025"
SPEND_COLUMNS = [
    "DSP",
    "LeadGen",
    "Paid Search",
    "Paid Social",
    "Prescreen",
    "Referrals",
    "Sweepstakes",
]
APP_COLUMNS = ["Digital_Apps", "Physical_Apps"]
APPROVED_COLUMNS = ["Digital_Approved", "Physical_Approved"]
REQUIRED_COLUMNS = ["ISO_YEAR", "ISO_WEEK", "STATE_CD", *SPEND_COLUMNS, *APP_COLUMNS, *APPROVED_COLUMNS]
COLOR_MAP = {
    "DSP": "#1f77b4",
    "LeadGen": "#ff7f0e",
    "Paid Search": "#2ca02c",
    "Paid Social": "#d62728",
    "Prescreen": "#9467bd",
    "Referrals": "#8c564b",
    "Sweepstakes": "#e377c2",
    "Digital_Apps": "#17becf",
    "Physical_Apps": "#111111",
}


def _read_uploaded_file(uploaded_file) -> pd.DataFrame:
    file_name = uploaded_file.name.lower()
    payload = uploaded_file.getvalue()

    if file_name.endswith(".csv"):
        return pd.read_csv(StringIO(payload.decode("utf-8-sig")))
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(payload))

    raise ValueError("Please upload a CSV or Excel file.")


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required columns: {missing_text}")


def _build_week_start(iso_year: int, iso_week: int) -> date:
    return date.fromisocalendar(int(iso_year), int(iso_week), 1)


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    _validate_columns(df)

    working_df = df[REQUIRED_COLUMNS].copy()
    working_df["ISO_YEAR"] = pd.to_numeric(working_df["ISO_YEAR"], errors="coerce")
    working_df["ISO_WEEK"] = pd.to_numeric(working_df["ISO_WEEK"], errors="coerce")

    numeric_columns = SPEND_COLUMNS + APP_COLUMNS + APPROVED_COLUMNS
    for column in numeric_columns:
        working_df[column] = pd.to_numeric(working_df[column], errors="coerce").fillna(0.0)

    working_df = working_df.dropna(subset=["ISO_YEAR", "ISO_WEEK", "STATE_CD"]).copy()
    working_df["ISO_YEAR"] = working_df["ISO_YEAR"].astype(int)
    working_df["ISO_WEEK"] = working_df["ISO_WEEK"].astype(int)
    working_df["STATE_CD"] = working_df["STATE_CD"].astype(str).str.strip()

    working_df["week_start"] = working_df.apply(
        lambda row: _build_week_start(row["ISO_YEAR"], row["ISO_WEEK"]),
        axis=1,
    )
    working_df["week_start"] = pd.to_datetime(working_df["week_start"])
    working_df["week_label"] = working_df["week_start"].apply(
        lambda value: f"{value.isocalendar().year}-W{value.isocalendar().week:02d}"
    )

    grouped = (
        working_df.groupby(["STATE_CD", "ISO_YEAR", "ISO_WEEK", "week_start", "week_label"], as_index=False)[
            SPEND_COLUMNS + APP_COLUMNS + APPROVED_COLUMNS
        ]
        .sum()
        .sort_values(["STATE_CD", "week_start"])
    )
    return grouped


def _build_chart(state_df: pd.DataFrame, selected_state: str) -> go.Figure:
    figure = go.Figure()

    for column in SPEND_COLUMNS:
        figure.add_trace(
            go.Scatter(
                x=state_df["week_start"],
                y=state_df[column],
                mode="lines+markers",
                name=column,
                line={"width": 2, "color": COLOR_MAP[column]},
                marker={"size": 6},
                yaxis="y",
                hovertemplate="%{x|%Y-%m-%d}<br>" + column + ": %{y:,.2f}<extra></extra>",
            )
        )

    for column in APP_COLUMNS:
        figure.add_trace(
            go.Scatter(
                x=state_df["week_start"],
                y=state_df[column],
                mode="lines+markers",
                name=column,
                line={"width": 3, "dash": "dot", "color": COLOR_MAP[column]},
                marker={"size": 7},
                yaxis="y2",
                hovertemplate="%{x|%Y-%m-%d}<br>" + column + ": %{y:,.0f}<extra></extra>",
            )
        )

    figure.update_layout(
        title=f"{TITLE}: {selected_state}",
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        margin={"l": 20, "r": 20, "t": 80, "b": 20},
        xaxis={
            "title": "Week",
            "tickformat": "%Y-W%V",
            "tickangle": -45,
        },
        yaxis={"title": "Spend", "tickformat": ",.0f"},
        yaxis2={"title": "Applications", "overlaying": "y", "side": "right", "tickformat": ",.0f"},
    )
    return figure


def _build_quarterly_summary(state_df: pd.DataFrame) -> pd.DataFrame:
    quarterly_df = (
        state_df.assign(quarter=state_df["week_start"].dt.to_period("Q"))
        .groupby("quarter", as_index=False)[SPEND_COLUMNS + APP_COLUMNS + APPROVED_COLUMNS]
        .sum()
    )
    quarterly_df["total_spend"] = quarterly_df[SPEND_COLUMNS].sum(axis=1)
    quarterly_df["digital_spend_per_application"] = (
        quarterly_df["total_spend"] / quarterly_df["Digital_Apps"].replace(0, pd.NA)
    )
    quarterly_df["physical_spend_per_application"] = (
        quarterly_df["total_spend"] / quarterly_df["Physical_Apps"].replace(0, pd.NA)
    )
    quarterly_df["digital_approval_rate"] = (
        quarterly_df["Digital_Approved"] / quarterly_df["Digital_Apps"].replace(0, pd.NA)
    )
    quarterly_df["physical_approval_rate"] = (
        quarterly_df["Physical_Approved"] / quarterly_df["Physical_Apps"].replace(0, pd.NA)
    )
    quarterly_df["digital_spend_per_approved_application"] = (
        quarterly_df["total_spend"] / quarterly_df["Digital_Approved"].replace(0, pd.NA)
    )
    quarterly_df["physical_spend_per_approved_application"] = (
        quarterly_df["total_spend"] / quarterly_df["Physical_Approved"].replace(0, pd.NA)
    )
    quarterly_df["Quarter"] = quarterly_df["quarter"].astype(str)
    quarterly_df["Digital Spend per Application"] = quarterly_df["digital_spend_per_application"].apply(
        lambda value: "n/a" if pd.isna(value) else f"${value:,.2f}"
    )
    quarterly_df["Digital Approval Rate"] = quarterly_df["digital_approval_rate"].apply(
        lambda value: "n/a" if pd.isna(value) else f"{value:.1%}"
    )
    quarterly_df["Digital Spend per Approved Application"] = quarterly_df[
        "digital_spend_per_approved_application"
    ].apply(lambda value: "n/a" if pd.isna(value) else f"${value:,.2f}")
    quarterly_df["Digital Total Approved Applications"] = quarterly_df["Digital_Approved"].apply(
        lambda value: f"{value:,.0f}"
    )
    quarterly_df["Physical Spend per Application"] = quarterly_df["physical_spend_per_application"].apply(
        lambda value: "n/a" if pd.isna(value) else f"${value:,.2f}"
    )
    quarterly_df["Digital Approval Rate"] = quarterly_df["digital_approval_rate"].apply(
        lambda value: "n/a" if pd.isna(value) else f"{value:.1%}"
    )
    quarterly_df["Physical Approval Rate"] = quarterly_df["physical_approval_rate"].apply(
        lambda value: "n/a" if pd.isna(value) else f"{value:.1%}"
    )
    quarterly_df["Physical Spend per Approved Application"] = quarterly_df[
        "physical_spend_per_approved_application"
    ].apply(lambda value: "n/a" if pd.isna(value) else f"${value:,.2f}")
    quarterly_df["Physical Total Approved Applications"] = quarterly_df["Physical_Approved"].apply(
        lambda value: f"{value:,.0f}"
    )
    summary_df = quarterly_df[
        [
            "Quarter",
            "Digital Spend per Application",
            "Digital Approval Rate",
            "Digital Spend per Approved Application",
            "Digital Total Approved Applications",
            "Physical Spend per Application",
            "Physical Approval Rate",
            "Physical Spend per Approved Application",
            "Physical Total Approved Applications",
        ]
    ].copy()
    summary_df.columns = pd.MultiIndex.from_tuples(
        [
            ("Quarter", "Quarter"),
            ("Digital", "Spend / App"),
            ("Digital", "Approval Rate"),
            ("Digital", "Spend / Approved App"),
            ("Digital", "Approved Apps"),
            ("Physical", "Spend / App"),
            ("Physical", "Approval Rate"),
            ("Physical", "Spend / Approved App"),
            ("Physical", "Approved Apps"),
        ]
    )
    return summary_df


def _style_quarterly_summary(summary_df: pd.DataFrame):
    styles = [
        {
            "selector": "table",
            "props": [("font-size", "0.88rem"), ("border-collapse", "collapse"), ("width", "100%")],
        },
        {
            "selector": "thead th",
            "props": [
                ("font-size", "0.82rem"),
                ("font-style", "italic"),
                ("font-weight", "600"),
                ("text-align", "center"),
                ("padding", "0.5rem 0.45rem"),
            ],
        },
        {
            "selector": "tbody td",
            "props": [("padding", "0.45rem"), ("font-size", "0.84rem"), ("text-align", "center")],
        },
    ]
    return (
        summary_df.style.hide(axis="index")
        .set_table_styles(styles)
        .set_properties(subset=pd.IndexSlice[:, [("Quarter", "Quarter")]], **{"font-weight": "700"})
        .set_properties(subset=pd.IndexSlice[:, pd.IndexSlice["Digital", :]], **{"background-color": "#eef6ff"})
        .set_properties(subset=pd.IndexSlice[:, pd.IndexSlice["Physical", :]], **{"background-color": "#fff4ea"})
        .set_properties(
            subset=pd.IndexSlice[:, [("Digital", "Approval Rate"), ("Physical", "Approval Rate")]],
            **{"font-style": "italic", "font-weight": "700"},
        )
    )


def main() -> None:
    st.title(TITLE)
    st.caption("Upload a CSV or Excel file, then toggle through each state to view weekly spend and application trends.")

    uploaded_file = st.file_uploader("Upload modeling file", type=["csv", "xlsx", "xls"])

    if uploaded_file is None:
        st.info("Upload `ModelingFile_ForPlot.csv` to begin.")
        return

    try:
        raw_df = _read_uploaded_file(uploaded_file)
        prepared_df = _prepare_data(raw_df)
    except Exception as exc:
        st.error(str(exc))
        return

    states = sorted(prepared_df["STATE_CD"].dropna().unique().tolist())
    if not states:
        st.warning("No states were found in the uploaded file.")
        return

    selected_state = st.selectbox("Select a state", options=states)
    state_df = prepared_df.loc[prepared_df["STATE_CD"] == selected_state].sort_values("week_start")

    if state_df.empty:
        st.warning(f"No rows were found for {selected_state}.")
        return

    st.plotly_chart(_build_chart(state_df, selected_state), use_container_width=True)
    st.caption("Quarterly digital and physical application summary")
    st.dataframe(
        _style_quarterly_summary(_build_quarterly_summary(state_df)),
        use_container_width=True,
    )

    with st.expander("View filtered data"):
        display_columns = ["ISO_YEAR", "ISO_WEEK", "STATE_CD", *SPEND_COLUMNS, *APP_COLUMNS, *APPROVED_COLUMNS]
        st.dataframe(state_df[display_columns], use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
