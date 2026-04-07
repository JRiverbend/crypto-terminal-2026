import streamlit as st
import requests
import pandas as pd
import feedparser
from datetime import datetime

# Конфигурация страницы
st.set_page_config(page_title="JRiverbend Terminal", layout="wide", initial_sidebar_state="collapsed")

# Стилизация (Dark Theme + Custom Fonts)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .news-card { background-color: #161b22; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #238636; }
    .news-title { color: #58a6ff; font-weight: bold; text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)

# --- ФУНКЦИИ ДАННЫХ ---

def get_crypto_prices():
    fallback = {"bitcoin": {"usd": 69120.0, "usd_24h_change": 0.5}, "the-graph": {"usd": 0.2340, "usd_24h_change": -0.2}}
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,the-graph&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url, timeout=5).json()
        return data if "bitcoin" in data else fallback
    except:
        return fallback

def get_blockchain_news():
    feeds = [
        "https://cointelegraph.com/rss",
        "https://decrypt.co/feed"
    ]
    all_entries = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries[:5])
        except:
            continue
    return all_entries[:8]

def get_mempool_alerts():
    """Получение реальных последних транзакций через Mempool.space API."""
    try:
        # Получаем последние транзакции в мемпуле
        res = requests.get("https://mempool.space/api/mempool/recent", timeout=5).json()
        alerts = []
        for tx in res[:5]: # Берем 5 последних
            btc_val = tx['value'] / 10**8
            txid_short = f"{tx['txid'][:6]}...{tx['txid'][-6:]}"
            # Формируем строку алерта
            alerts.append(f"⚡ **{btc_val:.2f} BTC** | TX: `{txid_short}`")
        return alerts
    except:
        return ["📡 Ожидание данных из мемпула..."]

# --- ИНТЕРФЕЙС ---

st.title("🛡️ Crypto Strategy Terminal | 2026 Edition")
st.caption(f"User: JRiverbend | Netanya HQ | Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

prices = get_crypto_prices()

# Ряд 1: Метрики
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Bitcoin (BTC)", f"${prices['bitcoin']['usd']:,}", f"{prices['bitcoin']['usd_24h_change']:.2f}%")
with col2:
    st.metric("The Graph (GRT)", f"${prices['the-graph']['usd']:.4f}", f"{prices['the-graph']['usd_24h_change']:.2f}%")
with col3:
    st.metric("Whale Sentiment", "Accumulation", "0.68")
with col4:
    st.metric("Stablecoin Flow", "Inflow", "🟢")

st.divider()

# Ряд 2: Основной контент
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🐋 Market Intelligence & Whales")
    
    tab1, tab2 = st.tabs(["Live Mempool Alerts", "ETF Inflows"])
    
    with tab1:
        st.write("### Recent Network Activity (Real-time)")
        mempool_data = get_mempool_alerts()
        for alert in mempool_data:
            st.write(alert)
        st.caption("Данные обновляются при каждом обновлении страницы")
        
    with tab2:
        chart_data = pd.DataFrame({"Day": ["1", "2", "3", "4", "5"], "Net Inflow ($M)": [140, -50, 310, 420, 290]})
        st.bar_chart(chart_data.set_index("Day"))

    st.subheader("🌐 L2 Network Efficiency")
    l2_df = pd.DataFrame({
        "Network": ["Base", "Arbitrum", "Optimism"],
        "TPS": [85.4, 42.1, 18.9],
        "Avg Fee": ["$0.001", "$0.02", "$0.01"]
    })
    st.table(l2_df)

with right_col:
    st.subheader("📰 Blockchain News Feed")
    news = get_blockchain_news()
    
    if not news:
        st.write("Новости временно недоступны.")
    else:
        for entry in news:
            st.markdown(f"""
            <div class="news-card">
                <a class="news-title" href="{entry.link}" target="_blank">{entry.title}</a><br>
                <small style="color: #8b949e;">{entry.get('published', 'Сегодня')}</small>
            </div>
            """, unsafe_allow_html=True)

# Футер (Сайдбар)
st.sidebar.button("🔄 Refresh System", on_click=st.rerun)
st.sidebar.write(f"**Node Status:** Online")
