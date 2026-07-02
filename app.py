import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Superstore Sales & Profit Analytics")
st.markdown("Interact with the sidebar filters to explore the dataset.")

# 2. Load Data (with caching for performance)
@st.cache_data
def load_data():
    # Reads superstore.csv from the root directory
    df = pd.read_csv("superstore.csv")
    
    # Convert date columns to datetime objects just in case
    if 'Order.Date' in df.columns:
        df['Order.Date'] = pd.to_datetime(df['Order.Date'])
    return df

try:
    df = load_data()

    # 3. Sidebar Filters
    st.sidebar.header("Filter Data")
    
    # Market Filter
    markets = sorted(df['Market'].unique().tolist())
    selected_market = st.sidebar.multiselect("Select Market", options=markets, default=markets)
    
    # Category Filter
    categories = sorted(df['Category'].unique().tolist())
    selected_category = st.sidebar.multiselect("Select Category", options=categories, default=categories)

    # Filter the dataframe based on selection
    filtered_df = df[
        (df['Market'].isin(selected_market)) & 
        (df['Category'].isin(selected_category))
    ]

    # 4. KPI Top Cards
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()
    total_orders = filtered_df['Order.ID'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Sales", value=f"${total_sales:,.2f}")
    col2.metric(label="Total Profit", value=f"${total_profit:,.2f}", delta=f"{(total_profit/total_sales)*100:.1f}% Margin" if total_sales > 0 else "0%")
    col3.metric(label="Unique Orders", value=f"{total_orders:,}")

    st.markdown("---")

    # 5. Visualizations
    left_chart_col, right_chart_col = st.columns(2)

    with left_chart_col:
        st.subheader("Sales by Sub-Category")
        sub_cat_sales = filtered_df.groupby('Sub.Category')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=True)
        fig_bar = px.bar(
            sub_cat_sales, 
            x='Sales', 
            y='Sub.Category', 
            orientation='h',
            title="Revenue per Sub-Category",
            labels={'Sales': 'Total Sales ($)', 'Sub.Category': 'Sub-Category'},
            color='Sales',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with right_chart_col:
        st.subheader("Profit vs Sales by Segment")
        fig_scatter = px.scatter(
            filtered_df,
            x='Sales',
            y='Profit',
            color='Segment',
            hover_data=['Product.Name', 'Customer.Name'],
            title="Transaction Level Sales vs Profitability",
            labels={'Sales': 'Sales ($)', 'Profit': 'Profit ($)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # 6. Data Table View
    st.markdown("---")
    st.subheader("Filtered Data Preview")
    st.dataframe(
        filtered_df[['Order.ID', 'Order.Date', 'Customer.Name', 'Market', 'Category', 'Sub.Category', 'Sales', 'Profit']], 
        use_container_width=True,
        hide_index=True
    )

except FileNotFoundError:
    st.error("Error: 'superstore.csv' file not found. Please make sure it's in the same directory as this app.py script.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")