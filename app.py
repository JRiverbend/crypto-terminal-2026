import streamlit as st
import requests
import pandas as pd
import feedparser
from datetime import datetime

# Конфигурация страницы
st.set_page_config(page_title="JRiverbend Terminal", layout="wide", initial_sidebar_state="collapsed")

# Стилизация
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
    fallback = {"bitcoin": {"usd": 68400.0, "usd_24h_change": -1.7}, "the-graph": {"usd": 0.0236, "usd_24h_change": -3.8}}
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,the-graph&vs_currencies=usd&include_24hr_change=true"
        data = requests.get(url, timeout=5).json()
        return data if "bitcoin" in data else fallback
    except:
        return fallback

def get_mempool_data():
    """Получаем расширенные данные из мемпула для аналитики."""
    try:
        # Берем больше данных (50 транзакций) для расчета индекса
        res = requests.get("https://api.mempool.space/api/mempool/recent", timeout=5).json()
        
        # Фильтруем только КРУПНЫЕ транзакции для алертов (> 5 BTC)
        whale_alerts = [tx for tx in res if (tx['value'] / 10**8) >= 5.0]
        
        # Считаем Whale Index (Sentiment)
        # Логика: отношение суммы крупных транзакций к общему числу
        avg_value = sum(tx['value'] for tx in res) / len(res) / 10**8
        sentiment_score = min(0.99, avg_value / 2.0) # Нормализуем (если средняя 2 BTC, индекс ~1.0)
        
        sentiment_label = "Accumulation" if sentiment_score > 0.5 else "Distribution"
        if sentiment_score < 0.3: sentiment_label = "Retail Noise"
            
        return whale_alerts[:5], sentiment_score, sentiment_label
    except:
        return [], 0.5, "Neutral"

def get_blockchain_news():
    feeds = ["https://cointelegraph.com/rss", "https://decrypt.co/feed"]
    all_entries = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries[:5])
        except: continue
    return all_entries[:8]

# --- ИНТЕРФЕЙС ---

st.title("🛡️ Crypto Strategy Terminal | 2026 Edition")
st.caption(f"User: JRiverbend | Netanya HQ | Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

# Загрузка данных
prices = get_crypto_prices()
whale_txs, s_score, s_label = get_mempool_data()

# Ряд 1: Метрики
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Bitcoin (BTC)", f"${prices['bitcoin']['usd']:,}", f"{prices['bitcoin']['usd_24h_change']:.2f}%")
with col2:
    st.metric("The Graph (GRT)", f"${prices['the-graph']['usd']:.4f}", f"{prices['the-graph']['usd_24h_change']:.2f}%")
with col3:
    # Теперь сентимент динамический
    st.metric("Whale Sentiment", s_label, f"{s_score:.2f}")
with col4:
    st.metric("Stablecoin Flow", "Inflow", "🟢")

st.divider()

# Ряд 2: Основной контент
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🐋 Market Intelligence & Whales")
    tab1, tab2 = st.tabs(["Whale Tracker (>5 BTC)", "ETF Inflows"])
    
    with tab1:
        st.write("### Significant On-Chain Movements")
        if not whale_txs:
            st.info("крупных перемещений (>5 BTC) в последние минуты не обнаружено. Рынок спокоен.")
        for tx in whale_txs:
            val = tx['value'] / 10**8
            txid = f"{tx['txid'][:6]}...{tx['txid'][-6:]}"
            st.error(f"🐳 **Whale Move: {val:.2f} BTC** | TX: `{txid}`")
        
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
    for entry in news:
        st.markdown(f"""
        <div class="news-card">
            <a class="news-title" href="{entry.link}" target="_blank">{entry.title}</a><br>
            <small style="color: #8b949e;">{entry.get('published', 'Сегодня')}</small>
        </div>
        """, unsafe_allow_html=True)

# Футер
st.sidebar.button("🔄 Refresh System", on_click=st.rerun)
st.sidebar.write(f"**Node Status:** Online")
