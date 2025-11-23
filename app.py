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
# Note: Indentation removed to prevent Markdown code-block rendering
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 1rem;}

/* NEWS GRID */
.news-card {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}
.news-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    border-color: #4a90e2;
}
.news-title {
    font-size: 16px;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1.4;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
.news-meta {
    font-size: 11px;
    color: #95a5a6;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.read-more-btn {
    background-color: #f8f9fa;
    color: #4a90e2;
    border: 1px solid #4a90e2;
    padding: 8px 0;
    border-radius: 6px;
    text-align: center;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    display: block;
    transition: background 0.2s;
}
.read-more-btn:hover {
    background-color: #4a90e2;
    color: white;
}

/* DETAILED SECTOR CARD STYLING */
.sector-container {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 25px;
    border-left: 6px solid #2c3e50;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.sector-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}
.sector-title { font-size: 22px; font-weight: 800; color: #2c3e50; }
.sector-share { font-size: 14px; background: #eef2f7; padding: 4px 10px; border-radius: 20px; color: #555; font-weight: 600; }
.sector-status { font-size: 16px; font-weight: bold; }

.insight-section { margin-top: 15px; }
.insight-label { font-size: 13px; text-transform: uppercase; color: #95a5a6; font-weight: 700; letter-spacing: 1px; margin-bottom: 5px; }
.insight-text { font-size: 15px; line-height: 1.6; color: #34495e; margin-bottom: 20px; text-align: justify; }

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
    """Returns sector usage, status, dynamics, and outlook."""
    insights = {
        "Hazelnuts": [
            {
                "Sector": "Confectionery & Chocolate", 
                "Share": "80%", 
                "Status": "🔴 Stressed", 
                "Dynamics": "The confectionery sector is facing a severe supply shock due to the Giresun frost event. Major buyers like Ferrero and Lindt, who depend on the specific fat content and flavor profile of Turkish hazelnuts, are seeing spot prices surge. Contract fulfillment rates are dropping as farmers withhold stock in anticipation of higher prices (30-40% increase year-on-year). Substitution with Georgian or Italian nuts is technically difficult due to differing roasting profiles.",
                "Outlook": "We expect a significant margin compression for Q3/Q4 2025. Manufacturers will likely pass costs to consumers through 'shrinkflation' (reducing pack sizes). Long-term, R&D teams are accelerating recipes that reduce nut inclusion rates or blend origin sources to mitigate single-origin risk."
            },
            {
                "Sector": "Snacks & Retail", 
                "Share": "15%", 
                "Status": "🟡 Caution", 
                "Dynamics": "Private label brands are particularly vulnerable as they operate on thinner margins than premium brands. Retailers are currently resisting price hikes, forcing suppliers to absorb the raw material volatility. There is a noticeable shift in shelf space towards peanut or almond-based alternatives which offer more stable pricing structures.",
                "Outlook": "Expect a reduction in promotional activities for hazelnut spreads and whole-nut snacks. If prices remain elevated through the post-harvest season, retailers may temporarily delist lower-tier hazelnut SKUs in favor of more profitable almond or cashew mixes."
            }
        ],
        "Cocoa": [
            {
                "Sector": "Chocolate Manufacturing", 
                "Share": "65%", 
                "Status": "🔴 Critical", 
                "Dynamics": "We are witnessing a structural deficit in the cocoa market driven by aging tree stocks and swollen shoot virus in West Africa (Ivory Coast/Ghana). The 'farm gate' price mechanism has failed to incentivize replanting fast enough. Grinders are reporting critically low butter ratios, and the cost of goods sold (COGS) for dark chocolate lines has nearly doubled in 18 months.",
                "Outlook": "The industry is pivoting towards 'Cocoa Butter Equivalents' (CBEs) and compound coatings for mass-market products. Premium lines will see steep price increases, positioning real chocolate as a luxury good. Regulatory pressure (EU Deforestation Regulation) will further tighten supply of compliant beans, keeping a floor under prices."
            },
            {
                "Sector": "Cosmetics & Personal Care", 
                "Share": "15%", 
                "Status": "🟢 Growing", 
                "Dynamics": "Demand for cocoa butter in skin and hair care remains robust, driven by the 'clean beauty' trend. Unlike food, the cosmetics sector can absorb higher input costs due to high retail markups. However, competition for high-quality butter is intensifying with food manufacturers.",
                "Outlook": "Formulators are likely to blend cocoa butter with Shea or Mango butter to manage costs. We forecast steady growth, but supply security will become a key component of supplier contracts, with brands seeking direct-trade relationships to bypass volatile exchanges."
            }
        ],
        "Avocados": [
            {
                "Sector": "Fresh Retail & Food Service", 
                "Share": "85%", 
                "Status": "🟢 Bullish", 
                "Dynamics": "Demand is heavily event-driven (Super Bowl, Cinco de Mayo) but has stabilized into a year-round staple. Supply chain reliability from Mexico (Michoacán) faces intermittent disruption from cartel activity and water scarcity issues. However, the rise of Peruvian and Colombian exports has successfully smoothed out the traditional summer supply gaps.",
                "Outlook": "Volume continues to grow, but price sensitivity is increasing. Fast Casual chains (e.g., Chipotle) are hedging costs through forward contracts. Expect to see smaller sizing specs (48s vs 60s) becoming the norm in retail bags to mask inflation. Ripening-at-destination technology is improving, reducing waste and improving margins."
            }
        ],
        "Coffee": [
            {
                "Sector": "Specialty Roasters", 
                "Share": "20%", 
                "Status": "🟠 Strained", 
                "Dynamics": "The specialty market is grappling with climate-induced volatility. High temperatures in Brazil and Vietnam are affecting bean density and cupping scores. Roasters are finding it harder to secure '80+ point' lots at historical prices. Logistics costs remain elevated, squeezing the margins of independent cafes.",
                "Outlook": "Consolidation is likely among mid-sized roasters. Menus will simplify, and blends will replace single-origin offerings to maintain flavor consistency despite crop variability. Price increases at the cup level are inevitable."
            },
            {
                "Sector": "Instant & Commercial", 
                "Share": "45%", 
                "Status": "🟢 Stable", 
                "Dynamics": "Robusta prices have hit record highs, but the sector is resilient. Major conglomerates have massive hedging capabilities and buffer stocks. The shift towards 'Cold Brew' ready-to-drink (RTD) products is creating a new, high-margin revenue stream that offsets raw bean costs.",
                "Outlook": "Continued investment in Vietnam and Indonesia to secure Robusta supply. We expect a surge in RTD coffee products in emerging markets, driving volume growth even if per-cup margins tighten."
            }
        ],
        "Wheat": [
            {
                "Sector": "Milling & Baking", 
                "Share": "60%", 
                "Status": "🟡 Volatile", 
                "Dynamics": "Geopolitical tension in the Black Sea continues to create uncertainty. While prices have retreated from 2022 highs, basis risk remains high. Millers are keeping shorter coverage positions, unwilling to lock in long-term contracts in a backwardated market.",
                "Outlook": "Focus on protein premiums. High-protein milling wheat will command a significant spread over feed wheat. Bakeries will explore enzyme solutions to improve dough stability using lower-protein flour to manage costs."
            }
        ],
        "Corn": [
            {
                "Sector": "Animal Feed", 
                "Share": "55%", 
                "Status": "🟢 Abundant", 
                "Dynamics": "A record US crop and strong Brazilian Safrinha harvest have rebuilt global stocks. Feed ratios are favorable, encouraging herd expansion in poultry and swine sectors. Prices are currently testing cost-of-production support levels.",
                "Outlook": "Demand will likely remain robust, but upside price potential is limited without a major weather event. Buyers are moving to 'hand-to-mouth' purchasing strategies, confident in the depth of supply."
            },
            {
                "Sector": "Ethanol & Biofuels", 
                "Share": "35%", 
                "Status": "🟡 Regulatory Risk", 
                "Dynamics": "Margins are healthy, but the sector is heavily dependent on government mandates (RFS in USA). The push for Electric Vehicles (EVs) poses a long-term existential threat to liquid biofuel demand.",
                "Outlook": "The industry is pivoting towards Sustainable Aviation Fuel (SAF). We expect corn demand for ethanol to plateau, with future growth driven by aviation rather than road transport."
            }
        ]
    }
    
    # Fallback for error handling
    default = [{
        "Sector": "General Market", 
        "Share": "100%", 
        "Status": "⚪ Normal", 
        "Dynamics": "Standard supply and demand forces are currently balanced. No major disruptions reported.", 
        "Outlook": "Market is expected to track historical seasonality."
    }]
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
    for entry in feed.entries:
        published_parsed = entry.get('published_parsed', time.gmtime())
        date_str = time.strftime("%d %b %Y", published_parsed)
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': date_str,
            'timestamp': published_parsed,
            'source': entry.source.title if 'source' in entry else 'Google News'
        })
    news_items.sort(key=lambda x: x['timestamp'], reverse=True)
    return news_items[:12]

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
            for i in range(0, len(news_data), 3):
                row_items = news_data[i:i+3]
                cols = st.columns(3)
                for idx, item in enumerate(row_items):
                    with cols[idx]:
                        # Removed indentation inside markdown string to prevent code block rendering
                        html_content = f"""
<div class="news-card">
    <div>
        <div class="news-meta">{item['source']} • {item['published']}</div>
        <div class="news-title">{item['title']}</div>
    </div>
    <a href="{item['link']}" target="_blank" class="read-more-btn">
        Read Article ↗
    </a>
</div>
"""
                        st.markdown(html_content, unsafe_allow_html=True)       
    except Exception as e:
        st.error(f"Could not load news feed. Connection error to Google RSS. {e}")

# === TAB 2: SUPPLY MAPS & SECTORS ===
with tab_map:
    st.header(f"Global Supply Chain: {selected_commodity}")
    
    # 1. Map Section
    st.subheader("📍 Primary Supply Locations & Risk Zones")
    map_df = get_supply_map_data(selected_commodity)
    
    if not map_df.empty:
        fig = px.scatter_mapbox(
            map_df, lat="Lat", lon="Lon", color="Risk",
            size=pd.Series([20]*len(map_df)), hover_name="Region",
            hover_data={"Output": True, "Lat": False, "Lon": False},
            color_discrete_map={
                'Critical (Frost)': '#d62728', 'High (Frost)': '#ff7f0e',
                'High (Drought)': '#ff7f0e', 'High (Geopolitics)': '#ff7f0e',
                'Medium': '#bcbd22', 'Low': '#2ca02c'
            }, zoom=1, height=450
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Map data not available.")

    st.divider()

    # 2. Sector Analysis Section (New Layout)
    st.subheader("🏭 Downstream Sector Impact & Future Outlook")
    sectors = get_sector_insights(selected_commodity)
    
    for sec in sectors:
        # Removed indentation inside markdown string to prevent code block rendering
        html_content = f"""
<div class="sector-container">
    <div class="sector-header">
        <div>
            <span class="sector-title">{sec['Sector']}</span>
            <span class="sector-share">Share: {sec['Share']}</span>
        </div>
        <div class="sector-status">{sec['Status']}</div>
    </div>
    
    <div class="insight-section">
        <div class="insight-label">Market Dynamics</div>
        <div class="insight-text">{sec['Dynamics']}</div>
    </div>
    
    <div class="insight-section">
        <div class="insight-label">Strategic Outlook</div>
        <div class="insight-text">{sec['Outlook']}</div>
    </div>
</div>
"""
        st.markdown(html_content, unsafe_allow_html=True)
