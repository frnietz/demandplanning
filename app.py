import streamlit as st
import feedparser
import pandas as pd
import plotly.express as px
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Letta Earth | Agri-News & Intelligence", 
    layout="wide", 
    page_icon="🌍",
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
            .sector-card {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                text-align: center;
                height: 100%;
            }
            .metric-val {font-size: 24px; font-weight: bold; color: #2c3e50;}
            .metric-label {font-size: 14px; color: #7f8c8d; margin-bottom: 10px;}
            a {text-decoration: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- DATA ENGINE: MAPS & SECTORS ---
def get_supply_map_data(commodity):
    """Returns geolocation data for major production hubs."""
    data = {
        "Hazelnuts": [
            {"Region": "Giresun, Turkey", "Lat": 40.91, "Lon": 38.38, "Output": "High", "Risk": "Critical (Frost)"},
            {"Region": "Ordu, Turkey", "Lat": 40.98, "Lon": 37.88, "Output": "High", "Risk": "High (Frost)"},
            {"Region": "Viterbo, Italy", "Lat": 42.42, "Lon": 12.10, "Output": "Medium", "Risk": "Low"},
            {"Region": "Oregon, USA", "Lat": 44.94, "Lon": -123.03, "Output": "Low", "Risk": "Low"},
        ],
        "Cocoa": [
            {"Region": "Abidjan, Ivory Coast", "Lat": 5.36, "Lon": -4.00, "Output": "Very High", "Risk": "Medium (Disease)"},
            {"Region": "Accra, Ghana", "Lat": 5.60, "Lon": -0.18, "Output": "High", "Risk": "High (Drought)"},
            {"Region": "Sulawesi, Indonesia", "Lat": -2.50, "Lon": 119.50, "Output": "Medium", "Risk": "Low"},
        ],
        "Avocados": [
            {"Region": "Michoacan, Mexico", "Lat": 19.56, "Lon": -101.70, "Output": "Very High", "Risk": "Medium (Cartel/Water)"},
            {"Region": "La Libertad, Peru", "Lat": -8.10, "Lon": -79.02, "Output": "High", "Risk": "Low"},
            {"Region": "California, USA", "Lat": 36.77, "Lon": -119.41, "Output": "Medium", "Risk": "High (Drought)"},
        ],
        "Coffee": [
            {"Region": "Minas Gerais, Brazil", "Lat": -18.51, "Lon": -44.55, "Output": "Very High", "Risk": "Medium (Heat)"},
            {"Region": "Dak Lak, Vietnam", "Lat": 12.66, "Lon": 108.03, "Output": "High", "Risk": "Low"},
            {"Region": "Huila, Colombia", "Lat": 2.53, "Lon": -75.54, "Output": "Medium", "Risk": "Low"},
        ],
        "Wheat": [
            {"Region": "Kansas, USA", "Lat": 38.50, "Lon": -98.00, "Output": "High", "Risk": "Medium"},
            {"Region": "Rostov, Russia", "Lat": 47.23, "Lon": 39.70, "Output": "Very High", "Risk": "High (Geopolitics)"},
        ],
        "Corn": [
            {"Region": "Iowa, USA", "Lat": 42.03, "Lon": -93.64, "Output": "Very High", "Risk": "Low"},
            {"Region": "Mato Grosso, Brazil", "Lat": -12.68, "Lon": -56.09, "Output": "High", "Risk": "Medium"},
        ]
    }
    return pd.DataFrame(data.get(commodity, []))

def get_sector_insights(commodity):
    """Returns sector usage and status info."""
    insights = {
        "Hazelnuts": [
            {"Sector": "Confectionery & Chocolate", "Share": "80%", "Status": "🔴 Stressed", "Insight": "Major buyers (Ferrero, Lindt) facing 30% input cost hikes due to Giresun shortage."},
            {"Sector": "Snacks & Retail", "Share": "15%", "Status": "🟡 Caution", "Insight": "Private label brands reducing pack sizes (shrinkflation) to maintain price points."},
            {"Sector": "Cosmetics (Oil)", "Share": "5%", "Status": "🟢 Stable", "Insight": "Niche market demand remains unaffected by bulk commodity price swings."}
        ],
        "Cocoa": [
            {"Sector": "Chocolate Mfg", "Share": "65%", "Status": "🔴 Critical", "Insight": "Historic supply deficit. Manufacturers pivoting to compounds/fillers to reduce cocoa mass."},
            {"Sector": "Beverage & Powder", "Share": "20%", "Status": "🟠 Strained", "Insight": "High powder prices impacting instant beverage margins in Asia."},
            {"Sector": "Cosmetics", "Share": "15%", "Status": "🟢 Growing", "Insight": "Cocoa butter substitutes gaining traction, but natural trend keeps demand high."}
        ],
        "Avocados": [
            {"Sector": "Fresh Retail / QSR", "Share": "85%", "Status": "🟢 Bullish", "Insight": "Super Bowl volume record expected. Chipotle/Subway demand steady."},
            {"Sector": "Oil & Processing", "Share": "10%", "Status": "🟢 Emerging", "Insight": "Avocado oil capturing market share from olive oil due to price parity."},
            {"Sector": "Cosmetics", "Share": "5%", "Status": "🟡 Flat", "Insight": "Steady demand for hair/skin products, highly sensitive to pricing."}
        ]
    }
    # Default fallback
    default = [{"Sector": "General Food", "Share": "90%", "Status": "⚪ Normal", "Insight": "Standard commodity demand patterns apply."}]
    return insights.get(commodity, default)

# --- NEWS ENGINE (RSS) ---
@st.cache_data(ttl=3600)
def fetch_news(query, region='Global'):
    if region == 'Turkey':
        base_url = "https://news.google.com/rss/search?q={}&hl=tr&gl=TR&ceid=TR:tr"
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

    feed_url = base_url.format(search_term.replace(" ", "%20"))
    feed = feedparser.parse(feed_url)
    
    news_items = []
    for entry in feed.entries[:15]:
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'source': entry.source.title if 'source' in entry else 'Google News'
        })
    return news_items

# --- MAIN APP LAYOUT ---

st.title("Letta Earth Intelligence")
st.markdown("Global Agribusiness Insights & News Aggregation")

# Global Controls
col1, col2 = st.columns([1, 1])
with col1:
    selected_commodity = st.selectbox(
        "Select Commodity", 
        ["Hazelnuts", "Cocoa", "Avocados", "Coffee", "Wheat", "Corn"]
    )
with col2:
    region_toggle = st.radio("Data Source", ["Global (English)", "Turkey (Local)"], horizontal=True)
    region_code = "Turkey" if region_toggle == "Turkey (Local)" else "Global"

st.divider()

# --- TABS ARCHITECTURE ---
tab_news, tab_map = st.tabs(["📰 News Feed", "🗺️ Supply & Sector Intelligence"])

# === TAB 1: NEWS ===
with tab_news:
    try:
        with st.spinner(f"Fetching latest {selected_commodity} news from {region_code} sources..."):
            news_data = fetch_news(selected_commodity, region=region_code)
        
        if not news_data:
            st.info("No recent news found. Try a different region or commodity.")
        else:
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

# === TAB 2: SUPPLY MAPS & SECTORS ===
with tab_map:
    st.header(f"Global Supply Chain: {selected_commodity}")
    
    # 1. Map Section
    st.subheader("📍 Primary Supply Locations & Risk Zones")
    map_df = get_supply_map_data(selected_commodity)
    
    if not map_df.empty:
        # Create interactive Mapbox scatter plot
        fig = px.scatter_mapbox(
            map_df, 
            lat="Lat", 
            lon="Lon", 
            color="Risk",
            size=pd.Series([20]*len(map_df)), # Fixed bubble size
            hover_name="Region",
            hover_data={"Output": True, "Lat": False, "Lon": False},
            color_discrete_map={
                'Critical (Frost)': '#d62728', # Red
                'High (Frost)': '#ff7f0e',     # Orange
                'High (Drought)': '#ff7f0e',
                'High (Geopolitics)': '#ff7f0e',
                'Medium': '#bcbd22',           # Yellow/Olive
                'Low': '#2ca02c'               # Green
            },
            zoom=1,
            height=500
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Map data not available for this commodity yet.")

    st.divider()

    # 2. Sector Analysis Section
    st.subheader("🏭 Downstream Sector Impact & Future Outlook")
    sectors = get_sector_insights(selected_commodity)
    
    # Dynamic columns based on number of sectors
    cols = st.columns(len(sectors))
    
    for idx, col in enumerate(cols):
        sec = sectors[idx]
        with col:
            st.markdown(f"""
            <div class="sector-card">
                <div class="metric-label">{sec['Sector']} (Uses {sec['Share']})</div>
                <div class="metric-val">{sec['Status']}</div>
                <hr style="margin: 10px 0; opacity: 0.3;">
                <div style="font-size: 13px; color: #555; line-height: 1.4;">
                    {sec['Insight']}
                </div>
            </div>
            """, unsafe_allow_html=True)
