import streamlit as st
import feedparser
import pandas as pd
import plotly.express as px
import numpy as np
import time
import textwrap
from bs4 import BeautifulSoup

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Letta Earth | Agri-News & Intelligence", 
    layout="wide", 
    page_icon="🌍",
    initial_sidebar_state="collapsed"
)

# --- TRANSLATION ENGINE ---
TRANSLATIONS = {
    "en": {
        "title": "Letta Earth Intelligence",
        "subtitle": "Global Agribusiness Insights & News Aggregation",
        "select_lbl": "Select Commodity",
        "custom_lbl": "Type Commodity Name",
        "source_lbl": "News & Data Source",
        "supply_zones": "📍 Supply Zones",
        "sector_insights": "🏭 Sector Insights",
        "market_balance": "📊 Global Market Balance (Est. 2024/25)",
        "production": "Production",
        "consumption": "Consumption",
        "balance": "Balance",
        "surplus": "Surplus/Deficit",
        "fact_sheet": "📋 Product Fact Sheet",
        "sci_desc": "Scientific Description:",
        "top_prod": "🌍 Top Producers:",
        "uses": "🏭 Primary Uses:",
        "news_header": "📰 Latest News",
        "read_btn": "Read Article ↗",
        "no_news": "No recent news found.",
        "loading": "Fetching latest news...",
        "sources_foot": "Sources: FAOSTAT, Wikipedia, USDA",
        "other_opt": "Other (Type Custom)",
        "global_opt": "Global (English)",
        "local_opt": "Turkey (Local)",
        "news_error": "Could not fetch news. Error:"
    },
    "tr": {
        "title": "Letta Earth İstihbarat",
        "subtitle": "Küresel Tarım İşletmeleri İçgörüleri ve Haber Kaynağı",
        "select_lbl": "Ürün Seçiniz",
        "custom_lbl": "Ürün Adı Giriniz",
        "source_lbl": "Haber ve Veri Kaynağı",
        "supply_zones": "📍 Tedarik Bölgeleri",
        "sector_insights": "🏭 Sektörel İçgörüler",
        "market_balance": "📊 Küresel Pazar Dengesi (Tahmini 2024/25)",
        "production": "Üretim",
        "consumption": "Tüketim",
        "balance": "Denge",
        "surplus": "Fazla/Açık",
        "fact_sheet": "📋 Ürün Bilgi Kartı",
        "sci_desc": "Bilimsel Tanım:",
        "top_prod": "🌍 En Büyük Üreticiler:",
        "uses": "🏭 Temel Kullanım Alanları:",
        "news_header": "📰 Güncel Haberler",
        "read_btn": "Haberi Oku ↗",
        "no_news": "Güncel haber bulunamadı.",
        "loading": "Haberler yükleniyor...",
        "sources_foot": "Kaynaklar: FAOSTAT, Wikipedia, USDA",
        "other_opt": "Diğer (Manuel Giriş)",
        "global_opt": "Küresel (İngilizce)",
        "local_opt": "Türkiye (Yerel)",
        "news_error": "Haberler yüklenemedi. Hata:"
    }
}

# --- SIDEBAR LANGUAGE SELECTOR ---
with st.sidebar:
    st.title("Settings / Ayarlar")
    lang_choice = st.radio("Language / Dil", ["English", "Türkçe"])
    lang_code = "tr" if lang_choice == "Türkçe" else "en"
    t = TRANSLATIONS[lang_code]

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
        height: 320px;
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
    .news-meta {
        font-size: 11px;
        color: #95a5a6;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .news-title {
        font-size: 15px;
        font-weight: 700;
        color: #2c3e50;
        line-height: 1.3;
        margin-bottom: 10px;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    .news-summary {
        font-size: 13px;
        color: #555;
        line-height: 1.5;
        margin-bottom: 15px;
        flex-grow: 1;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
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

# --- DATA ENGINE ---
def get_supply_map_data(commodity):
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

def get_market_balance(commodity):
    market_data = {
        "Hazelnuts": [1.35, 1.28, "Million MT"],
        "Cocoa": [4.90, 5.05, "Million MT"],
        "Avocados": [9.20, 8.90, "Million MT"],
        "Coffee": [171.4, 169.5, "Million Bags"],
        "Wheat": [787.3, 790.2, "Million MT"],
        "Corn": [1222, 1208, "Million MT"],
        "Soybeans": [396, 382, "Million MT"],
        "Palm Oil": [79.5, 77.2, "Million MT"],
        "Cotton": [113.5, 115.8, "Million Bales"],
        "Sugar": [183.5, 180.2, "Million MT"],
    }
    return market_data.get(commodity, None)

def get_sector_insights(commodity, lang='en'):
    insights_en = {
        "Hazelnuts": [
            {"Sector": "Confectionery", "Share": 80, "Status": "🔴 Stressed"},
            {"Sector": "Snacks & Retail", "Share": 15, "Status": "🟡 Caution"},
            {"Sector": "Cosmetics", "Share": 5, "Status": "🟢 Stable"}
        ],
        "Cocoa": [
             {"Sector": "Chocolate Mfg", "Share": 65, "Status": "🔴 Critical"},
             {"Sector": "Cosmetics", "Share": 15, "Status": "🟢 Growing"}
        ],
        "Avocados": [
            {"Sector": "Fresh Retail", "Share": 85, "Status": "🟢 Bullish"},
            {"Sector": "Oil Processing", "Share": 10, "Status": "🟢 Emerging"}
        ],
        "Coffee": [
            {"Sector": "Specialty Roasters", "Share": 20, "Status": "🟠 Strained"},
            {"Sector": "Instant/Commercial", "Share": 45, "Status": "🟢 Stable"}
        ],
        "Wheat": [
            {"Sector": "Milling & Baking", "Share": 60, "Status": "🟡 Volatile"}
        ],
        "Corn": [
            {"Sector": "Animal Feed", "Share": 55, "Status": "🟢 Abundant"},
            {"Sector": "Ethanol", "Share": 35, "Status": "🟡 Risk"}
        ]
    }
    
    insights_tr = {
        "Hazelnuts": [
            {"Sector": "Şekerleme & Çikolata", "Share": 80, "Status": "🔴 Kritik"},
            {"Sector": "Perakende", "Share": 15, "Status": "🟡 Dikkat"},
            {"Sector": "Kozmetik", "Share": 5, "Status": "🟢 Stabil"}
        ],
        "Cocoa": [
             {"Sector": "Çikolata Üretimi", "Share": 65, "Status": "🔴 Kritik"},
             {"Sector": "Kozmetik", "Share": 15, "Status": "🟢 Büyüyor"}
        ],
        "Avocados": [
            {"Sector": "Perakende", "Share": 85, "Status": "🟢 Yükselişte"},
            {"Sector": "Yağ Üretimi", "Share": 10, "Status": "🟢 Gelişiyor"}
        ],
        "Coffee": [
            {"Sector": "Özel Kavurucular", "Share": 20, "Status": "🟠 Zorlu"},
            {"Sector": "Endüstriyel Kahve", "Share": 45, "Status": "🟢 Stabil"}
        ],
        "Wheat": [
            {"Sector": "Un ve Fırıncılık", "Share": 60, "Status": "🟡 Dalgalı"}
        ],
        "Corn": [
            {"Sector": "Hayvan Yemi", "Share": 55, "Status": "🟢 Bol"},
            {"Sector": "Etanol", "Share": 35, "Status": "🟡 Riskli"}
        ]
    }
    
    data_source = insights_tr if lang == 'tr' else insights_en
    
    default_en = [{"Sector": "General Market", "Share": 100, "Status": "⚪ Normal"}]
    default_tr = [{"Sector": "Genel Pazar", "Share": 100, "Status": "⚪ Normal"}]
    default = default_tr if lang == 'tr' else default_en

    return pd.DataFrame(data_source.get(commodity, default))

def get_commodity_facts(commodity, lang='en'):
    facts_en = {
        "Hazelnuts": {
            "producers": "Turkey (~70%), Italy, Azerbaijan.",
            "uses": "Confectionery, baking, oil extraction.",
            "desc": "The hazelnut is the nut of the hazel genus, widely used in pralines and spreads."
        },
        "Cocoa": {
            "producers": "Ivory Coast (~40%), Ghana, Indonesia.",
            "uses": "Chocolate, Cocoa butter, Cocoa powder.",
            "desc": "Cocoa beans are fermented seeds of Theobroma cacao, essential for chocolate."
        },
        "Avocados": {
            "producers": "Mexico, Peru, Indonesia.",
            "uses": "Fresh consumption, oil, cosmetics.",
            "desc": "The avocado is a tree native to the Americas, prized for its rich, oily fruit."
        },
        "Coffee": {
            "producers": "Brazil, Vietnam, Colombia.",
            "uses": "Beverage, flavoring, caffeine.",
            "desc": "Coffee is a brewed drink prepared from roasted coffee beans."
        },
        "Wheat": {
            "producers": "China, India, Russia, USA.",
            "uses": "Flour (bread, pasta), animal feed.",
            "desc": "Wheat is a grass cultivated worldwide for its seed, a cereal grain staple."
        },
        "Corn": {
            "producers": "USA, China, Brazil.",
            "uses": "Animal feed, ethanol, food.",
            "desc": "Maize, also known as corn, is a cereal grain first domesticated in Mexico."
        },
        "Cotton": {
            "producers": "China, India, USA.",
            "uses": "Textiles, oil, feed.",
            "desc": "Cotton is a soft, fluffy staple fiber that grows in a boll around seeds."
        },
        "Sugar": {
            "producers": "Brazil, India, EU.",
            "uses": "Sweetener, ethanol, preservatives.",
            "desc": "Sugar is the generic name for sweet-tasting, soluble carbohydrates."
        },
        "Soybeans": {
            "producers": "Brazil, USA, Argentina.",
            "uses": "Animal feed, oil, tofu.",
            "desc": "The soybean is a species of legume native to East Asia."
        },
        "Palm Oil": {
            "producers": "Indonesia, Malaysia.",
            "uses": "Cooking oil, biofuels, soap.",
            "desc": "Palm oil is an edible vegetable oil derived from the mesocarp of oil palms."
        }
    }

    facts_tr = {
        "Hazelnuts": {
            "producers": "Türkiye (~%70), İtalya, Azerbaycan.",
            "uses": "Şekerleme, pastacılık, yağ.",
            "desc": "Fındık, özellikle çikolata ve ezme yapımında kullanılan değerli bir sert kabuklu meyvedir."
        },
        "Cocoa": {
            "producers": "Fildişi Sahili (~%40), Gana, Endonezya.",
            "uses": "Çikolata, Kakao yağı, toz.",
            "desc": "Kakao çekirdekleri, çikolatanın ana maddesi olan Theobroma cacao ağacının tohumlarıdır."
        },
        "Avocados": {
            "producers": "Meksika, Peru, Endonezya.",
            "uses": "Taze tüketim, yağ, kozmetik.",
            "desc": "Avokado, Amerika kökenli, yağlı meyvesiyle bilinen bir ağaç türüdür."
        },
        "Coffee": {
            "producers": "Brezilya, Vietnam, Kolombiya.",
            "uses": "İçecek, aroma, kafein.",
            "desc": "Kahve, kavrulmuş kahve çekirdeklerinden demlenen popüler bir içecektir."
        },
        "Wheat": {
            "producers": "Çin, Hindistan, Rusya.",
            "uses": "Un (ekmek, makarna), yem.",
            "desc": "Buğday, tohumu için yetiştirilen ve dünya çapında temel besin olan bir tahıldır."
        },
        "Corn": {
            "producers": "ABD, Çin, Brezilya.",
            "uses": "Hayvan yemi, etanol, gıda.",
            "desc": "Mısır, ilk olarak Meksika'da evcilleştirilmiş bir tahıl bitkisidir."
        },
        "Cotton": {
            "producers": "Çin, Hindistan, ABD.",
            "uses": "Tekstil, yağ, yem.",
            "desc": "Pamuk, tohumları saran yumuşak, kabarık liflerden oluşan değerli bir bitkidir."
        },
        "Sugar": {
            "producers": "Brezilya, Hindistan, AB.",
            "uses": "Tatlandırıcı, etanol, koruyucu.",
            "desc": "Şeker, gıdalarda kullanılan tatlı ve çözünür karbonhidratların genel adıdır."
        },
        "Soybeans": {
            "producers": "Brezilya, ABD, Arjantin.",
            "uses": "Hayvan yemi, yağ, tofu.",
            "desc": "Soya fasulyesi, Doğu Asya kökenli, çok yönlü kullanıma sahip bir baklagildir."
        },
        "Palm Oil": {
            "producers": "Endonezya, Malezya.",
            "uses": "Yemeklik yağ, biyoyakıt, sabun.",
            "desc": "Palm yağı, yağ palmiyesinin meyvesinden elde edilen bitkisel bir yağdır."
        }
    }

    data_source = facts_tr if lang == 'tr' else facts_en
    
    default_en = {"producers": "Global", "uses": "Various", "desc": "Global commodity."}
    default_tr = {"producers": "Küresel", "uses": "Çeşitli", "desc": "Küresel emtia."}
    default = default_tr if lang == 'tr' else default_en
    
    return data_source.get(commodity, default)

# --- NEWS ENGINE ---
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
        
        raw_summary = entry.get('summary', '')
        clean_summary = ""
        if raw_summary:
            try:
                soup = BeautifulSoup(raw_summary, "html.parser")
                clean_summary = soup.get_text()
                if len(clean_summary) > 200:
                    clean_summary = clean_summary[:200] + "..."
            except Exception:
                clean_summary = raw_summary[:200]
        
        news_items.append({
            'title': entry.title,
            'link': entry.link,
            'published': date_str,
            'timestamp': published_parsed,
            'source': entry.source.title if 'source' in entry else 'Google News',
            'summary': clean_summary
        })
    news_items.sort(key=lambda x: x['timestamp'], reverse=True)
    return news_items[:12]

# --- MAIN APP LAYOUT ---

st.title(t["title"])
st.markdown(t["subtitle"])

# Global Controls
col1, col2 = st.columns([1, 1])
with col1:
    presets_en = ["Hazelnuts", "Cocoa", "Avocados", "Coffee", "Wheat", "Corn", "Soybeans", "Palm Oil", "Cotton", "Sugar", t["other_opt"]]
    choice = st.selectbox(t["select_lbl"], presets_en)
    
    if choice == t["other_opt"]:
        selected_commodity = st.text_input(t["custom_lbl"], value="Rice")
    else:
        selected_commodity = choice

with col2:
    default_idx = 1 if lang_code == 'tr' else 0
    region_toggle = st.radio(
        t["source_lbl"], 
        [t["global_opt"], t["local_opt"]], 
        index=default_idx,
        horizontal=True
    )
    region_code = "Turkey" if region_toggle == t["local_opt"] else "Global"

st.divider()

# --- TOP SECTION: INTELLIGENCE ---
c_map, c_table = st.columns([1.5, 1])

with c_map:
    st.subheader(f"{t['supply_zones']}: {selected_commodity}")
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
        st.warning("Map data not available.")

with c_table:
    st.subheader(t["sector_insights"])
    sector_df = get_sector_insights(selected_commodity, lang=lang_code)
    st.dataframe(
        sector_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Health", help="Status"),
            "Share": st.column_config.ProgressColumn(
                "Share", 
                format="%d%%", 
                min_value=0, 
                max_value=100
            ),
        }
    )
    
    st.write("")
    st.markdown(f"**{t['market_balance']}**")
    market_stats = get_market_balance(selected_commodity)
    
    if market_stats:
        m1, m2, m3 = st.columns(3)
        prod, cons, unit = market_stats
        balance = prod - cons
        m1.metric(t["production"], f"{prod}", unit)
        m2.metric(t["consumption"], f"{cons}", unit)
        m3.metric(t["balance"], f"{balance:+.2f}", t["surplus"], delta_color="normal")
    else:
        st.caption("N/A")

    st.write("")
    st.subheader(t["fact_sheet"])
    facts = get_commodity_facts(selected_commodity, lang=lang_code)
    
    html_content = textwrap.dedent(f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #eee;">
            <div style="font-size: 14px; color: #555; margin-bottom: 8px;">
                <strong>{t['sci_desc']}</strong><br>
                <span style="font-style: italic;">{facts['desc']}</span>
            </div>
            <div style="font-size: 14px; color: #555; margin-bottom: 8px;">
                <strong>{t['top_prod']}</strong> {facts['producers']}
            </div>
            <div style="font-size: 14px; color: #555; margin-bottom: 8px;">
                <strong>{t['uses']}</strong> {facts['uses']}
            </div>
             <div style="font-size: 12px; color: #999; margin-top: 10px; border-top: 1px solid #ddd; padding-top: 5px;">
                {t['sources_foot']}
            </div>
        </div>
    """)
    st.markdown(html_content, unsafe_allow_html=True)

st.divider()

# --- BOTTOM SECTION: NEWS ---
st.subheader(f"{t['news_header']}: {selected_commodity}")

try:
    with st.spinner(t["loading"]):
        news_data = fetch_news(selected_commodity, region=region_code)
    
    if not news_data:
        st.info(t["no_news"])
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
                                <div class="news-summary">{item['summary']}</div>
                            </div>
                            <a href="{item['link']}" target="_blank" class="read-more-btn">
                                {t['read_btn']}
                            </a>
                        </div>
                    """)
                    st.markdown(html_content, unsafe_allow_html=True)       
except Exception as e:
    st.error(f"{t['news_error']} {e}")
