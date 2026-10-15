import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="মানব সাথি — স্মার্ট শপ ফাইন্ডার",
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
    <div class="app-subtitle">এলাকা ও পণ্যভিত্তিক সুনির্দিষ্ট দোকান ফাইন্ডার</div>
    <div style="color:#f1c40f; font-size:0.9rem; margin-top:0.4rem;">Created by Kaliagonj Naziraton High School (SOUNDARJYA)</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 পণ্য ও দোকান খুঁজুন",
    "🗺️ কাল্পনিক ভার্চুয়াল জোন ম্যাপ",
    "📋 সকল ৩২০টি দোকানের তালিকা",
    "🚨 দুর্নীতির অভিযোগ দাখিল",
    "🏥 স্বাস্থ্য সঙ্গী ও লাইফস্টাইল"
])

with tab1:
    st.markdown("## 🔍 সুনির্দিষ্ট এলাকা ও পণ্যভিত্তিক দোকান খুঁজুন")
    st.info("নিচে থেকে আপনার **এলাকা** এবং কাঙ্ক্ষিত **পণ্য** সিলেক্ট করুন। ফাইলে যে যে দোকানে এই পণ্যটি রয়েছে, শুধু সেই দোকানগুলোর তথ্যই নিচে দেখাবে।")
    
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
        ]

        st.markdown(f"### 🎯 ফলাফল: **{selected_area}** এলাকায় **{selected_product}** পাওয়া যায় এমন **{len(result_df)}টি** দোকান:")

        if len(result_df) > 0:
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
    st.markdown("## 🗺️ কাল্পনিক ভার্চুয়াল জোন ও দোকান লোকেশন ম্যাপ")
    st.info("বিজ্ঞান মেলা প্রদর্শনের জন্য তৈরি কাল্পনিক ডিজিটাল জোন ম্যাপ, যেখানে প্রতিটি দোকানের সুনির্দিষ্ট কাল্পনিক পজিশন ও কোঅর্ডিনেট পিন করা আছে।")
    
    if df_stores is not None:
        map_area = st.selectbox("এলাকা সিলেক্ট করুন (ভার্চুয়াল ম্যাপ দেখতে):", sorted(df_stores['এলাকা'].dropna().unique()), key="virtual_map_area")
        area_stores = df_stores[df_stores['এলাকা'] == map_area].copy()
        
        # Generating simulated virtual coordinates (latitude/longitude around a base point for the area)
        import numpy as np
        np.random.seed(42) # Stable random coordinates for each store
        base_lat, base_lon = 25.85, 88.60
        area_stores['lat'] = base_lat + np.random.uniform(-0.05, 0.05, len(area_stores))
        area_stores['lon'] = base_lon + np.random.uniform(-0.05, 0.05, len(area_stores))
        
        st.markdown(f"### 📍 **{map_area}** জোন ম্যাপে দোকানের অবস্থান ({len(area_stores)}টি দোকান চিহ্নিত)")
        
        # Displaying Streamlit interactive map
        st.map(area_stores, latitude='lat', longitude='lon', size=30, color='#e94560')
        
        st.markdown("### 🏪 নির্বাচিত এলাকার দোকানসমূহের ভার্চুয়াল লোকেশন বিবরণ:")
        for idx, row in area_stores.iterrows():
            st.markdown(f"""
            <div style="background:#f8f9fa; border-left:4px solid #0f3460; padding:10px; border-radius:8px; margin-bottom:8px;">
                <strong>🏪 {row['দোকানের নাম']}</strong> (আইডি: {row.get('দোকান আইডি', 'N/A')})<br>
                📍 ঠিকানা: {row['ঠিকানা']} | 📞 ফোন: {row['যোগাযোগ নম্বর']}<br>
                <small style="color:#e94560;">📌 কাল্পনিক জোন কোঅর্ডিনেট: Lat {row['lat']:.4f}, Lon {row['lon']:.4f}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ ম্যাপ ডাটা লোড করা যায়নি।")

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
    st.markdown("## 🚨 ভোক্তা অধিকার ও দুর্নীতি অভিযোগ ব্যবস্থাপনা")
    with st.form("complaint_form_fixed"):
        c_shop = st.text_input("দোকানের নাম ও ঠিকানা:")
        c_area = st.selectbox("এলাকা:", ["বোদা", "পঞ্চগড়", "ময়দানদীঘি", "ঠাকুরগাঁও"], key="comp_area_fixed")
        c_desc = st.text_area("অভিযোগের বিবরণ:", height=120)
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

with tab5:
    st.markdown("## 🏥 স্বাস্থ্য সঙ্গী ও লাইফস্টাইল মডিউল")
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
st.markdown("""
<div style="text-align:center;padding:1.2rem;background:linear-gradient(135deg,#0f3460,#1a1a2e);der-radius:14px;color:white;">
    <strong>🛡️ মানব সাথি ১.০ (মোবাইল ও ট্যাবলেট সংস্করণ)</strong><br>
    <small>Created by Kaliagonj Naziraton High School (SOUNDARJYA)</small>
</div>
""", unsafe_allow_html=True)
