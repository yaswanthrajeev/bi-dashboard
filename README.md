# Executive Business Dashboard

A comprehensive Streamlit-based business intelligence dashboard designed for executives and decision-makers to analyze business performance, marketing effectiveness, and key operational metrics.

## 🚀 Features

### Core Business Analytics
- **Revenue & Profitability Tracking** - Monitor total revenue, gross profit, and profit margins
- **Order Analysis** - Track total orders, new orders, and repeat order patterns
- **Customer Acquisition** - Analyze new customer acquisition trends
- **Marketing ROI** - Calculate and track Return on Ad Spend (ROAS) across platforms

### Interactive Visualizations
- **KPI Cards** - Gradient-styled cards with trend indicators and period comparisons
- **Revenue Trends** - Interactive line charts with zoom and pan capabilities
- **Orders Analysis** - Total vs new orders with repeat order visualization
- **Platform Performance** - ROAS comparison across Facebook, Google, and TikTok
- **Cost Structure** - Revenue breakdown showing COGS vs profit

### Advanced Filtering & Analysis
- **Date Range Selection** - Custom date ranges with quick filters (30/90 days, 6 months, 1 year)
- **Time Aggregation** - View data by daily, weekly, or monthly periods
- **Period Comparison** - Compare to previous period or same period last year
- **Executive Summary** - Comprehensive metrics table with change indicators

## 📊 Data Requirements

The dashboard expects four CSV files in the `data/` directory:

### Business Data (`data/business.csv`)
\`\`\`
date, # of orders, # of new orders, new customers, total revenue, gross profit, COGS
\`\`\`

### Marketing Platform Data
- `data/Facebook_clean.csv`
- `data/Google_clean.csv` 
- `data/TikTok_clean.csv`

Each with schema:
\`\`\`
date, tactic, state, campaign, impression, clicks, spend, attributed revenue, platform
\`\`\`

## 🛠️ Installation & Setup

1. **Install Dependencies**
\`\`\`bash
pip install requirements.txt
\`\`\`


3. **Run Dashboard**
\`\`\`bash
streamlit run compact_executive_dashboard.py
\`\`\`

## 📈 Key Metrics Explained

### ROAS (Return on Ad Spend)
**Formula**: `Attributed Revenue ÷ Marketing Spend`
- **3.0x+** = Target performance
- **4.0x+** = Outstanding performance
- **Below 2.0x** = Needs optimization

### Profit Margin
**Formula**: `(Gross Profit ÷ Total Revenue) × 100`

### Repeat Order Rate
**Formula**: `((Total Orders - New Orders) ÷ Total Orders) × 100`

## 🎯 Business Intelligence Focus

This dashboard is designed with executive decision-making in mind:

- **Strategic KPIs** - Focus on metrics that drive business decisions
- **Marketing Efficiency** - Understand which channels deliver the best ROI
- **Customer Behavior** - Track acquisition vs retention patterns
- **Profitability Analysis** - Monitor margins and cost structures
- **Trend Analysis** - Identify patterns and seasonal variations




## 🚨 Troubleshooting

- Ensure all CSV files have the correct column names and date formats
- Check that numeric columns don't contain text or special characters
- Verify date ranges don't exceed available data periods
- For performance issues, consider filtering to smaller date ranges

---

*Built with Streamlit, Plotly, and Pandas for professional business intelligence.*
