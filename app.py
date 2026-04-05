import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Конфигурация страницы
st.set_page_config(page_title="JRiverbend Terminal", layout="wide", initial_sidebar_state="collapsed")

# Стилизация (Dark Theme)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- ДАННЫЕ (Эмуляция + API) ---
def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,the-graph,ethereum&vs_currencies=usd&include_24hr_change=true"
        return requests.get(url).json()
    except:
        return {"bitcoin": {"usd": 68450, "usd_24h_change": 1.2}, "the-graph": {"usd": 0.023, "usd_24h_change": -0.5}}

# --- ИНТЕРФЕЙС ---
st.title("🛡️ Crypto Strategy Terminal | 2026 Edition")
st.caption(f"User: JRiverbend | Hardware: MacBook Air 2017 (Cloud Optimized) | Date: {datetime.now().strftime('%d.%m.%Y')}")

data = get_crypto_prices()

# Ряд 1: Главные метрики
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bitcoin (BTC)", f"${data['bitcoin']['usd']:,}", f"{data['bitcoin']['usd_24h_change']:.2f}%")
with col2:
    st.metric("The Graph (GRT)", f"${data['the-graph']['usd']:.4f}", f"{data['the-graph']['usd_24h_change']:.2f}%")
with col3:
    st.metric("Stablecoin Liquidity", "High (Inflow)", "🟢")

st.divider()

# Ряд 2: Аналитика спроса и китов
left, right = st.columns(2)

with left:
    st.subheader("🐋 Whale Activity (April 2026)")
    st.code("""
    [ALERT] 1,420 BTC ($96M) moved to Cold Storage
    [INFO] Exchange Reserves: Multi-year Low
    [SENTIMENT] Accumulation Trend: 0.68 (Strong)
    """, language="bash")
    
    st.write("### Institutional Demand (ETF)")
    chart_data = pd.DataFrame({"Days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "Inflow ($M)": [120, 340, 210, 450, 310]})
    st.line_chart(chart_data.set_index("Days"))

with right:
    st.subheader("🌐 Layer 2 & Utility")
    l2_data = pd.DataFrame({
        "Network": ["Arbitrum", "Base", "Optimism"],
        "Daily Fees": ["$42k", "$108k", "$29k"],
        "Efficiency": ["High", "Very High", "Stable"]
    })
    st.dataframe(l2_data, use_container_width=True)
    
    st.info("**GRT Strategy:** Staking rewards (8.5% APY) cover current inflation. Target: $0.06 (Conservative).")

# Футер
if st.button("🔄 Force Refresh On-Chain Data"):
    st.rerun()
