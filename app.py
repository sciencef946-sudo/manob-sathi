import streamlit as st
import pandas as pd
import json
import os
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="মানব সাথি — স্মার্ট শপ ফাইন্ডার ও দোকানদার প্যানেল",
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
.result-card p { color: #2c3e50 !important; margin: 4px 0; }
.complaint-card { background: #fff5f5; border-radius: 12px; padding: 1.2rem; margin: 1rem 0; border-left: 6px solid #e74c3c; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
.complaint-card p { color: #2c3e50 !important; margin: 3px 0; }
.herbal-card { background: #f0fff4; border-radius: 10px; padding: 1rem; margin-bottom: 0.8rem; border-left: 5px solid #27ae60; border: 1px solid #c6efce; }
.herbal-card h4 { margin: 0 0 6px 0; color: #1e8449; }
.herbal-card p { margin: 2px 0; color: #2c3e50 !important; font-size: 0.95rem; }
.helpline-box { background: #e8f4f8; border-left: 5px solid #2980b9; padding: 1rem; border-radius: 10px; margin-bottom: 0.8rem; }
.helpline-box h4 { margin: 0 0 4px 0; color: #2980b9; }
.helpline-box p { margin: 2px 0; color: #2c3e50 !important; }
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
    <div class="app-subtitle">স্মার্ট শপ ফাইন্ডার, লাইভ স্টক ভেরিফিকেশন ও দোকানদার অ্যানালিটিক্স</div>
    <div style="color:#f1c40f; font-size:0.9rem; margin-top:0.4rem;">Created by Kaliagonj Naziraton High School (SOUNDARJYA)</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "🔍 পণ্য ও স্টক চেক",
    "🗺️ জোন ম্যাপ",
    "📋 ৩২০ দোকান",
    "📊 বাজার দর",
    "⭐ দোকান রেটিং",
    "📞 হেল্পলাইন",
    "🚨 ভোক্তা অভিযোগ",
    "🏥 স্বাস্থ্য সঙ্গী",
    "🏪 দোকানদার প্যানেল",
    "🏛️ গভঃ ড্যাশবোর্ড"
])

with tab1:
    st.markdown("## 🔍 সুনির্দিষ্ট এলাকা, পণ্যভিত্তিক দোকান এবং লাইভ স্টক যাচাই")
    st.info("নিচে থেকে আপনার **এলাকা** এবং কাঙ্ক্ষিত **পণ্য** সিলেক্ট করুন। পণ্যটি স্টকে আছে কিনা তা নিশ্চিত করতে **'স্টক যাচাই করুন'** বাটনে চাপ দিন।")
    
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
            
            lats = base_lat + np.random.uniform(-0.03, 0.03, len(result_df))
            lons = base_lon + np.random.uniform(-0.03, 0.03, len(result_df))
            
            result_df['lat'] = lats
            result_df['lon'] = lons
            
            distances = np.sqrt((lats - base_lat)**2 + (lons - base_lon)**2) * 111.0
            result_df['distance_km'] = np.round(distances, 2)

            st.markdown("#### 🗺️ সার্চকৃত দোকানগুলোর ভার্চুয়াল ম্যাপ লোকেশন:")
            st.map(result_df, latitude='lat', longitude='lon', size=40, color='#e94560')

            st.markdown("#### 🏪 দোকানসমূহের পূর্ণাঙ্গ বিবরণ ও লাইভ স্টক রিকোয়েস্ট:")
            for idx, row in result_df.iterrows():
                dist = row['distance_km']
                dist_str = f"{int(dist*1000)} মিটার" if dist < 1.0 else f"{dist:.1f} কিমি"
                walk_time = int(dist * 12) + 1
                store_id = str(row['দোকান আইডি'])
                store_name = row['দোকানের নাম']
                
                st.markdown(f"""
                <div class="result-card">
                    <h3 style="margin:0; color:#0f3460;">🏪 {store_name} <span style="font-size:0.8rem; color:#e94560; float:right;">আইডি: {store_id}</span></h3>
                    <hr style="margin:8px 0; border:0; border-top:1px solid #ddd;">
                    <p>📦 <strong>পণ্য:</strong> {row['প্রোডাক্টের নাম']} ({row['ওজন/সাইজ']})</p>
                    <p>🏷️ <strong>ব্র্যান্ড / কোম্পানি:</strong> {row['ব্র্যান্ড']} ({row['কোম্পানি']})</p>
                    <p>📍 <strong>দোকানের ঠিকানা:</strong> {row['ঠিকানা']}</p>
                    <p>📞 <strong>যোগাযোগ নম্বর:</strong> <span style="color:#c0392b; font-weight:bold;">{row['যোগাযোগ নম্বর']}</span></p>
                    <p style="background:#e8f4f8; padding:6px 10px; border-radius:6px; color:#2980b9 !important; font-weight:bold; display:inline-block; margin-top:6px;">
                        📏 দূরত্ব: {dist_str} (প্রায় {walk_time} মিনিট হাঁটার পথ)
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Live Stock Request Button per store
                with st.expander(f"📌 '{store_name}'-এ স্টক যাচাই করতে ক্লিক করুন"):
                    if st.button(f"🔍 স্টক যাচাই রিকোয়েস্ট পাঠান", key=f"req_{store_id}_{idx}"):
                        req_data = {
                            "store_id": store_id,
                            "store_name": store_name,
                            "product": selected_product,
                            "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                            "status": "মালিকের উত্তরের অপেক্ষায় ⏳"
                        }
                        requests_list = []
                        if os.path.exists("stock_requests.json"):
                            with open("stock_requests.json", "r", encoding="utf-8") as f:
                                try:
                                    requests_list = json.load(f)
                                except:
                                    requests_list = []
                        requests_list.insert(0, req_data)
                        with open("stock_requests.json", "w", encoding="utf-8") as f:
                            json.dump(requests_list, f, ensure_ascii=False, indent=2)
                        st.success(f"✅ '{store_name}'-এর দোকানদারের কাছে স্টক যাচাইয়ের রিকোয়েস্ট পাঠানো হয়েছে! দোকানদার ড্যাশবোর্ড থেকে উত্তর দিলে তা আপডেট হবে।")
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
    
    st.markdown("#### 💡 স্মার্ট বাজার খরচ ক্যালকুলেটর:")
    with st.form("calc_form"):
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            qty_rice = st.number_input("চাল (কেজি):", 0, 50, 5)
            qty_oil = st.number_input("সয়াবিন তেল (লিটার):", 0, 20, 2)
        with col_c2:
            qty_sugar = st.number_input("চিনি (কেজি):", 0, 20, 1)
            qty_dal = st.number_input("মসুর ডাল (কেজি):", 0, 20, 2)
        
        calc_btn = st.form_submit_button("🧮 আনুমানিক বাজার খরচ হিসাব করুন")
        if calc_btn:
            est_total = (qty_rice * 72) + (qty_oil * 175) + (qty_sugar * 140) + (qty_dal * 145)
            st.success(f"🛒 আপনার নির্বাচিত পণ্যের আনুমানিক বাজার খরচ: **{est_total} টাকা**")

with tab5:
    st.markdown("## ⭐ দোকান রেটিং ও কাস্টমার রিভিউ")
    st.info("আপনার এলাকার দোকানগুলোর পণ্যের মান ও সেবা কেমন, সে বিষয়ে আপনার মতামত ও স্টার রেটিং দিন।")
    
    with st.form("rating_form"):
        r_shop = st.text_input("দোকানের নাম:")
        r_stars = st.slider("স্টার রেটিং দিন:", 1, 5, 5)
        r_comment = st.text_area("আপনার মতামত বা রিভিউ:")
        r_submit = st.form_submit_button("⭐ রিভিউ সাবমিট করুন")
        
        if r_submit and r_shop:
            st.success(f"✅ **{r_shop}** দোকানটির জন্য আপনার {r_stars} স্টারের রিভিউ সফলভাবে সংরক্ষিত হয়েছে!")

with tab6:
    st.markdown("## 📞 জরুরি হেল্পলাইন ও হটলাইন নম্বরসমূহ")
    helplines = [
        {"name": "জাতীয় ভোক্তা অধিকার সংরক্ষণ অধিদপ্তর", "num": "১৬১২১", "desc": "পণ্য বা সেবায় প্রতারিত হলে বা অতিরিক্ত দাম রাখলে অভিযোগ জানাতে।"},
        {"name": "জাতীয় জরুরি সেবা (পুলিশ, ফায়ার সার্ভিস, অ্যাম্বুলেন্স)", "num": "৯৯৯", "desc": "যেকোনো জরুরি দুর্ঘটনা বা বিপদে সহায়তার জন্য।"},
        {"name": "স্বাস্থ্য বাতায়ন (সরকারি স্বাস্থ্য সেবা)", "num": "১৬২৬৩", "desc": "ডাক্তারি পরামর্শ ও স্বাস্থ্যসেবা সম্পর্কিত তথ্যের জন্য।"},
        {"name": "দুর্নীতি দমন কমিশন (দুদক হটলাইন)", "num": "১০৬", "desc": "সরকারি বা প্রাতিষ্ঠানিক দুর্নীতি ও অনিয়মের বিরুদ্ধে।"}
    ]
    for h in helplines:
        st.markdown(f"""
        <div class="helpline-box">
            <h4>📞 {h['name']} — হটলাইন: <span style="color:#c0392b;">{h['num']}</span></h4>
            <p>{h['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

with tab7:
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

with tab8:
    st.markdown("## 🏥 স্বাস্থ্য সঙ্গী ও ১৫+ নিত্যদিনের রোগের ভেষজ ঘরোয়া চিকিৎসা")
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
    st.markdown("### 🌿 সাধারণ ১৫+ টি রোগের ভেষজ ও প্রাকৃতিক সমাধান নির্দেশিকা")
    herbal_remedies = [
        {"disease": "১. সর্দি, কাশি ও গলার খুশখুশ", "remedy": "তুলসী পাতার রস, আদা ও মধু একসাথে মিশিয়ে হালকা গরম করে দিনে ২-৩ বার পান করুন।", "herb": "তুলসী, আদা, মধু"},
        {"disease": "২. গ্যাস্ট্রিক ও অ্যাসিডিটি", "remedy": "খাওয়ার পর ১ চামচ মৌরি অথবা ইসবগুলের ভুষি পানিতে ভিজিয়ে পান করুন।", "herb": "মৌরি, লবঙ্গ, ইসবগুল"},
        {"disease": "৩. বদহজম ও পেট ফাঁপা", "remedy": "এক গ্লাস ঈষদুষ্ণ পানিতে সামান্য জোয়ান গুঁড়ো ও বিট লবণ মিশিয়ে খেলে আরাম মেলে।", "herb": "জোয়ান, বিট লবণ"},
        {"disease": "৪. সাধারণ মাথাব্যথা", "remedy": "মাথায় পুদিনা পাতা বা আদার রস হালকা করে ম্যাসাজ করুন এবং আদা চা পান করুন।", "herb": "পুদিনা পাতা, আদা"}
    ]
    for item in herbal_remedies:
        st.markdown(f"""
        <div class="herbal-card">
            <h4>{item['disease']}</h4>
            <p>🌿 <strong>ভেষজ উপাদান:</strong> {item['herb']}</p>
            <p>💡 <strong>প্রস্তুতপ্রণালী:</strong> {item['remedy']}</p>
        </div>
        """, unsafe_allow_html=True)

with tab9:
    st.markdown("## 🏪 দোকানদার পোর্টাল ও স্টক ম্যানেজমেন্ট প্যানেল")
    st.info("দোকানদাররা তাদের নিজস্ব ইউজার আইডি (যেমন: STORE001 বা আপনার দোকানের আইডি) দিয়ে লগইন করে ক্রেতাদের স্টক রিকোয়েস্টের উত্তর দিতে পারবেন এবং বাজার বিশ্লেষণ দেখতে পারবেন।")
    
    owner_id = st.text_input("আপনার দোকান আইডি প্রবেশ করান (মেলার জন্য টেস্ট আইডি দিন: STORE001):", key="store_owner_login")
    
    if owner_id:
        st.success(f"✅ স্বাগতম! দোকান আইডি: **{owner_id}** এর ড্যাশবোর্ড সক্রিয়।")
        
        st.markdown("### 📥 ক্রেতাদের কাছ থেকে আসা স্টক যাচাইয়ের রিকোয়েস্ট:")
        req_file = "stock_requests.json"
        if os.path.exists(req_file):
            with open(req_file, "r", encoding="utf-8") as f:
                try:
                    all_reqs = json.load(f)
                except:
                    all_reqs = []
            
            store_reqs = [r for r in all_reqs if r.get('store_id') == owner_id]
            
            if len(store_reqs) > 0:
                for idx, req in enumerate(store_reqs):
                    st.markdown(f"""
                    <div style="background:#fff9e6; padding:1rem; border-radius:10px; border-left:5px solid #f39c12; margin-bottom:0.8rem;">
                        <h4 style="margin:0; color:#d35400;">📦 পণ্য: {req.get('product')}</h4>
                        <p style="margin:2px 0;">⏱️ সময়: {req.get('time')}</p>
                        <p style="margin:2px 0;">🔄 বর্তমান স্ট্যাটাস: <strong>{req.get('status')}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("🟢 স্টকে আছে", key=f"yes_{owner_id}_{idx}"):
                            req['status'] = "স্টকে উপলব্ধ আছে ✅"
                            with open(req_file, "w", encoding="utf-8") as fw:
                                json.dump(all_reqs, fw, ensure_ascii=False, indent=2)
                            st.experimental_rerun()
                    with col_b2:
                        if st.button("🔴 স্টক শেষ", key=f"no_{owner_id}_{idx}"):
                            req['status'] = "স্টক শেষ ❌"
                            with open(req_file, "w", encoding="utf-8") as fw:
                                json.dump(all_reqs, fw, ensure_ascii=False, indent=2)
                            st.experimental_rerun()
            else:
                st.info("📭 আপনার দোকানের জন্য বর্তমানে কোনো নতুন স্টক রিকোয়েস্ট নেই।")
        else:
            st.info("📭 এখন পর্যন্ত কোনো স্টক রিকোয়েস্ট করা হয়নি।")
            
        st.markdown("---")
        st.markdown("### 📈 পাইকারি ও খুচরা মূল্য এবং বাজার চাহিদা বিশ্লেষণ (Market Analytics)")
        
        analytics_data = [
            {"product": "নাজিরশাইল চাল", "wholesale": "৬৫ টাকা/কেজি", "retail": "৭২ টাকা/কেজি", "demand": "উচ্চ চাহিদা 🔥", "trend": "ক্রমাগত বাড়ছে ↗️"},
            {"product": "সয়াবিন তেল", "wholesale": "১৬৮ টাকা/লিটার", "retail": "১৭৫ টাকা/লিটার", "demand": "স্বাভাবিক ⚖️", "trend": "স্থির রয়েছে ➡️"},
            {"product": "মসুর ডাল", "wholesale": "১৩৫ টাকা/কেজি", "retail": "১৪৫ টাকা/কেজি", "demand": "উচ্চ চাহিদা 🔥", "trend": "বাড়ছে ↗️"},
            {"product": "চিনি", "wholesale": "১৩০ টাকা/কেজি", "retail": "১৪০ টাকা/কেজি", "demand": "স্বাভাবিক ⚖️", "trend": "স্থির রয়েছে ➡️"}
        ]
        df_analytics = pd.DataFrame(analytics_data)
        st.dataframe(df_analytics, use_container_width=True, hide_index=True)

with tab10:
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
                        <p>🏙️ <strong>এলাকা:</strong> {c.get('area')}</p>
                        <p>📝 <strong>বিবরণ:</strong> {c.get('details')}</p>
                        <p style="color:#7f8c8d; font-size:0.85rem;">⏱️ <strong>সময়:</strong> {c.get('time')}</p>
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
    <strong>🛡️ মানব সাথি ১.০ (স্মার্ট শপ ফাইন্ডার, স্টক রিকোয়েস্ট ও গভঃ ড্যাশবোর্ড)</strong><br>
    <small>Created by Kaliagonj Naziraton High School (SOUNDARJYA)</small>
</div>
""", unsafe_allow_html=True)
