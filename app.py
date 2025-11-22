import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Letta Earth | Agribusiness Intelligence", 
    layout="wide", 
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR WIX EMBEDDING ---
# This removes the top header and footer so it looks native inside your website
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- MOCK DATA ENGINE ---

def get_listed_commodities():
    # In real life, use yfinance library here
    dates = pd.date_range(start="2024-01-01", end="2025-05-20", freq="D")
    df = pd.DataFrame(index=dates)
    df['Cocoa ($/MT)'] = np.linspace(4000, 9000, len(dates)) + np.random.normal(0, 100, len(dates))
    df['Wheat ($/Bushel)'] = np.linspace(600, 550, len(dates)) + np.random.normal(0, 10, len(dates))
    return df

def get_hazelnut_data():
    """
    Simulating the 2025 Frost Event in Giresun.
    Unlisted data usually comes from local exchanges (Borsasi) or field reports.
    """
    dates = pd.date_range(start="2024-09-01", end="2025-05-20", freq="W") # Weekly prices
    
    # Simulating price spike after April 2025 Frost
    prices = []
    base_price = 100 # TRY/kg
    for d in dates:
        if d.month >= 4 and d.year == 2025:
            # Frost impact: Price jumps significantly
            base_price += np.random.randint(2, 5) 
        else:
            base_price += np.random.normal(0, 1)
        prices.append(base_price)
        
    df = pd.DataFrame({'Date': dates, 'Price (TRY/kg)': prices})
    return df

def get_climate_risk_data():
    """
    Map data for Turkey Hazelnut regions.
    """
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
    "🌍 Global Market Watch",
    "🌰 Hazelnut Special Report",
    "🌦️ Climate & Yield Maps", 
    "📰 News & Sentiment"
])

# --- DASHBOARD LOGIC ---

if menu == "🌍 Global Market Watch":
    st.title("Global Commodity Markets")
    st.markdown("Real-time tracking of **Listed Commodities** (Stock Market Data).")
    
    # 1. Ticker Tape (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cocoa (ICE)", "$9,240", "+1.2%", help="High volatility due to West Africa supply issues")
    c2.metric("Wheat (CBOT)", "$580", "-0.5%")
    c3.metric("Corn", "$430", "+0.1%")
    c4.metric("Brent Crude", "$82", "+0.4%", help="Affects logistics costs")
    
    # 2. Charts
    st.subheader("Market Trends")
    df_listed = get_listed_commodities()
    tab1, tab2 = st.tabs(["Cocoa", "Wheat"])
    
    with tab1:
        fig = px.line(df_listed, y='Cocoa ($/MT)', title="Cocoa Futures (2024-2025)")
        fig.update_traces(line_color='#8B4513')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = px.line(df_listed, y='Wheat ($/Bushel)', title="Wheat Futures")
        fig.update_traces(line_color='#F5DEB3')
        st.plotly_chart(fig, use_container_width=True)

elif menu == "🌰 Hazelnut Special Report":
    st.title("🌰 Unlisted Commodity Focus: Hazelnuts")
    st.warning("⚠️ **ALERT:** Significant yield reduction projected due to April 2025 Frost Event in Giresun region.")
    
    col1, col2 = st.columns([2, 1])
    
    df_nuts = get_hazelnut_data()
    
    with col1:
        st.subheader("Local Exchange Price (Giresun/Ordu)")
        # Annotate the chart to show the frost event
        fig = px.line(df_nuts, x='Date', y='Price (TRY/kg)', title="Raw Hazelnut Prices (TRY/kg)")
        fig.add_vline(x=datetime.datetime(2025, 4, 15).timestamp() * 1000, line_dash="dash", line_color="red", annotation_text="Frost Event")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Yield Forecast Model")
        current_yield = 650000 # Tons
        projected_yield = 480000 # Tons
        loss_pct = ((current_yield - projected_yield) / current_yield) * 100
        
        st.metric("Pre-Frost Estimate", f"{current_yield:,} Tons")
        st.metric("Revised Forecast", f"{projected_yield:,} Tons", delta=f"-{loss_pct:.1f}%", delta_color="inverse")
        st.info("**Analyst Note:** Flowering stage was severely impacted at >500m altitude.")

elif menu == "🌦️ Climate & Yield Maps":
    st.title("Climate Risk & Yield Impact")
    st.markdown("Geospatial analysis of production zones vs. weather anomalies.")
    
    df_risk = get_climate_risk_data()
    
    # Map Visualization
    fig = px.scatter_mapbox(
        df_risk, 
        lat="Lat", 
        lon="Lon", 
        color="Yield_Risk",
        size=pd.Series([50, 50, 50, 50]), # Bubble size
        hover_name="Name",
        hover_data={"Temp_Anomaly": True, "Lat": False, "Lon": False},
        color_discrete_map={'Critical': 'red', 'High': 'orange', 'Medium': 'yellow', 'Low': 'green'},
        zoom=6, 
        center={"lat": 41.0, "lon": 36.0},
        height=600,
        title="April 2025 Frost Impact Map"
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📰 News & Sentiment":
    st.title("Agri-Intelligence Feed")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Local Signals (Turkey)")
        st.markdown("""
        * **2025-04-20:** ❄️ *Ziraat Odası Reports:* "Damage assessment underway in Giresun highlands. Estimates suggest 40% loss in high altitude orchards."
        * **2025-04-18:** 📉 *Market Update:* Buyers halting procurement anticipating price discovery issues.
        * **2025-04-15:** 🚨 *Weather Alert:* Sudden temperature drop to -3°C recorded in inner Black Sea region.
        """)
        
    with col2:
        st.subheader("Global Context")
        st.markdown("""
        * **Ferrero Update:** Major buyers monitoring Turkish supply closely; Italy crop looking stable.
        * **Currency Impact:** TRY fluctuation adding complexity to export pricing.
        """)
