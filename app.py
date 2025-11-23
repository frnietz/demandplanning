import streamlit as st
import feedparser
import pandas as pd
import plotly.express as px
import numpy as np
import time
import textwrap

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Letta Earth | Agri-News & Intelligence", 
    layout="wide", 
    page_icon="🌍",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS FOR WIX EMBEDDING ---
hide_streamlit_style = textwrap.dedent("""
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
    a {text-decoration: none;}
    </style>
""")
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
        ],
        "Cotton": [
            {"Region": "Texas, USA", "Lat": 31.96, "Lon": -99.90, "Output": "High", "Risk": "Medium (Drought)"},
            {"Region": "Gujarat, India", "Lat": 22.25, "Lon": 71.19, "Output": "Very High", "Risk": "Medium"},
            {"Region": "Xinjiang, China", "Lat": 41.11, "Lon": 85.26, "Output": "Very High", "Risk": "Low"},
        ],
        "Soybeans": [
            {"Region": "Mato Grosso, Brazil", "Lat": -12.68, "Lon": -56.09, "Output": "Very High", "Risk": "Low"},
            {"Region": "Illinois, USA", "Lat": 40.63, "Lon": -89.39, "Output": "High", "Risk": "Low"},
        ]
    }
    return pd.DataFrame(data.get(commodity, []))

def get_sector_insights(commodity):
    """Returns sector usage, status, dynamics, and outlook."""
    insights = {
        "Hazelnuts": [
            {"Sector": "Confectionery", "Share": "80%", "Status": "🔴 Stressed", "Dynamics": "Supply shock due to frost."},
            {"Sector": "Snacks & Retail", "Share": "15%", "Status": "🟡 Caution", "Dynamics": "Margins squeezing."},
            {"Sector": "Cosmetics", "Share": "5%", "Status": "🟢 Stable", "Dynamics": "Niche market stable."}
        ],
        "Cocoa": [
            {"Sector": "Chocolate Mfg", "Share": "65%", "Status": "🔴 Critical", "Dynamics": "Structural deficit."},
            {"Sector": "Cosmetics", "Share": "15%", "Status": "🟢 Growing", "Dynamics": "Clean beauty trend."}
        ],
        "Avocados": [
            {"Sector": "Fresh Retail", "Share": "85%", "Status": "🟢 Bullish", "Dynamics": "Super Bowl demand."},
            {"Sector": "Oil Processing", "Share": "10%", "Status": "🟢 Emerging", "Dynamics": "Replacing olive oil."}
        ],
        "Coffee": [
            {"Sector": "Specialty Roasters", "Share": "20%", "Status": "🟠 Strained", "Dynamics": "High bean prices."},
            {"Sector": "Instant/Commercial", "Share": "45%", "Status": "🟢 Stable", "Dynamics": "Robust hedging."}
        ],
        "Wheat": [
            {"Sector": "Milling & Baking", "Share": "60%", "Status": "🟡 Volatile", "Dynamics": "Geopolitical risk."}
        ],
        "Corn": [
            {"Sector": "Animal Feed", "Share": "55%", "Status": "🟢 Abundant", "Dynamics": "Record crops."},
            {"Sector": "Ethanol", "Share": "35%", "Status": "🟡 Risk", "Dynamics": "EV transition threat."}
        ]
    }
    default = [{"Sector": "General Market", "Share": "100%", "Status": "⚪ Normal", "Dynamics": "Market balanced."}]
    return pd.DataFrame(insights.get(commodity, default))

def get_commodity_facts(commodity):
    """Returns static fact sheet data from curated knowledge base."""
    data = {
        "Hazelnuts": {
            "origin": "Native to the temperate Northern Hemisphere.",
            "producers": "Turkey (~70%), Italy, Azerbaijan, USA (Oregon).",
            "uses": "Confectionery (pralines, spreads), baking, oil extraction.",
            "desc": "The hazelnut is the nut of the hazel and therefore includes any of the nuts deriving from species of the genus Corylus, especially the nuts of the species Corylus avellana."
        },
        "Cocoa": {
            "origin": "Upper Amazon basin.",
            "producers": "Ivory Coast (~40%), Ghana, Indonesia, Ecuador.",
            "uses": "Chocolate, Cocoa butter (cosmetics), Cocoa powder.",
            "desc": "Cocoa beans are the dried and fully fermented seeds of Theobroma cacao, from which cocoa solids and cocoa butter can be extracted."
        },
        "Avocados": {
            "origin": "South Central Mexico.",
            "producers": "Mexico, Peru, Indonesia, Colombia.",
            "uses": "Fresh consumption (guacamole), oil, cosmetics.",
            "desc": "The avocado (Persea americana) is a medium-sized, evergreen tree in the laurel family. It is native to the Americas and was first domesticated by Mesoamerican tribes."
        },
        "Coffee": {
            "origin": "Ethiopia (Arabica) / West Africa (Robusta).",
            "producers": "Brazil, Vietnam, Colombia, Indonesia.",
            "uses": "Beverage, flavoring, caffeine extraction.",
            "desc": "Coffee is a brewed drink prepared from roasted coffee beans, the seeds of berries from certain Coffea species."
        },
        "Wheat": {
            "origin": "Fertile Crescent (Middle East).",
            "producers": "China, India, Russia, USA, France.",
            "uses": "Flour (bread, pasta, pastry), animal feed, ethanol.",
            "desc": "Wheat is a grass widely cultivated for its seed, a cereal grain which is a worldwide staple food."
        },
        "Corn": {
            "origin": "Southern Mexico.",
            "producers": "USA, China, Brazil, Argentina.",
            "uses": "Animal feed, ethanol, high-fructose corn syrup, human food.",
            "desc": "Maize, also known as corn, is a cereal grain first domesticated by indigenous peoples in southern Mexico about 10,000 years ago."
        },
        "Soybeans": {
            "origin": "East Asia.",
            "producers": "Brazil, USA, Argentina.",
            "uses": "Animal feed (meal), oil, tofu, soy milk.",
            "desc": "The soybean (Glycine max) is a species of legume native to East Asia, widely grown for its edible bean, which has numerous uses."
        },
        "Palm Oil": {
            "origin": "West Africa.",
            "producers": "Indonesia, Malaysia, Thailand.",
            "uses": "Cooking oil, processed foods, biofuels, soaps.",
            "desc": "Palm oil is an edible vegetable oil derived from the mesocarp (reddish pulp) of the fruit of the oil palms."
        },
        "Cotton": {
            "origin": "Independently in Old and New Worlds.",
            "producers": "China, India, USA, Brazil.",
            "uses": "Textiles, cottonseed oil, animal feed.",
            "desc": "Cotton is a soft, fluffy staple fiber that grows in a boll, or protective case, around the seeds of the cotton plants of the genus Gossypium."
        },
        "Sugar": {
            "origin": "New Guinea (Cane) / Europe (Beet).",
            "producers": "Brazil, India, EU, Thailand, China.",
            "uses": "Sweetener, ethanol, preservatives.",
            "desc": "Sugar is the generic name for sweet-tasting, soluble carbohydrates, many of which are used in food. Primary sources are Sugarcane and Sugar Beet."
        }
    }
    
    default = {
        "origin": "Global.",
        "producers": "Varies by specific type.",
        "uses": "Food, industrial applications.",
        "desc": f"{commodity} is a widely traded global commodity."
    }
    
    return data.get(commodity, default)

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
            "Corn": "Mısır hasadı",
            "Soybeans": "Soya fasulyesi fiyatları",
            "Palm Oil": "Palm yağı piyasası",
            "Cotton": "Pamuk fiyatları Adana",
            "Sugar": "Şeker pancarı fiyatları"
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
    preset_options = ["Hazelnuts", "Cocoa", "Avocados", "Coffee", "Wheat", "Corn", "Soybeans", "Palm Oil", "Cotton", "Sugar", "Other (Type Custom)"]
    choice = st.selectbox("Select Commodity", preset_options)
    if choice == "Other (Type Custom)":
        selected_commodity = st.text_input("Type Commodity Name", value="Rice")
    else:
        selected_commodity = choice

with col2:
    region_toggle = st.radio("Data Source", ["Global (English)", "Turkey (Local)"], horizontal=True)
    region_code = "Turkey" if region_toggle == "Turkey (Local)" else "Global"

st.divider()

# --- TOP SECTION: INTELLIGENCE (Map + Table + Fact Sheet) ---
c_map, c_table = st.columns([1.5, 1])

with c_map:
    st.subheader(f"📍 Supply Zones: {selected_commodity}")
    map_df = get_supply_map_data(selected_commodity)
    if not map_df.empty:
        fig = px.scatter_mapbox(
            map_df, lat="Lat", lon="Lon", color="Risk",
            size=pd.Series([15]*len(map_df)), hover_name="Region",
            hover_data={"Output": True, "Lat": False, "Lon": False},
            color_discrete_map={
                'Critical (Frost)': '#d62728', 'High (Frost)': '#ff7f0e',
                'High (Drought)': '#ff7f0e', 'High (Geopolitics)': '#ff7f0e',
                'Medium': '#bcbd22', 'Low': '#2ca02c'
            }, zoom=0.5, height=350
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Supply map data not available.")

with c_table:
    # 1. Sector Table
    st.subheader("🏭 Sector Insights")
    sector_df = get_sector_insights(selected_commodity)
    st.dataframe(
        sector_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Health", help="Current sector health"),
            "Share": st.column_config.ProgressColumn("Usage %", format="%s", min_value=0, max_value=100),
        }
    )
    
    # 2. Fact Sheet (Replaces Price Chart)
    st.write("") # Spacer
    st.subheader("📋 Product Fact Sheet")
    facts = get_commodity_facts(selected_commodity)
    
    # Styled Fact Sheet Card
    html_content = textwrap.dedent(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #eee;">
            <div style="font-size: 14px; color: #555; margin-bottom: 8px;">
                <strong>Scientific Description:</strong><br>
                <span style="font-style: italic;">{facts['desc']}</span>
            </div>
            <div style="font-size: 14px; color: #555; margin-bottom: 8px;">
                <strong>🌍 Top Producers:</strong> {facts['producers']}
            </div>
            <div style="font-size: 14px; color: #555; margin-bottom: 8px;">
                <strong>🏭 Primary Uses:</strong> {facts['uses']}
            </div>
             <div style="font-size: 12px; color: #999; margin-top: 10px; border-top: 1px solid #ddd; padding-top: 5px;">
                Sources: FAOSTAT, Wikipedia, USDA
            </div>
        </div>
    """)
    st.markdown(html_content, unsafe_allow_html=True)

st.divider()

# --- BOTTOM SECTION: NEWS GRID ---
st.subheader(f"📰 Latest News: {selected_commodity}")

try:
    with st.spinner(f"Fetching latest news..."):
        news_data = fetch_news(selected_commodity, region=region_code)
    
    if not news_data:
        st.info("No recent news found.")
    else:
        for i in range(0, len(news_data), 3):
            row_items = news_data[i:i+3]
            cols = st.columns(3)
            for idx, item in enumerate(row_items):
                with cols[idx]:
                    html_content = textwrap.dedent(f"""
                        <div class="news-card">
                            <div>
                                <div class="news-meta">{item['source']} • {item['published']}</div>
                                <div class="news-title">{item['title']}</div>
                            </div>
                            <a href="{item['link']}" target="_blank" class="read-more-btn">
                                Read Article ↗
                            </a>
                        </div>
                    """)
                    st.markdown(html_content, unsafe_allow_html=True)       
except Exception as e:
    st.error(f"News Error: {e}")
