import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
import feedparser
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Letta Earth | Agribusiness Intelligence", 
    layout="wide", 
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR WIX EMBEDDING ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1rem;}
            .news-card {
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
                border-left: 5px solid #4a90e2;
            }
            .news-title {font-size: 18px; font-weight: bold; color: #333;}
            .news-meta {font-size: 12px; color: #666;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- NEWS ENGINE (RSS) ---
@st.cache_data(ttl=3600) # Cache news for 1 hour to prevent spamming Google
def fetch_news(query, region='Global'):
    """
    Fetches news from Google News RSS based on query and region.
    """
    # 1. Define URL based on Region
    if region == 'Turkey':
        base_url = "https://news.google.com/rss/search?q={}&hl=tr&gl=TR&ceid=TR:tr"
        # Smart Translation for Local Context
        translations = {
            "Hazelnuts": "Fındık fiyatları Giresun Ordu",
            "Cocoa": "Kakao fiyatları",
            "Avocados": "Avokado üretimi",
            "Coffee": "Kahve piyasası",
            "Wheat": "Buğday fiyatları TMO",
            "Corn": "Mısır hasadı"
        }
        search_term = translations.get(query, query)
    else:
        base_url = "https://news.google.com/rss/search?q={}+commodity+market&hl=en-US&gl=US&ceid=US:en"
        search_term = query

    # 2. Fetch and Parse
    feed_url = base_url.format(search_term.replace(" ", "%20"))
    feed = feedparser.parse(feed_url)
    
    news_items = []
    for entry in feed.entries[:10]: # Top 10 stories
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'source': entry.source.title if 'source' in entry else 'Google News'
        })
    return news_items

# --- MOCK DATA ENGINE (EXISTING) ---
def get_listed_commodities():
    dates = pd.date_range(start="2024-01-01", end="2025-05-20", freq="D")
    df = pd.DataFrame(index=dates)
    df['Cocoa ($/MT)'] = np.linspace(4000, 9000, len(dates)) + np.random.normal(0, 100, len(dates))
    df['Wheat ($/Bushel)'] = np.linspace(600, 550, len(dates)) + np.random.normal(0, 10, len(dates))
    return df

def get_hazelnut_data():
    dates = pd.date_range(start="2024-09-01", end="2025-05-20", freq="W")
    prices = []
    base_price = 100 
    for d in dates:
        if d.month >= 4 and d.year == 2025:
            base_price += np.random.randint(2, 5) 
        else:
            base_price += np.random.normal(0, 1)
        prices.append(base_price)
    return pd.DataFrame({'Date': dates, 'Price (TRY/kg)': prices})

def get_climate_risk_data():
    regions = [
        {'Name': 'Giresun', 'Lat': 40.91, 'Lon': 38.38, 'Yield_Risk': 'Critical', 'Temp_Anomaly': -4.5},
        {'Name': 'Ordu', 'Lat': 40.98, 'Lon': 37.88, 'Yield_Risk': 'High', 'Temp_Anomaly': -3.2},
        {'Name': 'Trabzon', 'Lat': 41.00, 'Lon': 39.71, 'Yield_Risk': 'Medium', 'Temp_Anomaly': -1.5},
        {'Name': 'Sakarya', 'Lat': 40.75, 'Lon': 30.38, 'Yield_Risk': 'Low', 'Temp_Anomaly': -0.5},
    ]
    return pd.DataFrame(regions)

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://img.icons8.com/ios-filled/100/4a90e2/earth-element.png", width=80)
st.sidebar.title("Letta Earth")
st.sidebar.caption("Agribusiness Solutions & Trading")

menu = st.sidebar.radio("Intelligence Modules", [
    "📰 Global News Aggregator", # Moved to top as requested
    "🌍 Global Market Watch",
    "🌰 Hazelnut Special Report",
    "🌦️ Climate & Yield Maps", 
])

# --- DASHBOARD LOGIC ---

if menu == "📰 Global News Aggregator":
    st.title("📰 Agri-News Aggregator")
    st.markdown("Real-time intelligence from global and local sources.")
    
    # Controls
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_commodity = st.selectbox(
            "Select Commodity", 
            ["Hazelnuts", "Cocoa", "Avocados", "Coffee", "Wheat", "Corn"]
        )
    with col2:
        region_toggle = st.radio("News Source", ["Global (English)", "Turkey (Local)"], horizontal=True)
        region_code = "Turkey" if region_toggle == "Turkey (Local)" else "Global"

    st.divider()
    
    # Fetch Data
    try:
        with st.spinner(f"Fetching latest {selected_commodity} news from {region_code} sources..."):
            news_data = fetch_news(selected_commodity, region=region_code)
        
        if not news_items:
            st.info("No recent news found. Try a different region.")
        
        # Display Cards
        for item in news_data:
            st.markdown(f"""
            <div class="news-card">
                <a href="{item['link']}" target="_blank" style="text-decoration: none;">
                    <div class="news-title">{item['title']}</div>
                </a>
                <div class="news-meta">
                    Source: <b>{item['source']}</b> | {item['published']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Could not load news feed. Connection error to Google RSS. {e}")

elif menu == "🌍 Global Market Watch":
    st.title("Global Commodity Markets")
    # (Existing Code)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cocoa (ICE)", "$9,240", "+1.2%")
    c2.metric("Wheat (CBOT)", "$580", "-0.5%")
    c3.metric("Corn", "$430", "+0.1%")
    c4.metric("Brent Crude", "$82", "+0.4%")
    
    df_listed = get_listed_commodities()
    tab1, tab2 = st.tabs(["Cocoa", "Wheat"])
    with tab1:
        st.plotly_chart(px.line(df_listed, y='Cocoa ($/MT)', title="Cocoa Futures"), use_container_width=True)
    with tab2:
        st.plotly_chart(px.line(df_listed, y='Wheat ($/Bushel)', title="Wheat Futures"), use_container_width=True)

elif menu == "🌰 Hazelnut Special Report":
    st.title("🌰 Unlisted Commodity Focus: Hazelnuts")
    st.warning("⚠️ **ALERT:** Significant yield reduction projected due to April 2025 Frost Event in Giresun.")
    
    col1, col2 = st.columns([2, 1])
    df_nuts = get_hazelnut_data()
    
    with col1:
        fig = px.line(df_nuts, x='Date', y='Price (TRY/kg)', title="Raw Hazelnut Prices (TRY/kg)")
        fig.add_vline(x=datetime.datetime(2025, 4, 15).timestamp() * 1000, line_dash="dash", line_color="red", annotation_text="Frost Event")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.metric("Pre-Frost Estimate", "650,000 Tons")
        st.metric("Revised Forecast", "480,000 Tons", delta="-26.1%", delta_color="inverse")
        st.info("**Analyst Note:** Flowering stage was severely impacted at >500m altitude.")

elif menu == "🌦️ Climate & Yield Maps":
    st.title("Climate Risk & Yield Impact")
    df_risk = get_climate_risk_data()
    
    fig = px.scatter_mapbox(
        df_risk, lat="Lat", lon="Lon", color="Yield_Risk", size=pd.Series([50, 50, 50, 50]),
        color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'},
        zoom=6, center={"lat": 41.0, "lon": 36.0}, height=600, title="Frost Impact Map"
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
