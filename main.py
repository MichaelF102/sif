import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# Load Data
# -------------------------
data = {
    "Fund": [
        "qsif Hybrid Long-Short Fund",
        "Altiva Hybrid LongShort Fund",
        "qsif Equity Long Short Fund",
        "qsif Equity ExTop 100 LongShort Fund",
        "ISIF Hybrid LongShort Fund",
        "iSIF Equity ExTop 100 LongShort Fund",
        "Titanium Hybrid LongShort Fund",
        "Magnum Hybrid Long Short Fund",
        "Arudha Equity LongShort Fund",
        "Arudha Hybrid LongShort Fund",
        "Diviniti Equity Long Short Fund",
        "DynaSIF Active Asset Allocator LongShort Fund",
        "DynaSIF Equity Long Short Fund"
    ],
    "Equity": [20.89,38.36,70.56,70.51,66.87,86.15,48.69,68.15,60.11,-0.13,9.83,62.56,0],
    "Debt": [36.96,43.08,8.22,6.87,24.45,5.59,23.28,23.83,37.72,66.62,7.78,9.67,25.63],
    "Others": [16.79,15.83,21.21,22.62,8.68,8.26,28.12,4.18,2.17,22.51,82.39,27.06,74.37],
    "Real Estate": [25.35,2.72,0,0,0,0,0,3.84,0,0,0,0.72,0]
}

df = pd.DataFrame(data)

# -------------------------
# Derived Metrics
# -------------------------
df["Risk Score"] = df["Equity"]*0.6 + df["Debt"]*0.3 + df["Others"]*0.1

# -------------------------
# Sidebar - Global Filters
# -------------------------
st.sidebar.title("🎯 Filters")

selected_funds = st.sidebar.multiselect(
    "Select Funds",
    df["Fund"],
    default=list(df["Fund"])
)

filtered_df = df[df["Fund"].isin(selected_funds)]

# -------------------------
# Tabs Layout
# -------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "📊 Fund Comparison",
    "🔍 Deep Dive"
])

# -------------------------
# Overview Tab
# -------------------------
with tab1:
    st.title("📊 SIF India - Overview")

    st.markdown(f"## Fund Name: {filtered_df.loc[filtered_df['Equity'].idxmax(), 'Fund']}")

    col1, col2= st.columns(2)

    col1.metric("Avg Equity", f"{filtered_df['Equity'].mean():.2f}%")
    col2.metric("Avg Debt", f"{filtered_df['Debt'].mean():.2f}%")

    # Bar Chart
    fig = px.bar(
        filtered_df,
        x="Fund",
        y="Equity",
        title="Equity Allocation",
        color="Equity"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Pie Chart
    total = filtered_df[["Equity","Debt","Others","Real Estate"]].sum()

    fig2 = px.pie(
        values=total.values,
        names=total.index,
        title="Overall Allocation"
    )
    st.plotly_chart(fig2, use_container_width=True)

    filtered_df["Diversification"] = (
    1 - filtered_df[["Equity","Debt","Others","Real Estate"]].std(axis=1)/100
    )

    fig = px.bar(
    filtered_df,
    x="Fund",
    y=["Equity","Debt","Others","Real Estate"],
    title="Asset Allocation Breakdown",
    )

    st.plotly_chart(fig, use_container_width=True)

    
# -------------------------
# Fund Comparison Tab
# -------------------------
with tab2:
    st.title("📊 Fund Comparison")

    sort_by = st.selectbox(
    "Sort Funds By",
    ["Equity", "Debt", "Others", "Real Estate", "Risk Score"]
    )

    sorted_df = filtered_df.sort_values(sort_by, ascending=False)

    # Optional: Add table
    st.dataframe(sorted_df)

    fig = go.Figure()

    for col in ["Equity","Debt","Others","Real Estate"]:
        fig.add_trace(go.Bar(
            name=col,
            x=sorted_df["Fund"],
            y=sorted_df[col]
        ))

    fig.update_layout(
        barmode='stack',
        title=f"Asset Allocation (Sorted by {sort_by})",
        xaxis_title="Funds",
        yaxis_title="Allocation (%)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚔️ Head-to-Head Comparison")

    col1, col2 = st.columns(2)

    fund1 = col1.selectbox("Select Fund 1", sorted_df["Fund"])
    fund2 = col2.selectbox("Select Fund 2", sorted_df["Fund"], index=1)

    f1 = sorted_df[sorted_df["Fund"] == fund1].iloc[0]
    f2 = sorted_df[sorted_df["Fund"] == fund2].iloc[0]

    compare_df = pd.DataFrame({
        "Metric": ["Equity","Debt","Others","Real Estate","Risk Score"],
        fund1: [f1[c] for c in ["Equity","Debt","Others","Real Estate","Risk Score"]],
        fund2: [f2[c] for c in ["Equity","Debt","Others","Real Estate","Risk Score"]],
    })

    st.dataframe(compare_df)

    diff = compare_df.set_index("Metric")
    diff["Difference"] = diff[fund1] - diff[fund2]

    fig_diff = px.bar(
    diff,
    y=diff.index,
    x="Difference",
    title=f"Difference: {fund1} vs {fund2}",
    orientation='h'
    )

    st.plotly_chart(fig_diff, use_container_width=True)

    st.subheader("🏆 Top 5 Funds")

    top5 = sorted_df.head(5)
    st.dataframe(top5[["Fund","Equity","Debt","Risk Score"]])

    st.subheader("⚠️ Lowest Equity Funds")

    bottom5 = sorted_df.sort_values("Equity").head(5)
    st.dataframe(bottom5[["Fund","Equity","Debt"]])

    

    # -------------------------
    # Deep Dive Tab
    # -------------------------
with tab3:
    st.title("🔍 Deep Dive")

    fund = st.selectbox("Select Fund", filtered_df["Fund"])


    if fund:
        row = filtered_df[filtered_df["Fund"] == fund].iloc[0]

        categories = ["Equity","Debt","Others","Real Estate"]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[row[c] for c in categories],
            theta=categories,
            fill='toself',
            name=fund
        ))

        fig.update_layout(title="Asset Allocation Radar")

        st.plotly_chart(fig, use_container_width=True)

        # Metrics Row
        c1, c2 = st.columns(2)
        c1.metric("Risk Score", round(row["Risk Score"],2))
        c2.metric("Equity Exposure", f"{row['Equity']}%")

        st.subheader("📊 Relative Position")

        rank = filtered_df["Risk Score"].rank(ascending=False)
        fund_rank = int(rank[filtered_df["Fund"] == fund].values[0])

        st.write(f"Risk Rank: {fund_rank} / {len(filtered_df)}")

        st.subheader("📊 vs Market Average")

        avg = filtered_df[["Equity","Debt","Others","Real Estate"]].mean()

        compare_df = pd.DataFrame({
            "Metric": ["Equity","Debt","Others","Real Estate"],
            "Fund": [row[c] for c in ["Equity","Debt","Others","Real Estate"]],
            "Average": avg.values
        })

        fig_compare = go.Figure()

        fig_compare.add_trace(go.Bar(name="Fund", x=compare_df["Metric"], y=compare_df["Fund"]))
        fig_compare.add_trace(go.Bar(name="Average", x=compare_df["Metric"], y=compare_df["Average"]))

        fig_compare.update_layout(barmode="group", title="Fund vs Average")

        st.plotly_chart(fig_compare, use_container_width=True)

       
