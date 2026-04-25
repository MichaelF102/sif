import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------
# App Config
# -------------------------
st.set_page_config(page_title="SIF India NAV Dashboard", layout="wide")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("sif_data3.csv")

    df.columns = df.columns.str.strip()
    df.rename(columns={df.columns[0]: "Date"}, inplace=True)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    for col in df.columns[1:]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "")
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values("Date")

df = load_data()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.title("🎯 Filters")

funds = df.columns[1:]

selected_funds = st.sidebar.multiselect(
    "Select Funds",
    funds,
    default=list(funds[:3])
)

if len(selected_funds) == 0:
    st.warning("Please select at least one fund")
    st.stop()

# Clean subset
filtered = df[["Date"] + selected_funds].dropna()

if filtered.empty:
    st.warning("No data available")
    st.stop()

# -------------------------
# Precompute Metrics
# -------------------------
returns_daily = filtered.set_index("Date")[selected_funds].pct_change()

total_returns = (
    (filtered[selected_funds].iloc[-1] /
     filtered[selected_funds].iloc[0] - 1) * 100
)

volatility = returns_daily.std() * np.sqrt(252)

risk_return_df = pd.DataFrame({
    "Return": returns_daily.mean() * 252,
    "Volatility": volatility
})

# Normalized NAV
norm_df = filtered.copy()
for col in selected_funds:
    norm_df[col] = (norm_df[col] / norm_df[col].iloc[0]) * 100

# -------------------------
# Tabs
# -------------------------
tab1, tab2 = st.tabs(["📊 Overview", "📈 Advanced Analytics"])

# =========================
# 📊 OVERVIEW
# =========================
with tab1:
    st.title("📊 SIF India Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Funds Selected", len(selected_funds))
    col2.metric("Best Fund", total_returns.idxmax())
    col3.metric("Max Return", f"{total_returns.max():.2f}%")
    col4.metric("Avg Return", f"{total_returns.mean():.2f}%")

    # Growth Comparison
    st.subheader("📈 Growth Comparison")
    fig1 = px.line(norm_df, x="Date", y=selected_funds)
    st.plotly_chart(fig1, use_container_width=True)

    # Returns Ranking
    st.subheader("💰 Return Ranking")
    returns_df = total_returns.sort_values(ascending=False)

    fig2 = px.bar(
        returns_df,
        x=returns_df.index,
        y=returns_df.values,
        labels={"x": "Fund", "y": "Return %"}
    )
    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 📈 ADVANCED ANALYTICS
# =========================
with tab2:
    st.title("📈 Advanced Fund Analytics")

    # NAV Comparison
    st.subheader("NAV Comparison")
    fig3 = px.line(filtered, x="Date", y=selected_funds)
    st.plotly_chart(fig3, use_container_width=True)

    # Drawdown
    st.subheader("📉 Drawdown")
    dd = norm_df.set_index("Date")[selected_funds]
    drawdown = (dd / dd.cummax()) - 1

    fig4 = px.line(drawdown)
    st.plotly_chart(fig4, use_container_width=True)

    # Volatility
    st.subheader("⚡ Volatility (Annualized)")
    vol_df = volatility.to_frame(name="Volatility")

    fig5 = px.bar(vol_df, x=vol_df.index, y="Volatility")
    st.plotly_chart(fig5, use_container_width=True)

    # Rolling Volatility
    st.subheader("📉 Rolling Volatility (30D)")

    rolling_vol = returns_daily.rolling(30).std() * np.sqrt(252)

    fig8 = px.line(rolling_vol)
    st.plotly_chart(fig8, use_container_width=True)
