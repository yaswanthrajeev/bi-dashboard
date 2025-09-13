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

    # Trend Charts
    st.markdown('<div class="section-header">📈 Performance Trends</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily spend vs revenue trend
        daily_trends = filtered_df.groupby('date').agg({
            'spend': 'sum',
            'attributed revenue': 'sum'
        }).reset_index()
        
        fig_spend_revenue = go.Figure()
        fig_spend_revenue.add_trace(go.Scatter(
            x=daily_trends['date'],
            y=daily_trends['spend'],
            mode='lines+markers',
            name='Ad Spend',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=6)
        ))
        fig_spend_revenue.add_trace(go.Scatter(
            x=daily_trends['date'],
            y=daily_trends['attributed revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#4ecdc4', width=3),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig_spend_revenue.update_layout(
            title='Daily Spend vs Revenue Trends',
            xaxis_title='Date',
            yaxis=dict(title='Ad Spend ($)', side='left', color='#ff6b6b'),
            yaxis2=dict(title='Revenue ($)', side='right', overlaying='y', color='#4ecdc4'),
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig_spend_revenue, use_container_width=True)
    
    with col2:
        # Daily impressions vs clicks trend
        daily_engagement = filtered_df.groupby('date').agg({
            'impression': 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        fig_engagement = go.Figure()
        fig_engagement.add_trace(go.Scatter(
            x=daily_engagement['date'],
            y=daily_engagement['impression'],
            mode='lines+markers',
            name='Impressions',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        fig_engagement.add_trace(go.Scatter(
            x=daily_engagement['date'],
            y=daily_engagement['clicks'],
            mode='lines+markers',
            name='Clicks',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=6),
            yaxis='y2'
        ))
        
        fig_engagement.update_layout(
            title='Daily Impressions vs Clicks',
            xaxis_title='Date',
            yaxis=dict(title='Impressions', side='left', color='#1f77b4'),
            yaxis2=dict(title='Clicks', side='right', overlaying='y', color='#ff7f0e'),
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Platform Comparison Charts
    st.markdown('<div class="section-header">🏆 Platform Performance</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by platform bar chart
        platform_revenue = filtered_df.groupby('platform')['attributed revenue'].sum().reset_index()
        platform_revenue = platform_revenue.sort_values('attributed revenue', ascending=True)
        
        fig_platform_revenue = px.bar(
            platform_revenue,
            x='attributed revenue',
            y='platform',
            orientation='h',
            title='Revenue by Platform',
            color='attributed revenue',
            color_continuous_scale='viridis',
            text='attributed revenue'
        )
        fig_platform_revenue.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig_platform_revenue.update_layout(
            height=400,
            template='plotly_white',
            showlegend=False
        )
        st.plotly_chart(fig_platform_revenue, use_container_width=True)
    
    with col2:
        # Spend distribution pie chart
        platform_spend = filtered_df.groupby('platform')['spend'].sum().reset_index()
        
        fig_spend_pie = px.pie(
            platform_spend,
            values='spend',
            names='platform',
            title='Ad Spend Distribution by Platform',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_spend_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_spend_pie.update_layout(height=400)
        st.plotly_chart(fig_spend_pie, use_container_width=True)
    
    # Tactic Performance
    st.markdown('<div class="section-header">🎯 Tactic Performance</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ROAS by tactic
        tactic_performance = filtered_df.groupby('tactic').agg({
            'attributed revenue': 'sum',
            'spend': 'sum'
        }).reset_index()
        tactic_performance['roas'] = tactic_performance['attributed revenue'] / tactic_performance['spend']
        tactic_performance = tactic_performance.sort_values('roas', ascending=True)
        
        fig_tactic_roas = px.bar(
            tactic_performance,
            x='roas',
            y='tactic',
            orientation='h',
            title='ROAS by Tactic',
            color='roas',
            color_continuous_scale='RdYlGn',
            text='roas'
        )
        fig_tactic_roas.update_traces(texttemplate='%{text:.2f}x', textposition='outside')
        fig_tactic_roas.update_layout(
            height=400,
            template='plotly_white',
            showlegend=False
        )
        st.plotly_chart(fig_tactic_roas, use_container_width=True)
    
    with col2:
        # CTR by tactic
        tactic_ctr = filtered_df.groupby('tactic').agg({
            'clicks': 'sum',
            'impression': 'sum'
        }).reset_index()
        tactic_ctr['ctr'] = (tactic_ctr['clicks'] / tactic_ctr['impression']) * 100
        tactic_ctr = tactic_ctr.sort_values('ctr', ascending=False)
        
        fig_tactic_ctr = px.bar(
            tactic_ctr,
            x='tactic',
            y='ctr',
            title='Click-Through Rate by Tactic',
            color='ctr',
            color_continuous_scale='blues',
            text='ctr'
        )
        fig_tactic_ctr.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_tactic_ctr.update_layout(
            height=400,
            template='plotly_white',
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_tactic_ctr, use_container_width=True)
    
    # State Performance
    st.markdown('<div class="section-header">🗺️ Geographic Performance</div>', unsafe_allow_html=True)
    
    state_performance = filtered_df.groupby('state').agg({
        'attributed revenue': 'sum',
        'spend': 'sum',
        'clicks': 'sum',
        'impression': 'sum'
    }).reset_index()
    state_performance['roas'] = state_performance['attributed revenue'] / state_performance['spend']
    state_performance['ctr'] = (state_performance['clicks'] / state_performance['impression']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by state
        state_revenue = state_performance.sort_values('attributed revenue', ascending=False).head(10)
        fig_state_revenue = px.bar(
            state_revenue,
            x='state',
            y='attributed revenue',
            title='Top 10 States by Revenue',
            color='attributed revenue',
            color_continuous_scale='viridis'
        )
        fig_state_revenue.update_layout(height=400, template='plotly_white', showlegend=False)
        st.plotly_chart(fig_state_revenue, use_container_width=True)
    
    with col2:
        # ROAS by state
        state_roas = state_performance.sort_values('roas', ascending=False).head(10)
        fig_state_roas = px.bar(
            state_roas,
            x='state',
            y='roas',
            title='Top 10 States by ROAS',
            color='roas',
            color_continuous_scale='RdYlGn'
        )
        fig_state_roas.update_layout(height=400, template='plotly_white', showlegend=False)
        st.plotly_chart(fig_state_roas, use_container_width=True)
    
    st.markdown('<div class="section-header">📋 Raw Data</div>', unsafe_allow_html=True)
    
    with st.expander("View Filtered Data", expanded=False):
        st.write(f"**Total Records:** {len(filtered_df):,}")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Daily Spend", f"${filtered_df.groupby('date')['spend'].sum().mean():,.2f}")
        with col2:
            st.metric("Avg Daily Revenue", f"${filtered_df.groupby('date')['attributed revenue'].sum().mean():,.2f}")
        with col3:
            st.metric("Avg Daily ROAS", f"{(filtered_df['attributed revenue'].sum() / filtered_df['spend'].sum()):.2f}x")
        
        # Data table with download option
        st.dataframe(
            filtered_df.sort_values('date', ascending=False),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"social_media_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    st.markdown("---")
    st.markdown("*Dashboard last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


if __name__ == "__main__":
    main()
