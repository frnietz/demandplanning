import streamlit as st
import feedparser
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Letta Earth | Agri-News", 
    layout="wide", 
    page_icon="📰",
    initial_sidebar_state="collapsed"
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
                transition: transform 0.2s;
            }
            .news-card:hover {
                transform: scale(1.01);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .news-title {font-size: 18px; font-weight: bold; color: #333;}
            .news-meta {font-size: 12px; color: #666;}
            a {text-decoration: none;}
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
    for entry in feed.entries[:20]: # Increased limit to 20 stories
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'source': entry.source.title if 'source' in entry else 'Google News'
        })
    return news_items

# --- MAIN DASHBOARD ---

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
    
    if not news_data:
        st.info("No recent news found. Try a different region or commodity.")
    else:
        # Display Cards
        for item in news_data:
            st.markdown(f"""
            <div class="news-card">
                <a href="{item['link']}" target="_blank">
                    <div class="news-title">{item['title']}</div>
                </a>
                <div class="news-meta">
                    Source: <b>{item['source']}</b> | {item['published']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
except Exception as e:
    st.error(f"Could not load news feed. Connection error to Google RSS. {e}")
