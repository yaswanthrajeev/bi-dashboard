import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Business Dashboard", 
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    /* KPI card styling */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #4a5568;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 50px;
        height: 3px;
        background: #764ba2;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }
    
    /* Filter headers */
    .filter-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Load CSV
df = pd.read_csv("data/business.csv")

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

st.markdown('<h1 class="main-header">📊 Business Performance Dashboard</h1>', unsafe_allow_html=True)

st.markdown('<div class="section-header">📈 Key Performance Metrics</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">${df['total revenue'].sum():,.0f}</div>
        <div class="kpi-label">Total Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">${df['gross profit'].sum():,.0f}</div>
        <div class="kpi-label">Gross Profit</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{df['# of orders'].sum():,}</div>
        <div class="kpi-label">Total Orders</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{df['new customers'].sum():,}</div>
        <div class="kpi-label">New Customers</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown('<div class="filter-header">🔍 Dashboard Filters</div>', unsafe_allow_html=True)
start_date = st.sidebar.date_input("📅 Start Date", df["date"].min())
end_date = st.sidebar.date_input("📅 End Date", df["date"].max())

st.sidebar.markdown('<div class="filter-header">📊 Data Aggregation</div>', unsafe_allow_html=True)
agg_level = st.sidebar.selectbox("Aggregate Data By", ["Daily", "Weekly", "Monthly"])

# Filter data based on date range
mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
filtered_df = df.loc[mask]

# Resample data
if agg_level == "Weekly":
    agg_df = filtered_df.resample("W-Mon", on="date").sum().reset_index().sort_values("date")
elif agg_level == "Monthly":
    agg_df = filtered_df.resample("M", on="date").sum().reset_index().sort_values("date")
else:  # Daily
    agg_df = filtered_df.copy()

st.markdown('<div class="section-header">📈 Revenue & Profit Trends</div>', unsafe_allow_html=True)

fig_trends = go.Figure()

fig_trends.add_trace(go.Scatter(
    x=agg_df["date"],
    y=agg_df["total revenue"],
    mode='lines+markers',
    name='Total Revenue',
    line=dict(color='#667eea', width=3),
    marker=dict(size=8),
    hovertemplate='<b>Total Revenue</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
))

fig_trends.add_trace(go.Scatter(
    x=agg_df["date"],
    y=agg_df["gross profit"],
    mode='lines+markers',
    name='Gross Profit',
    line=dict(color='#764ba2', width=3),
    marker=dict(size=8),
    hovertemplate='<b>Gross Profit</b><br>Date: %{x}<br>Amount: $%{y:,.0f}<extra></extra>'
))

fig_trends.update_layout(
    title="Revenue and Profit Trends Over Time",
    xaxis_title="Date",
    yaxis_title="Amount ($)",
    hovermode='x unified',
    height=500,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

fig_trends.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
fig_trends.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

st.plotly_chart(fig_trends, use_container_width=True)

st.markdown('<div class="section-header">📦 Orders Analysis</div>', unsafe_allow_html=True)

# Reshape agg_df into long form
orders_long = agg_df.melt(
    id_vars=["date"], 
    value_vars=["# of orders", "# of new orders"],
    var_name="Order Type", 
    value_name="Count"
)

fig_orders = px.bar(
    orders_long,
    x="date",
    y="Count",
    color="Order Type",
    barmode="group",
    title="Orders vs New Orders Comparison",
    labels={"Count": "Number of Orders", "date": "Date"},
    color_discrete_sequence=['#667eea', '#764ba2']
)

fig_orders.update_traces(marker_line_width=0, opacity=0.8)
fig_orders.update_layout(
    bargap=0.2,
    height=450,
    xaxis=dict(
        title="",
        tickformat="%b %Y" if agg_level == "Monthly" else "%d %b"
    ),
    legend_title_text="",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

st.plotly_chart(fig_orders, use_container_width=True)

st.markdown('<div class="section-header">👥 Customer Acquisition</div>', unsafe_allow_html=True)

fig_customers = go.Figure()

fig_customers.add_trace(go.Bar(
    x=agg_df["date"],
    y=agg_df["new customers"],
    name="New Customers",
    marker_color='#667eea',
    opacity=0.8,
    hovertemplate='<b>New Customers</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
))

fig_customers.update_layout(
    title="New Customer Acquisition Over Time",
    xaxis_title="Date",
    yaxis_title="Number of New Customers",
    height=450,
    bargap=0.3,
    xaxis=dict(tickformat="%b %Y" if agg_level=="Monthly" else "%d %b"),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

fig_customers.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
fig_customers.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

st.plotly_chart(fig_customers, use_container_width=True)

st.markdown('<div class="section-header">💰 Cost Structure Analysis</div>', unsafe_allow_html=True)

avg_cogs = filtered_df["COGS"].mean()
avg_profit = filtered_df["gross profit"].mean()

data = pd.DataFrame({
    "Category": ["COGS", "Gross Profit"],
    "Value": [avg_cogs, avg_profit]
})

fig_pie = go.Figure(data=[go.Pie(
    labels=data["Category"],
    values=data["Value"],
    hole=0.4,
    marker_colors=['#ff6b6b', '#4ecdc4'],
    textposition="outside",
    textinfo="percent+label",
    hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Share: %{percent}<extra></extra>'
)])

fig_pie.update_layout(
    title="Average Cost Breakdown (Donut Chart)",
    height=450,
    showlegend=False,
    margin=dict(t=50, b=30, l=30, r=30),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('<div class="section-header">📋 Data Explorer</div>', unsafe_allow_html=True)

with st.expander("📊 View Detailed Data & Analytics", expanded=False):
    st.subheader("📈 Summary Statistics")
    
    summary_stats = filtered_df.describe().round(2)
    st.dataframe(summary_stats, use_container_width=True)
    
    st.subheader("📥 Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"business_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        summary_csv = summary_stats.to_csv()
        st.download_button(
            label="📊 Download Summary Stats (CSV)",
            data=summary_csv,
            file_name=f"business_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    st.subheader("🔍 Raw Data Table")
    st.dataframe(filtered_df, use_container_width=True, height=400)

st.markdown("---")
st.markdown(f"*Dashboard last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
