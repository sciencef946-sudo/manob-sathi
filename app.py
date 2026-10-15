import streamlit as st
import pandas as pd
import json
import os
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="মানব সাথি — স্মার্ট শপ ফাইন্ডার ও স্বাস্থ্য সঙ্গী",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
* { font-family: 'Hind Siliguri', sans-serif; }
.stApp { background: linear-gradient(135deg, #1f4068 0%, #162447 100%); }
.main .block-container { background: #ffffff; border-radius: 20px; padding: 2rem; box-shadow: 0 15px 40px rgba(0,0,0,0.3); }
.app-header { text-align: center; padding: 2rem; background: linear-gradient(135deg, #0f3460, #1a1a2e); border-radius: 15px; margin-bottom: 2rem; color: white; }
.app-title { font-size: 2.5rem; font-weight: 700; margin: 0; color: #fff; }
.app-subtitle { color: #e94560; font-size: 1.1rem; margin-top: 0.5rem; font-weight: 600; }
.result-card { background: #f8f9fa; border-radius: 14px; padding: 1.2rem; margin: 1rem 0; border-left: 6px solid #e94560; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
.result-card p, .result-card span { color: #2c3e50 !important; }
.complaint-card { background: #fff5f5; border-radius: 12px; padding: 1.2rem; margin: 1rem 0; border-left: 6px solid #e74c3c; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
.complaint-card p, .complaint-card strong { color: #2c3e50 !important; }
.herbal-card { background: #f0fff4; border-radius: 10px; padding: 1rem; margin-bottom: 0.8rem; border-left: 5px solid #27ae60; border: 1px solid #c6efce; }
.herbal-card h4 { margin: 0 0 6px 0; color: #1e8449; }
.herbal-card p { margin: 2px 0; color: #2c3e50 !important; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_database():
    file_name = 'Unique_Named_Bangla_Store_Distribution.xlsx'
    if os.path.exists(file_name):
        xls = pd.ExcelFile(file_name)
        df_mapping = pd.read_excel(xls, 'প্রোডাক্ট ও দোকান ম্যাপিং')
        df_stores = pd.read_excel(xls, 'সকল ৩২০টি দোকানের তালিকা')
        return df_stores, df_mapping
    return None, None

df_stores, df_mapping = load_database()

st.markdown("""
<div class="app-header">
    <div style="font-size:3rem;">🛡️</div>
    <div class="app-title">মানব সাথি</div>
    <div class="app-subtitle">এলাকা ও পণ্যভিত্তিক দোকান ফাইন্ডার, প্রাইজ মনিটরিং ও স্বাস্থ্য সঙ্গী</div>
    <div style="color:#f1c40f; font-size:0.9rem; margin-top:0.4rem;">Created by Kaliagonj Naziraton High School (SOUNDARJYA)</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔍 পণ্য ও লাইভ ম্যাপ",
    "🗺️ জোন ম্যাপ",
    "📋 ৩২০ দোকানের তালিকা",
    "📊 বাজার দর তুলনা",
    "🚨 ভোক্তা অভিযোগ",
    "🏥 স্বাস্থ্য সঙ্গী ও ভেষজ",
    "🏛️ কর্মকর্তা প্যানেল"
])

with tab1:
    st.markdown("## 🔍 সুনির্দিষ্ট এলাকা ও পণ্যভিত্তিক দোকান এবং লোকেশন ম্যাপ")
    st.info("নিচে থেকে আপনার **এলাকা** এবং কাঙ্ক্ষিত **পণ্য** সিলেক্ট করুন। নির্বাচিত পণ্যের সব ইনফরমেশন দেখানোর পাশাপাশি নিচের ম্যাপে দোকানগুলোর লোকেশন পিন পয়েন্ট করে দেখানো হবে।")
    
    if df_mapping is not None:
        all_areas = sorted(df_mapping['এলাকা'].dropna().unique().tolist())
        all_products = sorted(df_mapping['প্রোডাক্টের নাম'].dropna().unique().tolist())
        
        col1, col2 = st.columns(2)
        with col1:
            selected_area = st.selectbox("১. এলাকা নির্বাচন করুন:", all_areas, key="sel_area")
        with col2:
            selected_product = st.selectbox("২. পণ্যের নাম নির্বাচন করুন:", all_products, key="sel_prod")
            
        result_df = df_mapping[
            (df_mapping['এলাকা'].astype(str).str.strip() == str(selected_area).strip()) & 
            (df_mapping['প্রোডাক্টের নাম'].astype(str).str.strip() == str(selected_product).strip())
        ].copy()

        st.markdown(f"### 🎯 ফলাফল: **{selected_area}** এলাকায় **{selected_product}** পাওয়া যায় এমন **{len(result_df)}টি** দোকান:")

        if len(result_df) > 0:
            np.random.seed(100)
            base_lat, base_lon = 25.85, 88.60
            result_df['lat'] = base_lat + np.random.uniform(-0.03, 0.03, len(result_df))
            result_df['lon'] = base_lon + np.random.uniform(-0.03, 0.03, len(result_df))

            st.markdown("#### 🗺️ সার্চকৃত দোকানগুলোর ভার্চুয়াল ম্যাপ লোকেশন:")
            st.map(result_df, latitude='lat', longitude='lon', size=40, color='#e94560')

            st.markdown("#### 🏪 দোকানসমূহের পূর্ণাঙ্গ বিবরণ:")
            for idx, row in result_df.iterrows():
                st.markdown(f"""
                <div class="result-card">
                    <h3 style="margin:0; color:#0f3460;">🏪 {row['দোকানের নাম']} <span style="font-size:0.8rem; color:#e94560; float:right;">আইডি: {row['দোকান আইডি']}</span></h3>
                    <hr style="margin:8px 0; border:0; border-top:1px solid #ddd;">
                    <p style="margin:4px 0;">📦 <strong>পণ্য:</strong> {row['প্রোডাক্টের নাম']} ({row['ওজন/সাইজ']})</p>
                    <p style="margin:4px 0;">🏷️ <strong>ব্র্যান্ড / কোম্পানি:</strong> {row['ব্র্যান্ড']} ({row['কোম্পানি']})</p>
                    <p style="margin:4px 0;">📍 <strong>দোকানের ঠিকানা:</strong> {row['ঠিকানা']}</p>
                    <p style="margin:4px 0;">🏙️ <strong>এলাকা:</strong> {row['এলাকা']} | 📂 <strong>ক্যাটাগরি:</strong> {row['ক্যাটাগরি']}</p>
                    <p style="margin:4px 0;">📞 <strong>যোগাযোগ নম্বর:</strong> <span style="color:#c0392b; font-weight:bold; font-size:1.1rem;">{row['যোগাযোগ নম্বর']}</span></p>
                    <div style="margin-top:10px;">
                        <span style="background:#27ae60; color:white; padding:4px 12px; border-radius:6px; font-size:0.85rem; font-weight:600;">🟢 স্টকে উপলব্ধ</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ এই এলাকায় নির্দিষ্ট এই পণ্যটি বিক্রয় করে এমন কোনো দোকান আমাদের ডাটাবেজে নেই।")
    else:
        st.error("⚠️ ডাটাবেজ ফাইল পাওয়া যায়নি।")

with tab2:
    st.markdown("## 🗺️ এলাকার পূর্ণাঙ্গ জোন ম্যাপ ও দোকানসমূহ")
    if df_stores is not None:
        map_area = st.selectbox("এলাকা সিলেক্ট করুন:", sorted(df_stores['এলাকা'].dropna().unique()), key="virtual_map_area")
        area_stores = df_stores[df_stores['এলাকা'] == map_area].copy()
        
        np.random.seed(42)
        area_stores['lat'] = 25.85 + np.random.uniform(-0.05, 0.05, len(area_stores))
        area_stores['lon'] = 88.60 + np.random.uniform(-0.05, 0.05, len(area_stores))
        
        st.markdown(f"### 📍 **{map_area}** এলাকার সকল দোকানের জোন ম্যাপ ({len(area_stores)}টি দোকান)")
        st.map(area_stores, latitude='lat', longitude='lon', size=30, color='#1f4068')
        
        st.dataframe(area_stores[['দোকান আইডি', 'দোকানের নাম', 'ঠিকানা', 'যোগাযোগ নম্বর', 'ক্যাটাগরি']], use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ ম্যাপ ডাটা পাওয়া যায়নি।")

with tab3:
    st.markdown("## 📋 সকল ৩২০টি দোকানের পূর্ণাঙ্গ তালিকা")
    if df_stores is not None:
        area_filter = st.selectbox("এলাকা অনুযায়ী ফিল্টার করুন:", ["সব এলাকা"] + list(df_stores['এলাকা'].dropna().unique()), key="store_filter_area")
        stores_to_show = df_stores if area_filter == "সব এলাকা" else df_stores[df_stores['এলাকা'] == area_filter]
        
        st.markdown(f"**তালিকাভুক্ত দোকান সংখ্যা: {len(stores_to_show)}টি**")
        st.dataframe(stores_to_show, use_container_width=True, hide_index=True)
    else:
        st.error("⚠️ স্টোর ডাটাবেজ ফাইল পাওয়া যায়নি।")

with tab4:
    st.markdown("## 📊 বাজার দর তুলনা ও প্রাইজ মনিটরিং ট্র্যাকার")
    st.info("জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তরের নির্ধারিত মূল্য তালিকার সাথে খুচরা বাজারের বর্তমান দামের রিয়েল-টাইম তুলনা।")
    
    price_data = [
        {"product": "নাজিরশাইল চাল (কেজি)", "gov_price": "৬৮-৭০ টাকা", "market_price": "৭২ টাকা", "status": "⚠️ অতিরিক্ত মূল্য"},
        {"product": "সয়াবিন তেল (লিটার)", "gov_price": "১৭৫ টাকা", "market_price": "১৭৫ টাকা", "status": "✅ ন্যায্য মূল্য"},
        {"product": "মসুর ডাল (দেশি কেজি)", "gov_price": "১৪০ টাকা", "market_price": "১৪৫ টাকা", "status": "⚠️ সামান্য বেশি"},
        {"product": "বোতলজাত পানি (১ লিটার)", "gov_price": "২০ টাকা", "market_price": "২০ টাকা", "status": "✅ ন্যায্য মূল্য"},
        {"product": "চিনি (খোলা কেজি)", "gov_price": "১৩৫ টাকা", "market_price": "১৪০ টাকা", "status": "⚠️ অতিরিক্ত মূল্য"},
        {"product": "ময়দা (প্যাকেট কেজি)", "gov_price": "৬৫ টাকা", "market_price": "৬৫ টাকা", "status": "✅ ন্যায্য মূল্য"}
    ]
    df_price = pd.DataFrame(price_data)
    st.dataframe(df_price, use_container_width=True, hide_index=True)
    
    st.markdown("#### 💡 বাজার মনিটরিং সতর্কতা:")
    st.warning("কোনো বিক্রেতা নির্ধারিত সরকারি মূল্যের চেয়ে বেশি দাম রাখলে তাৎক্ষণিকভাবে **'ভোক্তা অভিযোগ'** ট্যাবে গিয়ে অভিযোগ দাখিল করুন।")

with tab5:
    st.markdown("## 🚨 ভোক্তা অধিকার ও দুর্নীতি অভিযোগ ব্যবস্থাপনা")
    with st.form("complaint_form_fixed"):
        c_shop = st.text_input("দোকানের নাম ও ঠিকানা:")
        c_area = st.selectbox("এলাকা:", ["বোদা", "পঞ্চগড়", "ময়দানদীঘি", "ঠাকুরগাঁও"], key="comp_area_fixed")
        c_desc = st.text_area("অভিযোগের বিবরণ (যেমন: অধিক মূল্য রাখা বা মেয়াদোত্তীর্ণ পণ্য):", height=120)
        submitted = st.form_submit_button("🚨 সরকারি প্যানেলে অভিযোগ সাবমিট করুন", type="primary")

        if submitted and c_shop and c_desc:
            complaint_data = {
                "shop": c_shop,
                "area": c_area,
                "details": c_desc,
                "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
            }
            complaints = []
            if os.path.exists("complaints.json"):
                with open("complaints.json", "r", encoding="utf-8") as f:
                    try:
                        complaints = json.load(f)
                    except:
                        complaints = []
            complaints.insert(0, complaint_data)
            with open("complaints.json", "w", encoding="utf-8") as f:
                json.dump(complaints, f, ensure_ascii=False, indent=2)
            st.balloons()
            st.success("✅ অভিযোগ সফলভাবে সরকারি ড্যাশবোর্ডে প্রেরণ করা হয়েছে!")

with tab6:
    st.markdown("## 🏥 স্বাস্থ্য সঙ্গী ও ১৫+ নিত্যদিনের রোগের ভেষজ ঘরোয়া চিকিৎসা")
    
    # BMI & BP Section
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("### ⚖️ BMI ক্যালকুলেটর")
        w = st.number_input("ওজন (কেজি):", 10.0, 200.0, 60.0, 0.5, key="bmi_w")
        h = st.number_input("উচ্চতা (সেমি):", 50.0, 250.0, 160.0, 0.5, key="bmi_h")
        if st.button("BMI হিসাব করুন", key="bmi_btn"):
            bmi = w / ((h/100)**2)
            st.info(f"আপনার BMI: **{bmi:.1f}**")
    with col_h2:
        st.markdown("### 🩺 রক্তচাপ (BP) মূল্যায়ন")
        bp_s = st.number_input("সিস্টোলিক:", 60, 250, 120, key="bp_s")
        bp_d = st.number_input("ডায়াস্টোলিক:", 40, 150, 80, key="bp_d")
        if st.button("প্রেশার যাচাই করুন", key="bp_btn"):
            if bp_s <= 120 and bp_d <= 80:
                st.success("স্বাভাবিক রক্তচাপ ✅")
            else:
                st.warning("রক্তচাপ স্বাভাবিকের চেয়ে বেশি/কম ⚠️")

    st.markdown("---")
    st.markdown("### 🌿 সাধারণ ১৫+ টি রোগের ভেষজ ও প্রাকৃতি সমাধান নির্দেশিকা")
    
    herbal_remedies = [
        {"disease": "১. সর্দি, কাশি ও গলার খুশখুশ", "remedy": "তুলসী পাতার রস, আদা ও মধু একসাথে মিশিয়ে হালকা গরম করে দিনে ২-৩ বার পান করুন।", "herb": "তুলসী, আদা, মধু"},
        {"disease": "২. গ্যাস্ট্রিক ও অ্যাসিডিটি", "remedy": "খাওয়ার পর ১ চামচ মৌরি অথবা ইসবগুলের ভুষি পানিতে ভিজিয়ে পান করুন। কাঁচা লবঙ্গ চিবিয়ে খেলেও দ্রুত আরাম মেলে।", "herb": "মৌরি, লবঙ্গ, ইসবগুল"},
        {"disease": "৩. বদহজম ও পেট ফাঁপা", "remedy": "এক গ্লাস ঈষদুষ্ণ পানিতে সামান্য জোয়ান গুঁড়ো ও বিট লবণ মিশিয়ে খেলে পেটের অস্বস্তি দূর হয়।", "herb": "জোয়ান, বিট লবণ"},
        {"disease": "৪. সাধারণ মাথাব্যথা", "remedy": "মাথায় পুদিনা পাতা বা আদার রস হালকা করে ম্যাসাজ করুন এবং আদা চা পান করুন।", "herb": "পুদিনা পাতা, আদা"},
        {"disease": "৫. কোষ্ঠকাঠিন্য", "remedy": "রাতে ঘুমানোর আগে এক গ্লাস হালকা গরম পানিতে ১-২ চামচ ইসবগুলের ভুষি বা ত্রফলা গুঁড়ো মিশিয়ে পান করুন।", "herb": "ত্রফলা, ইসবগুল"},
        {"disease": "৬. মানসিক চাপ ও অনিদ্রা", "remedy": "ঘুমানোর আগে এক কাপ গরম দুধের সাথে সামান্য জয়ফল গুঁড়ো অথবা ক্যামোমাইল চা পান করুন।", "herb": "জয়ফল, ক্যামোমাইল"},
        {"disease": "৭. দাঁত ও মাড়ির ব্যথা", "remedy": "আক্রান্ত দাঁতের গোড়ায় একটি লবঙ্গ চেপে রাখুন অথবা লবঙ্গের তেল তুলো দিয়ে লাগান।", "herb": "লবঙ্গ"},
        {"disease": "৮. উচ্চ রক্তচাপ নিয়ন্ত্রণ", "remedy": "প্রতিদিন সকালে খালি পেটে ১-২ কোয়া কাঁচা রসুন খেলে রক্তচাপ ও কোলেস্টেরল নিয়ন্ত্রণে থাকে।", "herb": "রসুন"},
        {"disease": "৯. মেদ ও ওজন কমানো", "remedy": "সকালে খালি পেটে এক গ্লাস হালকা গরম পানিতে অর্ধেকটা লেবুর রস ও ১ চামচ মধু মিশিয়ে পান করুন।", "herb": "লেবু, মধু"},
        {"disease": "১০. কৃমির সমস্যা", "remedy": "সকালে খালি পেটে কালমেঘ পাতার রস অথবা কাঁচা পেঁপের আঠা পানির সাথে মিশিয়ে খেলে কৃমি দূর হয়।", "herb": "কালমেঘ পাতা, পেঁপে"},
        {"disease": "১১. চর্মরোগ ও চুলকানি", "remedy": "কাঁচা হলুদ ও নিম পাতা বেটে আক্রান্ত স্থানে লাগালে যে কোনো ব্যাকটেরিয়া বা ফাঙ্গাল ইনফেকশন দূর হয়।", "herb": "নিম পাতা, হলুদ"},
        {"disease": "১২. প্রস্রাবের জ্বালাপোড়া", "remedy": "ধনে বীজ সারারাত পানিতে ভিজিয়ে রেখে সকালে সেই পানি ছেঁকে খেলে বা ডাবের পানি পান করলে দ্রুত আরাম মেলে।", "herb": "ধনে বীজ, ডাবের পানি"},
        {"disease": "১৩. চুল পড়া রোধ ও ড্যান্ড্রফ", "remedy": "আমলকী ও রিঠা গুঁড়ো পানিতে ফুটিয়ে সেই পানি দিয়ে চুল ধুলে চুল পড়া বন্ধ হয় এবং গোড়া শক্ত হয়।", "herb": "আমলকী, রিঠা"},
        {"disease": "১৪. রক্তস্বল্পতা (অ্যানিমিয়া)", "remedy": "প্রতিদিন কুল, ডালিম, খুরমা খেজুর এবং পালং শাক খেলে রক্তে হিমোগ্লোবিন দ্রুত বাড়ে।", "herb": "ডালিম, খেজুর, পালং শাক"},
        {"disease": "১৫. মুখের দুর্গন্ধ", "remedy": "খাওয়ার পর দারুচিনি বা এলাচ চিবিয়ে খেলে মুখের দুর্গন্ধ সৃষ্টিকারী ব্যাকটেরিয়া ধ্বংস হয়।", "herb": "দারুচিনি, এলাচ"}
    ]
    
    col_search, _ = st.columns([2, 1])
    with col_search:
        search_disease = st.text_input("🔍 কোনো নির্দিষ্ট রোগ বা ভেষজ উপাদান খুঁজুন:", placeholder="যেমন: গ্যাস্ট্রিক, কাশি, নিম পাতা...")

    for item in herbal_remedies:
        if search_disease == "" or (search_disease.lower() in item['disease'].lower() or search_disease.lower() in item['herb'].lower()):
            st.markdown(f"""
            <div class="herbal-card">
                <h4>{item['disease']}</h4>
                <p>🌿 <strong>প্রধান ভেষজ উপাদান:</strong> {item['herb']}</p>
                <p>💡 <strong>ঘরোয়া প্রস্তুতপ্রণালী:</strong> {item['remedy']}</p>
            </div>
            """, unsafe_allow_html=True)

with tab7:
    st.markdown("## 🏛️ সরকারি কর্মকর্তা ও এডমিন লগইন প্যানেল")
    st.info("এই ট্যাবটি শুধুমাত্র জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তরের অনুমোদিত কর্মকর্তাদের জন্য সংরক্ষিত।")
    
    officer_pass = st.text_input("অফিসার সিক্রেট পাসওয়ার্ড প্রবেশ করান:", type="password", key="admin_secret_key")
    
    if officer_pass == "admin123" or officer_pass == "9999":
        st.success("✅ লগইন সফল হয়েছে! সরকারি ড্যাশবোর্ড সক্রিয়।")
        
        complaints_file = "complaints.json"
        if os.path.exists(complaints_file):
            with open(complaints_file, "r", encoding="utf-8") as f:
                try:
                    comp_list = json.load(f)
                except:
                    comp_list = []
                    
            st.markdown(f"### 📥 মোট প্রাপ্ত অভিযোগ: **{len(comp_list)}টি**")
            
            if len(comp_list) > 0:
                for idx, c in enumerate(comp_list):
                    st.markdown(f"""
                    <div class="complaint-card">
                        <h3 style="margin:0; color:#c0392b;">🚨 অভিযোগ #{idx+1} — দোকান: {c.get('shop')}</h3>
                        <hr style="margin:6px 0; border:0; border-top:1px solid #ddd;">
                        <p style="margin:3px 0;">🏙️ <strong>এলাকা:</strong> {c.get('area')}</p>
                        <p style="margin:3px 0;">📝 <strong>বিবরণ:</strong> {c.get('details')}</p>
                        <p style="margin:3px 0; color:#7f8c8d; font-size:0.85rem;">⏱️ <strong>সময়:</strong> {c.get('time')}</p>
                        <div style="margin-top:8px;">
                            <span style="background:#e74c3c; color:white; padding:3px 10px; border-radius:4px; font-size:0.8rem; font-weight:600;">⚠️ তদন্তাধীন</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 বর্তমানে কোনো নতুন অভিযোগ জমা নেই।")
        else:
            st.info("📭 এখন পর্যন্ত কোনো অভিযোগ জমা হয়নি।")
    else:
        st.warning("🔒 ড্যাশবোর্ড দেখতে সঠিক সিক্রেট পাসওয়ার্ড প্রদান করুন। (মেলার জন্য পাসওয়ার্ড দিন: `admin123`)")

st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:1.2rem;background:linear-gradient(135deg,#0f3460,#1a1a2e);border-radius:14px;color:white;">
    <strong>🛡️ মানব সাথি ১.০ (স্মার্ট শপ ফাইন্ডার, প্রাইজ মনিটরিং ও গভঃ ড্যাশবোর্ড)</strong><br>
    <small>Created by Kaliagonj Naziraton High School (SOUNDARJYA)</small>
</div>
""", unsafe_allow_html=True)
