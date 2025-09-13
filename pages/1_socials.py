import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Social Media Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: -5px;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and combine all CSV files from local paths"""
    try:
        # Assuming your CSVs are in a "data" folder at project root
        paths = {
            'Facebook': os.path.join("data", "Facebook_clean.csv"),
            'Google': os.path.join("data", "Google_clean.csv"),
            'TikTok': os.path.join("data", "TikTok_clean.csv"),
        }

        dataframes = []
        for platform, path in paths.items():
            if not os.path.exists(path):
                st.error(f"Missing file: {path}")
                return None
            df = pd.read_csv(path)
            dataframes.append(df)

        # Combine all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)

        # Convert date column to datetime
        combined_df['date'] = pd.to_datetime(combined_df['date'])

        # Convert string columns to numeric
        numeric_cols = ['impression', 'clicks', 'spend', 'attributed revenue']
        for col in numeric_cols:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

        # Fill NaN with 0
        combined_df = combined_df.fillna(0)

        return combined_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def calculate_kpis(df):
    """Calculate key performance indicators"""
    total_impressions = df['impression'].sum()
    total_clicks = df['clicks'].sum()
    total_revenue = df['attributed revenue'].sum()
    total_spend = df['spend'].sum()

    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    roas = (total_revenue / total_spend) if total_spend > 0 else 0
    cpc = (total_spend / total_clicks) if total_clicks > 0 else 0

    return {
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_revenue': total_revenue,
        'total_spend': total_spend,
        'ctr': ctr,
        'roas': roas,
        'cpc': cpc
    }


def format_number(num):
    """Format numbers for display"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:,.0f}"


def main():
    st.markdown('<h1 class="main-header">📊 Social Media Analytics Dashboard</h1>', unsafe_allow_html=True)

    df = load_data()
    if df is None:
        return

    # Sidebar filters
    st.sidebar.header("🔍 Filters")

    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    platforms = ['All'] + sorted(df['platform'].unique().tolist())
    selected_platforms = st.sidebar.multiselect("Select Platforms", platforms, default=['All'])

    tactics = ['All'] + sorted(df['tactic'].unique().tolist())
    selected_tactics = st.sidebar.multiselect("Select Tactics", tactics, default=['All'])

    states = ['All'] + sorted(df['state'].unique().tolist())
    selected_states = st.sidebar.multiselect("Select States", states, default=['All'])

    # Filtering
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
    else:
        filtered_df = df.copy()

    if 'All' not in selected_platforms and selected_platforms:
        filtered_df = filtered_df[filtered_df['platform'].isin(selected_platforms)]

    if 'All' not in selected_tactics and selected_tactics:
        filtered_df = filtered_df[filtered_df['tactic'].isin(selected_tactics)]

    if 'All' not in selected_states and selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

    # KPIs
    kpis = calculate_kpis(filtered_df)

    st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">{format_number(kpis['total_impressions'])}</div>
            <div class="kpi-label">Total Impressions</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">{kpis['ctr']:.2f}%</div>
            <div class="kpi-label">Click-Through Rate</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">{format_number(kpis['total_clicks'])}</div>
            <div class="kpi-label">Total Clicks</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">{kpis['roas']:.2f}x</div>
            <div class="kpi-label">Return on Ad Spend</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">${format_number(kpis['total_revenue'])}</div>
            <div class="kpi-label">Total Revenue</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">${kpis['cpc']:.2f}</div>
            <div class="kpi-label">Cost Per Click</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-value">${format_number(kpis['total_spend'])}</div>
            <div class="kpi-label">Total Ad Spend</div>
        </div>""", unsafe_allow_html=True)

    # (Keep all charts + raw data table the same as before …)

    st.markdown("---")
    st.markdown("*Dashboard last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


if __name__ == "__main__":
    main()
