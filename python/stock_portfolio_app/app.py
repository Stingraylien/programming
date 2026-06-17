import streamlit as st
import pandas as pd
import plotly.express as px
import utils

# Page Config
st.set_page_config(
    page_title="投資組合管理",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
with open('stock_portfolio_app/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Sidebar: Add Transaction ---
st.sidebar.title("功能選單")

with st.sidebar.form("add_transaction_form"):
    st.subheader("新增 / 更新資產")
    
    ticker_input = st.text_input("股票代號 (Ticker)", placeholder="例如: 2330.TW 或 NVDA").upper().strip()
    # Default to TW if no suffix? No, let user be explicit or we can auto-detect later.
    
    col1, col2 = st.columns(2)
    with col1:
        # Step: Allow decimal for fractional shares
        quantity_input = st.number_input("股數 (可小數)", min_value=-100000.0, max_value=100000.0, step=0.01, format="%.2f")
    with col2:
        price_input = st.number_input("單位成本", min_value=0.0, step=0.01, format="%.2f")
    
    currency_input = st.selectbox("幣別", ["TWD", "USD"], index=0)
    
    submitted = st.form_submit_button("送出交易")
    if submitted:
        if ticker_input and quantity_input != 0:
            utils.add_transaction(ticker_input, quantity_input, price_input, currency_input)
            st.sidebar.success(f"已新增 {ticker_input}")
            st.rerun() # Refresh to show new data
        else:
            st.sidebar.error("請輸入有效的代號與股數")

st.sidebar.markdown("---")
if st.sidebar.button("刷新數據"):
    st.rerun()

# --- Main Dashboard ---

st.title("我的投資儀表板")

# 1. Load Data
portfolio = utils.load_portfolio()

# 2. Fetch Market Data
# Show a spinner while loading
with st.spinner('更新市場數據中...'):
    market_data, fx_rate, names, success_flag = utils.get_market_data(portfolio)
    
    # Check if we should warn the user
    if success_flag is False: 
         st.error("⚠️ 無法獲取最新股價 (Yahoo Finance連線限制)。目前顯示的數據可能不準確。")
         st.caption("原因: 短時間內請求過多，IP 被暫時封鎖。請稍後再試。")
    
    enriched_portfolio, total_value, total_cost = utils.calculate_portfolio_value(portfolio, market_data, fx_rate, names)

# 3. Top Metrics
# Calculate Total P/L
total_pl = total_value - total_cost
total_pl_percent = (total_pl / total_cost * 100) if total_cost != 0 else 0.0

col_m1, col_m2, col_m3 = st.columns(3)

def format_currency(val, currency="TWD"):
    return f"${val:,.0f}" if currency == "TWD" else f"${val:,.2f}"

with col_m1:
    st.metric("總淨值 (TWD)", format_currency(total_value), delta=None)

with col_m2:
    st.metric("總損益 (TWD)", format_currency(total_pl), f"{total_pl_percent:.2f}%")

with col_m3:
    st.metric("美金匯率 (USD/TWD)", f"{fx_rate:.2f}")

st.markdown("---")

# 4. Charts & Details
if not enriched_portfolio:
    st.info("您的投資組合目前為空，請從左側側邊欄新增交易。")
else:
    col_chart, col_table = st.columns([1, 2])
    
    df = pd.DataFrame(enriched_portfolio)
    
    with col_chart:
        st.subheader("資產配置佔比")
        # Pie Chart by Ticker
        # Handle negative values? Pie charts don't like negatives. 
        # For allocation, we usually use Market Value.
        valid_alloc = df[df['market_value_twd'] > 0]
        if not valid_alloc.empty:
            fig = px.pie(valid_alloc, values='market_value_twd', names='ticker', hole=0.4)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="white",
                showlegend=False,
                 margin=dict(t=0, b=0, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("無可顯示的持股數據。")

    with col_table:
        st.subheader("詳細持股清單")
        
        # Format for display
        display_df = df.copy()
        
        # Rename columns for prettier display
        # Add 'name' to the selection
        display_df = display_df[['ticker', 'name', 'quantity', 'avg_cost', 'current_price', 'market_value_twd', 'pl_twd', 'pl_percent', 'currency']]
        
        # Apply some formatting
        # Streamlit generic dataframe is okay, but we can do better with st.dataframe column config in newer versions
        # Or just round them
        display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:,.2f}")
        display_df['avg_cost'] = display_df['avg_cost'].apply(lambda x: f"{x:,.2f}")
        display_df['current_price'] = display_df['current_price'].apply(lambda x: f"{x:,.2f}")
        display_df['market_value_twd'] = display_df['market_value_twd'].apply(lambda x: f"{x:,.0f}")
        display_df['pl_twd'] = display_df['pl_twd'].apply(lambda x: f"{x:,.0f}")
        display_df['pl_percent'] = display_df['pl_percent'].apply(lambda x: f"{x:,.2f}%")
        
        st.dataframe(
            display_df,
            column_config={
                "ticker": "代號",
                "name": "股票名稱",
                "quantity": "股數",
                "avg_cost": "平均成本",
                "current_price": "現價",
                "market_value_twd": "市值 (TWD)",
                "pl_twd": "損益 (TWD)",
                "pl_percent": "報酬率 %",
                "currency": "幣別"
            },
            hide_index=True,
            use_container_width=True
        )

# Footer / Debug info
# st.write(f"Refreshed at: {datetime.now().strftime('%H:%M:%S')}")
