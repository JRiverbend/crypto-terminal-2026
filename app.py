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

# --- ФУНКЦИИ ДАННЫХ (OKX Edition) ---

def get_price_okx(inst_id):
    """Получение данных тикера через OKX V5 API."""
    try:
        # inst_id должен быть в формате BTC-USDT или GRT-USDT
        url = f"https://www.okx.com/api/v5/market/ticker?instId={inst_id}"
        res = requests.get(url, timeout=5).json()
        if res['code'] == '0':
            data = res['data'][0]
            last = float(data['last'])
            open_24h = float(data['open24h'])
            # Считаем процентное изменение
            change = ((last - open_24h) / open_24h) * 100
            return {"price": last, "change": change}
        return None
    except:
        return None

def get_crypto_data():
    btc = get_price_okx("BTC-USDT")
    grt = get_price_okx("GRT-USDT")
    
    # Резервные данные на случай сбоя API
    return {
        "bitcoin": btc if btc else {"price": 68401.0, "change": -1.78},
        "the-graph": grt if grt else {"price": 0.0236, "change": -3.89}
    }

def get_mempool_data():
    try:
        res = requests.get("https://api.mempool.space/api/mempool/recent", timeout=5).json()
        # Только транзакции более 5 BTC
        whale_alerts = [tx for tx in res if (tx['value'] / 10**8) >= 5.0]
        # Расчет сентимента на основе среднего объема
        avg_value = sum(tx['value'] for tx in res) / len(res) / 10**8
        sentiment_score = min(0.99, avg_value / 2.0)
        
        sentiment_label = "Accumulation" if sentiment_score > 0.5 else "Distribution"
        if sentiment_score < 0.3: sentiment_label = "Retail Noise"
            
        return whale_alerts[:10], sentiment_score, sentiment_label
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
    return all_entries[:10]

# --- ИНТЕРФЕЙС ---

st.title("🛡️ Crypto Strategy Terminal")
st.caption(f"User: JRiverbend | Netanya HQ | Source: OKX API | {datetime.now().strftime('%H:%M:%S')}")

# Загрузка данных
prices = get_crypto_data()
whale_txs, s_score, s_label = get_mempool_data()

# Ряд 1: Метрики
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bitcoin (BTC)", f"${prices['bitcoin']['price']:,}", f"{prices['bitcoin']['change']:.2f}%")
with col2:
    st.metric("The Graph (GRT)", f"${prices['the-graph']['price']:.4f}", f"{prices['the-graph']['change']:.2f}%")
with col3:
    st.metric("Whale Sentiment", s_label, f"{s_score:.2f}")

st.divider()

# Ряд 2: Контент (Мемпул и Новости)
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("🐋 Live Whale Tracker (>5 BTC)")
    if not whale_txs:
        st.info("Крупных движений (>5 BTC) в мемпуле не обнаружено.")
    else:
        for tx in whale_txs:
            val = tx['value'] / 10**8
            txid = f"{tx['txid'][:8]}...{tx['txid'][-8:]}"
            st.error(f"🐳 **Move: {val:.2f} BTC** | TX: `{txid}`")
    
    st.caption("Данные из Mempool.space. Обновляются вручную.")

with right_col:
    st.subheader("📰 Market Intelligence")
    news = get_blockchain_news()
    if not news:
        st.write("Лента новостей пуста.")
    for entry in news:
        st.markdown(f"""
        <div class="news-card">
            <a class="news-title" href="{entry.link}" target="_blank">{entry.title}</a><br>
            <small style="color: #8b949e;">{entry.get('published', 'Сегодня')}</small>
        </div>
        """, unsafe_allow_html=True)

# Сайдбар
st.sidebar.button("🔄 Refresh Terminal", on_click=st.rerun)
st.sidebar.write("**Status:** Node Online")
