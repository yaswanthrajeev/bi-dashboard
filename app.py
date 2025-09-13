import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Executive Business Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# Custom CSS for executive styling
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    
    .executive-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a202c;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .dashboard-subtitle {
        font-size: 1.1rem;
        color: #718096;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .kpi-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        color: white;
        transition: transform 0.2s ease;
    }
    
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .kpi-change {
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .positive { color: #68d391; }
    .negative { color: #fc8181; }
    
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2d3748;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .insight-box {
        background: #f7fafc;
        border-left: 4px solid #4299e1;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .insight-title {
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .recommendation-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #ed8936;
    }
</style>
""", unsafe_allow_html=True)

# Load data from local CSV files
@st.cache_data
def load_data():
    """Load business and marketing data from local CSV files"""
    
    file_paths = {
        'business': 'data/business.csv',
        'facebook': 'data/Facebook_clean.csv',
        'google': 'data/Google_clean.csv',
        'tiktok': 'data/TikTok_clean.csv'
    }
    
    try:
        # Load business data
        business = pd.read_csv(file_paths['business'], parse_dates=['date'])
        
        # Load marketing data
        marketing_data = []
        
        for platform, file_path in [('Facebook', file_paths['facebook']), ('Google', file_paths['google']), ('TikTok', file_paths['tiktok'])]:
            try:
                df = pd.read_csv(file_path, parse_dates=['date'])
                df['platform'] = platform
                
                # Standardize column names
                column_mapping = {
                    'impression': 'impressions',
                    'attributed revenue': 'attributed_revenue'
                }
                df = df.rename(columns=column_mapping)
                
                # Convert numeric columns
                numeric_cols = ['impressions', 'clicks', 'spend', 'attributed_revenue']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                marketing_data.append(df)
            except Exception as e:
                st.warning(f"Could not load {platform} data: {e}")
        
        # Combine marketing data
        if marketing_data:
            combined_marketing = pd.concat(marketing_data, ignore_index=True)
            
            # Aggregate marketing data by date
            marketing_agg = combined_marketing.groupby('date').agg({
                'spend': 'sum',
                'attributed_revenue': 'sum',
                'impressions': 'sum',
                'clicks': 'sum'
            }).reset_index()
            
            # Merge with business data
            df = business.merge(marketing_agg, on='date', how='left', suffixes=('', '_marketing'))
            
            # Fill missing marketing data with 0
            marketing_cols = ['spend', 'attributed_revenue', 'impressions', 'clicks']
            for col in marketing_cols:
                if col in df.columns:
                    df[col] = df[col].fillna(0)
        else:
            df = business.copy()
            # Add empty marketing columns if no marketing data
            df['spend'] = 0
            df['attributed_revenue'] = 0
            df['impressions'] = 0
            df['clicks'] = 0
        
        # Standardize business column names
        column_mapping = {
            'total revenue': 'total_revenue',
            'gross profit': 'gross_profit', 
            '# of orders': 'orders',
            '# of new orders': 'new_orders',
            'new customers': 'new_customers',
            'COGS': 'cogs'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Convert numeric columns
        numeric_cols = ['total_revenue', 'gross_profit', 'orders', 'new_orders', 'new_customers', 'cogs']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df, combined_marketing if marketing_data else pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

def calculate_change(current, previous):
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

def format_change(change):
    if change > 0:
        return f'<span class="positive">↗ +{change:.1f}%</span>'
    elif change < 0:
        return f'<span class="negative">↘ {change:.1f}%</span>'
    else:
        return '<span style="color: #a0aec0;">→ 0.0%</span>'

# Load data
df, marketing_df = load_data()

# Header
st.markdown('<h1 class="executive-header">Executive Business Dashboard</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="dashboard-subtitle">Strategic Performance Overview • {datetime.now().strftime("%B %Y")}</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    # Date range selector
    date_range = st.date_input(
        "📅 Select Date Range",
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min(),
        max_value=df['date'].max(),
        key="date_range"
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = df['date'].min()
        end_date = df['date'].max()

with col2:
    aggregation = st.selectbox("📊 View By", ["Daily", "Weekly", "Monthly"], index=1, key="aggregation")

with col3:
    comparison_period = st.selectbox("📈 Compare to", ["Previous Period", "Same Period Last Year"], key="compare")

with col4:
    # Quick date filters
    quick_filter = st.selectbox("⚡ Quick Filter", ["Custom", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last Year"], key="quick")
    
    if quick_filter != "Custom":
        end_date = df['date'].max()
        if quick_filter == "Last 30 Days":
            start_date = end_date - timedelta(days=30)
        elif quick_filter == "Last 90 Days":
            start_date = end_date - timedelta(days=90)
        elif quick_filter == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        elif quick_filter == "Last Year":
            start_date = end_date - timedelta(days=365)

# Filter data based on selected date range
current_data = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

# Comparison data
date_diff = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
if comparison_period == "Previous Period":
    comp_start = pd.to_datetime(start_date) - timedelta(days=date_diff)
    comp_end = pd.to_datetime(start_date) - timedelta(days=1)
else:
    comp_start = pd.to_datetime(start_date) - timedelta(days=365)
    comp_end = pd.to_datetime(end_date) - timedelta(days=365)

comparison_data = df[(df['date'] >= comp_start) & (df['date'] <= comp_end)]

# Calculate KPIs
current_kpis = {
    'revenue': current_data['total_revenue'].sum(),
    'profit': current_data['gross_profit'].sum(),
    'orders': current_data['orders'].sum(),
    'new_orders': current_data['new_orders'].sum(),
    'customers': current_data['new_customers'].sum(),
    'marketing_spend': current_data['spend'].sum(),
    'marketing_revenue': current_data['attributed_revenue'].sum()
}

comparison_kpis = {
    'revenue': comparison_data['total_revenue'].sum(),
    'profit': comparison_data['gross_profit'].sum(),
    'orders': comparison_data['orders'].sum(),
    'new_orders': comparison_data['new_orders'].sum(),
    'customers': comparison_data['new_customers'].sum(),
    'marketing_spend': comparison_data['spend'].sum(),
    'marketing_revenue': comparison_data['attributed_revenue'].sum()
}

# Core Business KPIs
st.markdown('<div class="section-title">🎯 Core Business Performance</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    change = calculate_change(current_kpis['revenue'], comparison_kpis['revenue'])
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">${current_kpis['revenue']:,.0f}</div>
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    change = calculate_change(current_kpis['profit'], comparison_kpis['profit'])
    margin = (current_kpis['profit'] / current_kpis['revenue']) * 100 if current_kpis['revenue'] > 0 else 0
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">${current_kpis['profit']:,.0f}</div>
        <div class="kpi-label">Gross Profit ({margin:.1f}% margin)</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    change = calculate_change(current_kpis['orders'], comparison_kpis['orders'])
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">{current_kpis['orders']:,}</div>
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    change = calculate_change(current_kpis['customers'], comparison_kpis['customers'])
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">{current_kpis['customers']:,}</div>
        <div class="kpi-label">New Customers</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

# Marketing Impact Analysis
st.markdown('<div class="section-title">💡 Marketing Impact Analysis</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    change = calculate_change(current_kpis['marketing_spend'], comparison_kpis['marketing_spend'])
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">${current_kpis['marketing_spend']:,.0f}</div>
        <div class="kpi-label">Marketing Spend</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    change = calculate_change(current_kpis['marketing_revenue'], comparison_kpis['marketing_revenue'])
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">${current_kpis['marketing_revenue']:,.0f}</div>
        <div class="kpi-label">Marketing-Attributed Revenue</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    marketing_percentage = (current_kpis['marketing_revenue'] / current_kpis['revenue']) * 100 if current_kpis['revenue'] > 0 else 0
    comp_marketing_percentage = (comparison_kpis['marketing_revenue'] / comparison_kpis['revenue']) * 100 if comparison_kpis['revenue'] > 0 else 0
    change = marketing_percentage - comp_marketing_percentage
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">{marketing_percentage:.1f}%</div>
        <div class="kpi-label">% Revenue from Marketing</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    roas = current_kpis['marketing_revenue'] / current_kpis['marketing_spend'] if current_kpis['marketing_spend'] > 0 else 0
    comp_roas = comparison_kpis['marketing_revenue'] / comparison_kpis['marketing_spend'] if comparison_kpis['marketing_spend'] > 0 else 0
    change = calculate_change(roas, comp_roas)
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-value">{roas:.1f}x</div>
        <div class="kpi-label">Marketing ROAS</div>
        <div class="kpi-change">{format_change(change)}</div>
    </div>
    """, unsafe_allow_html=True)

# Platform Performance Analysis
if not marketing_df.empty:
    st.markdown('<div class="section-title">🚀 Platform Performance Breakdown</div>', unsafe_allow_html=True)
    
    # Filter marketing data for current period
    current_marketing = marketing_df[(marketing_df['date'] >= pd.to_datetime(start_date)) & (marketing_df['date'] <= pd.to_datetime(end_date))]
    
    platform_performance = current_marketing.groupby('platform').agg({
        'spend': 'sum',
        'attributed_revenue': 'sum',
        'impressions': 'sum',
        'clicks': 'sum'
    }).reset_index()
    
    platform_performance['roas'] = platform_performance['attributed_revenue'] / platform_performance['spend']
    platform_performance['ctr'] = (platform_performance['clicks'] / platform_performance['impressions']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ROAS by platform
        fig_roas = px.bar(
            platform_performance, 
            x='platform', 
            y='roas',
            title='ROAS by Platform',
            color='roas',
            color_continuous_scale='RdYlGn',
            text='roas'
        )
        fig_roas.update_traces(texttemplate='%{text:.1f}x', textposition='outside')
        
        fig_roas.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_roas, use_container_width=True)
    
        with col2:
            totals = {
                "Total Revenue": current_data["total_revenue"].sum(),
                "COGS": current_data["cogs"].sum(),
                "Gross Profit": current_data["gross_profit"].sum()
            }

            fig_cogs = px.pie(
                names=list(totals.keys()),
                values=list(totals.values()),
                title="Revenue Breakdown: Revenue vs COGS vs Profit",
                color=list(totals.keys()),
                color_discrete_map={
                    "Total Revenue": "#3182ce",
                    "COGS": "#e53e3e",
                    "Gross Profit": "#38a169"
                }
            )
            fig_cogs.update_traces(textinfo="label+percent", pull=[0, 0.05, 0])
            fig_cogs.update_layout(height=350)
            st.plotly_chart(fig_cogs, use_container_width=True)





# Aggregate data based on selected aggregation
if aggregation == "Daily":
    freq = 'D'
    date_format = '%Y-%m-%d'
elif aggregation == "Weekly":
    freq = 'W-Mon'
    date_format = '%Y-%m-%d'
else:  # Monthly
    freq = 'M'
    date_format = '%Y-%m'








# Orders Analysis - Total vs New Orders
st.markdown('<div class="section-title">📦 Orders Analysis: Total vs New Orders</div>', unsafe_allow_html=True)

# Aggregate orders data
orders_data = current_data.resample(freq, on='date').agg({
    'orders': 'sum',
    'new_orders': 'sum'
}).reset_index()

# Calculate repeat orders
orders_data['repeat_orders'] = orders_data['orders'] - orders_data['new_orders']

fig_orders = go.Figure()

# Add total orders line
fig_orders.add_trace(go.Scatter(
    x=orders_data['date'],
    y=orders_data['orders'],
    mode='lines+markers',
    name='Total Orders',
    line=dict(color='#3182ce', width=3),
    marker=dict(size=8),
    hovertemplate=f'<b>Total Orders</b><br>{aggregation}: %{{x}}<br>%{{y:,}} orders<extra></extra>'
))

# Add new orders line
fig_orders.add_trace(go.Scatter(
    x=orders_data['date'],
    y=orders_data['new_orders'],
    mode='lines+markers',
    name='New Orders',
    line=dict(color='#38a169', width=3),
    marker=dict(size=8),
    hovertemplate=f'<b>New Orders</b><br>{aggregation}: %{{x}}<br>%{{y:,}} orders<extra></extra>'
))

# Add filled area for repeat orders
fig_orders.add_trace(go.Scatter(
    x=orders_data['date'],
    y=orders_data['repeat_orders'],
    mode='lines',
    name='Repeat Orders',
    line=dict(color='#ed8936', width=2),
    fill='tonexty',
    fillcolor='rgba(237, 137, 54, 0.2)',
    hovertemplate=f'<b>Repeat Orders</b><br>{aggregation}: %{{x}}<br>%{{y:,}} orders<extra></extra>'
))

fig_orders.update_layout(
    height=400,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=40, b=40, l=40, r=40),
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', title=f"{aggregation} Period"),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', title="Number of Orders")
)

st.plotly_chart(fig_orders, use_container_width=True)

# Revenue & Profit Trends
st.markdown('<div class="section-title">📈 Revenue & Profitability Trends</div>', unsafe_allow_html=True)

trends_data = current_data.resample(freq, on='date').agg({
    'total_revenue': 'sum',
    'gross_profit': 'sum',
    'attributed_revenue': 'sum'
}).reset_index()

fig_trends = go.Figure()

fig_trends.add_trace(go.Scatter(
    x=trends_data['date'],
    y=trends_data['total_revenue'],
    mode='lines+markers',
    name='Total Revenue',
    line=dict(color='#3182ce', width=3),
    marker=dict(size=6),
    hovertemplate=f'<b>Total Revenue</b><br>{aggregation}: %{{x}}<br>$%{{y:,.0f}}<extra></extra>'
))

fig_trends.add_trace(go.Scatter(
    x=trends_data['date'],
    y=trends_data['gross_profit'],
    mode='lines+markers',
    name='Gross Profit',
    line=dict(color='#38a169', width=3),
    marker=dict(size=6),
    hovertemplate=f'<b>Gross Profit</b><br>{aggregation}: %{{x}}<br>$%{{y:,.0f}}<extra></extra>'
))

fig_trends.update_layout(
    height=400,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=40, b=40, l=40, r=40),
    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', title=f"{aggregation} Period"),
    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)', title="Revenue ($)")
)

st.plotly_chart(fig_trends, use_container_width=True)



# Calculate key metrics for insights
revenue_trend = calculate_change(current_kpis['revenue'], comparison_kpis['revenue'])
profit_margin = (current_kpis['profit'] / current_kpis['revenue']) * 100 if current_kpis['revenue'] > 0 else 0
avg_order_value = current_kpis['revenue'] / current_kpis['orders'] if current_kpis['orders'] > 0 else 0
repeat_order_rate = ((current_kpis['orders'] - current_kpis['new_orders']) / current_kpis['orders']) * 100 if current_kpis['orders'] > 0 else 0

# Executive Summary Table
st.markdown('<div class="section-title">📋 Executive Summary</div>', unsafe_allow_html=True)

summary_data = {
    'Metric': ['Revenue', 'Gross Profit', 'Profit Margin', 'Total Orders', 'New Orders', 'Repeat Order Rate', 'Avg Order Value', 'New Customers', 'Marketing ROAS'],
    'Current Period': [
        f"${current_kpis['revenue']:,.0f}",
        f"${current_kpis['profit']:,.0f}",
        f"{profit_margin:.1f}%",
        f"{current_kpis['orders']:,}",
        f"{current_kpis['new_orders']:,}",
        f"{repeat_order_rate:.1f}%",
        f"${avg_order_value:.0f}",
        f"{current_kpis['customers']:,}",
        f"{roas:.1f}x"
    ],
    'Change': [
        f"{revenue_trend:+.1f}%",
        f"{calculate_change(current_kpis['profit'], comparison_kpis['profit']):+.1f}%",
        f"{profit_margin - (comparison_kpis['profit']/comparison_kpis['revenue']*100 if comparison_kpis['revenue'] > 0 else 0):+.1f}pp",
        f"{calculate_change(current_kpis['orders'], comparison_kpis['orders']):+.1f}%",
        f"{calculate_change(current_kpis['new_orders'], comparison_kpis['new_orders']):+.1f}%",
        f"{repeat_order_rate - ((comparison_kpis['orders'] - comparison_kpis['new_orders']) / comparison_kpis['orders'] * 100 if comparison_kpis['orders'] > 0 else 0):+.1f}pp",
        f"{calculate_change(avg_order_value, comparison_kpis['revenue']/comparison_kpis['orders'] if comparison_kpis['orders'] > 0 else 0):+.1f}%",
        f"{calculate_change(current_kpis['customers'], comparison_kpis['customers']):+.1f}%",
        f"{calculate_change(roas, comp_roas):+.1f}%"
    ]
}

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown(f"*Dashboard updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data period: {date_diff} days*")
