
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Bluestock | Mutual Fund Analytics",
    page_icon="📈",
    layout="wide",
)

DB_PATH = Path(__file__).parent / "data" / "db" / "bluestock_mf.db"

st.title("📈 Bluestock Mutual Fund Analytics")
st.caption("Explore fund data, NAV history, transactions and analytics.")

@st.cache_data
def load_database():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    # Read-only connection: the app cannot write to the database.
    uri = DB_PATH.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        tables = pd.read_sql_query(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """,
            conn,
        )["name"].tolist()

        data = {}
        for table in tables:
            # Table names come from SQLite's own table catalogue.
            escaped = table.replace('"', '""')
            data[table] = pd.read_sql_query(
                f'SELECT * FROM "{escaped}"', conn
            )

    return data


try:
    tables = load_database()
except Exception as exc:
    st.error(f"Could not load the database: {exc}")
    st.stop()

if not tables:
    st.warning("No tables were found in the database.")
    st.stop()

fund_table = next(
    (name for name in tables if name.lower() == "dim_fund"),
    None,
)
nav_table = next(
    (name for name in tables if name.lower() == "fact_nav"),
    None,
)

funds = tables[fund_table] if fund_table else pd.DataFrame()
nav = tables[nav_table] if nav_table else pd.DataFrame()

c1, c2, c3 = st.columns(3)
c1.metric("Database tables", len(tables))
c2.metric("Fund records", len(funds))
c3.metric("NAV records", len(nav))

st.divider()

overview, explorer, charts = st.tabs(
    ["Overview", "Data Explorer", "Charts"]
)

with overview:
    st.subheader("Database Overview")

    summary = pd.DataFrame([
        {"Table": name, "Rows": len(df), "Columns": len(df.columns)}
        for name, df in tables.items()
    ])
    st.dataframe(summary, hide_index=True, use_container_width=True)

    if not funds.empty:
        st.subheader("Fund Records")
        st.dataframe(funds.head(10), hide_index=True, use_container_width=True)

with explorer:
    st.subheader("Explore Your Data")

    selected_table = st.selectbox("Choose a table", tables)
    df = tables[selected_table]

    search = st.text_input("Filter rows (search across text)")
    if search:
        mask = df.astype(str).apply(
            lambda col: col.str.contains(search, case=False, na=False)
        ).any(axis=1)
        df = df[mask]

    st.caption(f"{len(df):,} matching rows")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download displayed data as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_table}.csv",
        mime="text/csv",
    )

with charts:
    st.subheader("Interactive Charts")

    selected_table = st.selectbox(
        "Chart data source", tables, key="chart_table"
    )
    df = tables[selected_table]

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    other_cols = [col for col in df.columns if col not in numeric_cols]

    if numeric_cols and not df.empty:
        x_options = other_cols or numeric_cols
        x_col = st.selectbox("Horizontal axis", x_options)
        y_col = st.selectbox("Numeric values", numeric_cols)

        chart_df = df[[x_col, y_col]].dropna().head(2000)
        fig = px.bar(
            chart_df,
            x=x_col,
            y=y_col,
            title=f"{y_col} by {x_col}",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("This table has no numeric columns available to chart.")

st.caption("Bluestock Mutual Fund Analytics · Local read-only dashboard")
