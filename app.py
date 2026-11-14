import streamlit as st
import pandas as pd
import numpy as np
import json, os, zlib, html, hmac, uuid
from datetime import datetime

st.set_page_config(page_title="মানব সাথি", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

DB_FILE = "Unique_Named_Bangla_Store_Distribution.xlsx"
REQ_F, COMP_F, REV_F = "stock_requests.json", "complaints.json", "reviews.json"
BASE = (25.85, 88.60)
SAT_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

try:
    ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", None)
except Exception:
    ADMIN_PASS = None
ADMIN_PASS = ADMIN_PASS or os.environ.get("ADMIN_PASSWORD", "admin123")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Hind Siliguri', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.stApp { background: #eef3ef; }
.block-container { max-width: 1200px; padding-top: 1.5rem; }
h1, h2, h3 { color: #0b3d2e; letter-spacing: -0.2px; }

.hero { position: relative; overflow: hidden; border-radius: 22px; padding: 2.2rem 1.5rem; text-align: center; color: #fff; margin-bottom: 1.4rem;
  background: linear-gradient(120deg, #0b3d2e, #14665a, #0e4d64, #0b3d2e); background-size: 300% 300%;
  animation: flow 14s ease infinite, rise .8s cubic-bezier(.2,.7,.2,1) both; box-shadow: 0 18px 40px rgba(11,61,46,.25); }
.hero::after { content: ""; position: absolute; inset: 0; background: radial-gradient(circle at 80% 0%, rgba(242,169,59,.28), transparent 45%); pointer-events: none; }
.hero .orb { font-size: 2.8rem; display: inline-block; animation: float 4s ease-in-out infinite; }
.hero h1 { color: #fff; font-size: 2.6rem; margin: .2rem 0; font-weight: 700; }
.hero p { color: #ffd98a; margin: 0; font-weight: 500; font-size: 1.05rem; }
.hero small { display: block; margin-top: .6rem; color: rgba(255,255,255,.7); }

.sec { margin: .2rem 0 1rem; animation: rise .5s ease both; }
.sec h2 { margin: 0; font-size: 1.6rem; }
.sec p { margin: .2rem 0 0; color: #5b6b63; }

.card { background: #fff; border-radius: 16px; padding: 1.1rem 1.25rem; margin: .8rem 0; border: 1px solid #e1e9e3; border-left: 5px solid #14665a;
  box-shadow: 0 4px 14px rgba(11,61,46,.06); animation: rise .5s cubic-bezier(.2,.7,.2,1) both; transition: transform .25s ease, box-shadow .25s ease; }
.card:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(11,61,46,.12); }
.card.red { border-left-color: #d64545; } .card.amber { border-left-color: #f2a93b; } .card.blue { border-left-color: #2b7bb9; }
.card-h { display: flex; justify-content: space-between; align-items: center; gap: .6rem; margin-bottom: .3rem; }
.card h4 { margin: 0; color: #0b3d2e; font-size: 1.1rem; }
.card p { margin: .22rem 0; color: #33443b; font-size: .96rem; }
.badge { background: #e6f2ee; color: #0b3d2e; padding: 2px 11px; border-radius: 999px; font-size: .8rem; font-weight: 600; white-space: nowrap; }
.badge.red { background: #fde8e8; color: #b03030; } .badge.amber { background: #fff1d6; color: #8a5a00; } .badge.green { background: #dff5e6; color: #1b7a3d; }
.pill { display: inline-block; background: #fff1d6; color: #8a5a00; padding: 5px 12px; border-radius: 10px; font-weight: 600; margin-top: .4rem; font-size: .9rem; }
.pill.blue { background: #e3f0fa; color: #1f5f8f; }

div[data-testid="stMetric"] { background: #fff; border: 1px solid #e1e9e3; border-radius: 16px; padding: .9rem 1.1rem; box-shadow: 0 4px 14px rgba(11,61,46,.05); transition: transform .25s ease; }
div[data-testid="stMetric"]:hover { transform: translateY(-2px); }
.stButton > button, .stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button { border-radius: 12px; font-weight: 600; transition: transform .2s ease, box-shadow .2s ease; }
.stButton > button:hover, .stDownloadButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { transform: translateY(-2px); box-shadow: 0 8px 18px rgba(20,102,90,.25); }
button[data-baseweb="tab"] { border-radius: 12px 12px 0 0; transition: background .25s ease, color .25s ease; font-weight: 600; }
button[data-baseweb="tab"]:hover { background: #e3eee8; }
div[data-baseweb="tab-list"] { gap: 4px; overflow-x: auto; }
section[data-testid="stSidebar"] { background: #0b3d2e; }
section[data-testid="stSidebar"] * { color: #eaf4ef !important; }
.stTabs [data-baseweb="tab-panel"] { animation: rise .45s ease both; }

@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes flow { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
@media (max-width: 640px) { .hero h1 { font-size: 1.8rem; } .block-container { padding: 1rem .6rem; } }
</style>
""", unsafe_allow_html=True)


# ---------- সহায়ক ফাংশন ----------
def esc(v):
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else html.escape(str(v).strip())

def bn(x):
    return str(x).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))

def now():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")

def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def head(title, sub=""):
    st.markdown(f'<div class="sec"><h2>{title}</h2><p>{sub}</p></div>', unsafe_allow_html=True)

def card(title, lines, badge="", badge_cls="", extra="", tone=""):
    b = f'<span class="badge {badge_cls}">{badge}</span>' if badge else ""
    body = "".join(f"<p>{l}</p>" for l in lines)
    return f'<div class="card {tone}"><div class="card-h"><h4>{title}</h4>{b}</div>{body}{extra}</div>'

@st.cache_data(show_spinner=False)
def load_database():
    if not os.path.exists(DB_FILE):
        return None, None
    try:
        xls = pd.ExcelFile(DB_FILE)
        return (pd.read_excel(xls, "সকল ৩২০টি দোকানের তালিকা"), pd.read_excel(xls, "প্রোডাক্ট ও দোকান ম্যাপিং"))
    except Exception:
        return None, None

def add_geo(df):
    d = df.copy()
    pts = np.array([np.random.default_rng(zlib.crc32(str(i).strip().upper().encode())).uniform(-0.03, 0.03, 2) for i in d["দোকান আইডি"]])
    d["lat"], d["lon"] = BASE[0] + pts[:, 0], BASE[1] + pts[:, 1]
    d["distance_km"] = np.round(np.hypot(pts[:, 0], pts[:, 1] * np.cos(np.radians(BASE[0]))) * 111, 2)
    d["name"] = d["দোকানের নাম"].astype(str)
    return d

def show_map(df, satellite=True):
    try:
        import pydeck as pdk
        layers = [pdk.Layer("TileLayer", data=SAT_URL, min_zoom=0, max_zoom=19, tile_size=256)] if satellite else []
        layers.append(pdk.Layer("ScatterplotLayer", data=df[["lat", "lon", "name"]], get_position="[lon, lat]",
                                get_fill_color=[242, 169, 59, 235], get_line_color=[255, 255, 255], stroked=True,
                                line_width_min_pixels=2, radius_min_pixels=7, get_radius=60, pickable=True))
        view = pdk.ViewState(latitude=float(df.lat.mean()), longitude=float(df.lon.mean()), zoom=11.5)
        st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view, map_style=None if satellite else "light", tooltip={"text": "{name}"}), height=420)
    except Exception:
        st.map(df, latitude="lat", longitude="lon", size=45, color="#14665a")

def latest_status(reqs, sid, product):
    for r in reqs:
        if str(r.get("store_id", "")).upper() == sid.upper() and r.get("product") == product:
            return f'{r.get("status")} ({r.get("time")})'
    return None

def is_pending(r):
    return r.get("state", "pending" if "অপেক্ষা" in str(r.get("status", "")) else "done") == "pending"


df_stores, df_map = load_database()
db_ok = df_stores is not None and df_map is not None

# ---------- সাইডবার ----------
with st.sidebar:
    st.markdown("### 🛰️ মানব সাথি")
    st.caption("আপনার এলাকার দোকান, দাম ও সেবার সঙ্গী")
    if db_ok:
        st.metric("নিবন্ধিত দোকান", bn(len(df_stores)))
        st.metric("এলাকা", bn(df_stores["এলাকা"].nunique()))
        st.metric("পণ্যের ধরন", bn(df_map["প্রোডাক্টের নাম"].nunique()))
    st.markdown("---")
    st.markdown("**কীভাবে ব্যবহার করবেন**\n\n১. এলাকা ও পণ্য বেছে দোকান খুঁজুন\n\n২. স্টক আছে কি না যাচাই করতে অনুরোধ পাঠান\n\n৩. দাম বা সেবায় সমস্যা হলে অভিযোগ জানান")
    st.markdown("---")
    st.caption("তৈরি করেছে: কালিয়াগঞ্জ নাজিরতন উচ্চ বিদ্যালয় (SOUNDARJYA)")

st.markdown("""<div class="hero"><div class="orb">🛰️</div><h1>মানব সাথি</h1>
<p>স্যাটেলাইট ম্যাপে দোকান খুঁজুন, লাইভ স্টক জানুন, ন্যায্য দামে কিনুন</p>
<small>কালিয়াগঞ্জ নাজিরতন উচ্চ বিদ্যালয় (SOUNDARJYA)</small></div>""", unsafe_allow_html=True)

T = st.tabs(["🔎 পণ্য খুঁজুন", "🏪 দোকান তালিকা", "📊 বাজার দর", "⭐ রিভিউ", "🚨 অভিযোগ ও হেল্পলাইন", "🏥 স্বাস্থ্য সঙ্গী", "🧾 দোকানদার প্যানেল", "🏛️ সরকারি প্যানেল"])

# ---------- ১. পণ্য খুঁজুন ----------
with T[0]:
    head("পণ্য খুঁজুন", "এলাকা ও পণ্য বেছে নিন — কাছের দোকান ম্যাপে দেখুন এবং স্টক যাচাই করুন।")
    if not db_ok:
        st.error(f"ডাটাবেজ ফাইল পাওয়া যায়নি। `{DB_FILE}` ফাইলটি অ্যাপের ফোল্ডারে রাখুন।")
    else:
        c1, c2, c3 = st.columns([2, 2, 2])
        areas = sorted(df_map["এলাকা"].dropna().astype(str).str.strip().unique())
        area = c1.selectbox("এলাকা", areas, key="s_area")
        in_area = df_map[df_map["এলাকা"].astype(str).str.strip() == area]
        products = sorted(in_area["প্রোডাক্টের নাম"].dropna().astype(str).str.strip().unique())
        product = c2.selectbox("পণ্য", products, key="s_prod") if products else None
        sort_by = c3.selectbox("সাজান", ["কাছের দোকান আগে", "নাম অনুযায়ী"], key="s_sort")
        mode = st.radio("ম্যাপ", ["🛰️ স্যাটেলাইট", "🗺️ সাধারণ"], horizontal=True, label_visibility="collapsed")

        res = in_area[in_area["প্রোডাক্টের নাম"].astype(str).str.strip() == product].copy() if product else pd.DataFrame()
        if res.empty:
            st.warning("এই এলাকায় পণ্যটি বিক্রি করে এমন কোনো দোকান ডাটাবেজে নেই। অন্য এলাকা বা পণ্য বেছে দেখুন।")
        else:
            res = add_geo(res).sort_values("distance_km" if "কাছের" in sort_by else "name")
            m1, m2, m3 = st.columns(3)
            m1.metric("পাওয়া গেছে", f"{bn(len(res))}টি দোকান")
            m2.metric("সবচেয়ে কাছের", f"{bn(round(res.distance_km.min(), 1))} কিমি")
            m3.metric("এলাকা", area)
            show_map(res, "স্যাটেলাইট" in mode)
            st.caption("ম্যাপের অবস্থান ও দূরত্ব আনুমানিক (ডেমো কেন্দ্র থেকে হিসাব করা)।")

            reqs = read_json(REQ_F)
            for idx, row in res.iterrows():
                d = row["distance_km"]
                dist = f"{bn(int(d * 1000))} মিটার" if d < 1 else f"{bn(round(d, 1))} কিমি"
                sid = str(row["দোকান আইডি"]).strip()
                ls = latest_status(reqs, sid, product)
                extra = f'<span class="pill blue">📏 {dist} — হেঁটে প্রায় {bn(int(d * 12) + 1)} মিনিট</span>'
                if ls:
                    extra += f'<br><span class="pill">📢 সর্বশেষ স্টক খবর: {esc(ls)}</span>'
                st.markdown(card(f"🏪 {esc(row['দোকানের নাম'])}", [
                    f"📦 <b>পণ্য:</b> {esc(row['প্রোডাক্টের নাম'])} ({esc(row['ওজন/সাইজ'])})",
                    f"🏷️ <b>ব্র্যান্ড:</b> {esc(row['ব্র্যান্ড'])} ({esc(row['কোম্পানি'])})",
                    f"📍 <b>ঠিকানা:</b> {esc(row['ঠিকানা'])}",
                    f"📞 <b>ফোন:</b> {esc(row['যোগাযোগ নম্বর'])}"], badge=f"আইডি {esc(sid)}", extra=extra), unsafe_allow_html=True)
                if st.button("🔍 স্টক আছে কি না জানতে চাই", key=f"rq_{sid}_{idx}"):
                    if any(is_pending(r) and str(r.get("store_id")).upper() == sid.upper() and r.get("product") == product for r in reqs):
                        st.toast("এই পণ্যের জন্য অনুরোধ আগেই পাঠানো হয়েছে, উত্তরের অপেক্ষা করুন।", icon="⏳")
                    else:
                        reqs.insert(0, {"id": uuid.uuid4().hex[:8], "store_id": sid.upper(), "store_name": str(row["দোকানের নাম"]),
                                        "product": product, "time": now(), "status": "মালিকের উত্তরের অপেক্ষায় ⏳", "state": "pending"})
                        write_json(REQ_F, reqs)
                        st.toast("অনুরোধ পাঠানো হয়েছে। দোকানদার উত্তর দিলে এখানে দেখা যাবে।", icon="✅")

# ---------- ২. দোকান তালিকা ----------
with T[1]:
    head("দোকান তালিকা", "এলাকা বা নাম দিয়ে খুঁজুন, ম্যাপে দেখুন এবং তালিকা ডাউনলোড করুন।")
    if not db_ok:
        st.error("দোকানের ডাটাবেজ ফাইল পাওয়া যায়নি।")
    else:
        c1, c2 = st.columns([1, 2])
        a = c1.selectbox("এলাকা", ["সব এলাকা"] + sorted(df_stores["এলাকা"].dropna().astype(str).unique()), key="l_area")
        q = c2.text_input("দোকানের নাম বা আইডি লিখে খুঁজুন", key="l_q", placeholder="যেমন: S-126")
        view = df_stores if a == "সব এলাকা" else df_stores[df_stores["এলাকা"].astype(str) == a]
        if q.strip():
            mask = view["দোকানের নাম"].astype(str).str.contains(q.strip(), case=False, na=False) | view["দোকান আইডি"].astype(str).str.contains(q.strip(), case=False, na=False)
            view = view[mask]
        st.markdown(f"**{bn(len(view))}টি দোকান পাওয়া গেছে**")
        if view.empty:
            st.info("কোনো দোকান মেলেনি। অন্য শব্দ দিয়ে চেষ্টা করুন।")
        else:
            show_map(add_geo(view), True)
            cols = [c for c in ["দোকান আইডি", "দোকানের নাম", "এলাকা", "ঠিকানা", "যোগাযোগ নম্বর", "ক্যাটাগরি"] if c in view.columns]
            st.dataframe(view[cols], use_container_width=True, hide_index=True)
            st.download_button("⬇️ তালিকা ডাউনলোড (CSV)", view[cols].to_csv(index=False).encode("utf-8-sig"), "dokan_talika.csv", "text/csv")

# ---------- ৩. বাজার দর ----------
PRICES = [("নাজিরশাইল চাল", "কেজি", 70, 72, 5), ("সয়াবিন তেল", "লিটার", 175, 175, 2), ("মসুর ডাল", "কেজি", 140, 145, 2),
          ("চিনি", "কেজি", 135, 140, 1), ("আটা/ময়দা", "কেজি", 60, 60, 2), ("আলু", "কেজি", 45, 50, 3),
          ("পেঁয়াজ", "কেজি", 85, 90, 2), ("ডিম", "হালি", 48, 50, 2), ("লবণ", "কেজি", 40, 40, 1), ("তরল দুধ", "লিটার", 85, 85, 1)]

def price_status(gov, mkt):
    if mkt <= gov: return "✅ ন্যায্য মূল্য"
    return "⚠️ সামান্য বেশি" if (mkt - gov) / gov <= 0.05 else "🚨 অতিরিক্ত মূল্য"

with T[2]:
    head("বাজার দর ও খরচ হিসাব", "সরকার নির্ধারিত দামের সাথে খুচরা বাজারের দাম মিলিয়ে দেখুন। (দামগুলো নমুনা; হালনাগাদ রাখুন)")
    dfp = pd.DataFrame([{"পণ্য": f"{n} ({u})", "সরকারি দর (৳)": g, "বাজার দর (৳)": m, "পার্থক্য (৳)": m - g, "অবস্থা": price_status(g, m)} for n, u, g, m, _ in PRICES])
    over = int((dfp["পার্থক্য (৳)"] > 0).sum())
    k1, k2 = st.columns(2)
    k1.metric("ন্যায্য দামে আছে", f"{bn(len(dfp) - over)}টি পণ্য")
    k2.metric("বেশি দামে বিক্রি হচ্ছে", f"{bn(over)}টি পণ্য")
    st.dataframe(dfp, use_container_width=True, hide_index=True)
    st.markdown("### 🧮 মাসিক বাজার খরচ ক্যালকুলেটর")
    cols = st.columns(5)
    qty = [cols[i % 5].number_input(f"{n} ({u})", 0, 100, d, key=f"q{i}") for i, (n, u, g, m, d) in enumerate(PRICES)]
    total = sum(q * p[3] for q, p in zip(qty, PRICES))
    gov_total = sum(q * p[2] for q, p in zip(qty, PRICES))
    r1, r2, r3 = st.columns(3)
    r1.metric("বাজার দরে মোট", f"{bn(total)} ৳")
    r2.metric("সরকারি দরে মোট", f"{bn(gov_total)} ৳")
    r3.metric("বাড়তি খরচ", f"{bn(total - gov_total)} ৳")
    if total > 0:
        st.bar_chart(pd.DataFrame({"খরচ (৳)": [q * p[3] for q, p in zip(qty, PRICES)]}, index=[p[0] for p in PRICES]), color="#14665a")

# ---------- ৪. রিভিউ ----------
with T[3]:
    head("দোকান রিভিউ", "আপনার অভিজ্ঞতা জানান, অন্যরা ভালো দোকান চিনতে পারবে।")
    revs = read_json(REV_F)
    left, right = st.columns([1, 1])
    with left:
        opts = [f"{r['দোকান আইডি']} — {r['দোকানের নাম']}" for _, r in df_stores.iterrows()] if df_stores is not None else []
        with st.form("rev_form", clear_on_submit=True):
            shop = st.selectbox("দোকান বেছে নিন", opts) if opts else st.text_input("দোকানের নাম বা আইডি")
            stars = st.slider("রেটিং (১–৫)", 1, 5, 5)
            text = st.text_area("আপনার মতামত", height=110)
            if st.form_submit_button("⭐ রিভিউ জমা দিন", type="primary"):
                if shop:
                    revs.insert(0, {"shop": shop, "stars": stars, "comment": text.strip(), "time": now()})
                    write_json(REV_F, revs)
                    st.toast("ধন্যবাদ! রিভিউ সংরক্ষিত হয়েছে।", icon="✅")
                    st.rerun()
    with right:
        if revs:
            avg = pd.DataFrame(revs).groupby("shop")["stars"].agg(["mean", "count"]).sort_values("mean", ascending=False).head(8)
            st.markdown("**সর্বোচ্চ রেটিং পাওয়া দোকান**")
            st.bar_chart(avg[["mean"]].rename(columns={"mean": "গড় রেটিং"}), color="#f2a93b")
        else:
            st.info("এখনো কোনো রিভিউ নেই। প্রথম রিভিউ আপনিই দিন।")
    for r in revs[:6]:
        st.markdown(card(esc(r["shop"]), [("⭐" * int(r["stars"])), esc(r.get("comment") or "মন্তব্য নেই"), f'<small>{esc(r["time"])}</small>'], tone="amber"), unsafe_allow_html=True)

# ---------- ৫. অভিযোগ ও হেল্পলাইন ----------
with T[4]:
    head("অভিযোগ ও হেল্পলাইন", "বেশি দাম, ওজনে কম বা ভেজাল পণ্যের অভিযোগ সরাসরি সরকারি প্যানেলে পাঠান।")
    cl, cr = st.columns([3, 2])
    with cl:
        areas_c = sorted(df_stores["এলাকা"].dropna().astype(str).unique()) if df_stores is not None else ["বোদা", "পঞ্চগড়", "ময়দানদীঘি", "ঠাকুরগাঁও"]
        with st.form("comp_form", clear_on_submit=True):
            shop = st.text_input("দোকানের নাম ও ঠিকানা")
            f1, f2 = st.columns(2)
            area_c = f1.selectbox("এলাকা", areas_c)
            kind = f2.selectbox("অভিযোগের ধরন", ["অতিরিক্ত দাম", "ওজনে কম", "মেয়াদোত্তীর্ণ পণ্য", "ভেজাল পণ্য", "অন্যান্য"])
            desc = st.text_area("বিস্তারিত লিখুন (কমপক্ষে ১০ অক্ষর)", height=120)
            if st.form_submit_button("🚨 অভিযোগ জমা দিন", type="primary"):
                if not shop.strip() or len(desc.strip()) < 10:
                    st.error("দোকানের নাম এবং অন্তত ১০ অক্ষরের বিবরণ দিন।")
                else:
                    cs = read_json(COMP_F)
                    cid = "C-" + uuid.uuid4().hex[:6].upper()
                    cs.insert(0, {"id": cid, "shop": shop.strip(), "area": area_c, "kind": kind, "details": desc.strip(), "time": now(), "status": "জমা হয়েছে"})
                    write_json(COMP_F, cs)
                    st.balloons()
                    st.success(f"অভিযোগ জমা হয়েছে। আপনার অভিযোগ নম্বর: {cid}")
    with cr:
        for n, num, d in [("ভোক্তা অধিকার অধিদপ্তর", "১৬১২১", "বেশি দাম বা প্রতারণার অভিযোগ"), ("জাতীয় জরুরি সেবা", "৯৯৯", "পুলিশ, ফায়ার সার্ভিস, অ্যাম্বুলেন্স"),
                          ("স্বাস্থ্য বাতায়ন", "১৬২৬৩", "স্বাস্থ্য পরামর্শ"), ("দুর্নীতি দমন কমিশন", "১০৬", "দুর্নীতির অভিযোগ")]:
            st.markdown(card(f"📞 {n}", [d], badge=num, tone="blue"), unsafe_allow_html=True)

# ---------- ৬. স্বাস্থ্য ----------
HERBS = [("সর্দি, কাশি ও গলা খুশখুশ", "তুলসী, আদা, মধু", "তুলসী পাতার রস, আদা ও মধু মিশিয়ে হালকা গরম করে দিনে ২–৩ বার খান।"),
         ("গ্যাস্ট্রিক ও অ্যাসিডিটি", "মৌরি, ইসবগুল", "খাওয়ার পর ১ চামচ মৌরি চিবান অথবা ইসবগুল ভিজিয়ে খান।"),
         ("বদহজম ও পেট ফাঁপা", "জোয়ান, বিট লবণ", "ঈষদুষ্ণ পানিতে সামান্য জোয়ান গুঁড়ো ও বিট লবণ মিশিয়ে পান করুন।"),
         ("সাধারণ মাথাব্যথা", "পুদিনা, আদা", "আদা চা পান করুন এবং কপালে পুদিনার রস হালকা লাগান।"),
         ("কোষ্ঠকাঠিন্য", "ইসবগুল, ত্রিফলা", "রাতে এক গ্লাস হালকা গরম পানিতে ১–২ চামচ ইসবগুল মিশিয়ে খান। প্রচুর পানি পান করুন।"),
         ("মানসিক চাপ ও অনিদ্রা", "ক্যামোমাইল, জায়ফল", "ঘুমের আগে ক্যামোমাইল চা বা এক কাপ গরম দুধে এক চিমটি জায়ফল গুঁড়ো খান।"),
         ("দাঁত ও মাড়ির ব্যথা", "লবঙ্গ", "ব্যথার জায়গায় একটি লবঙ্গ চেপে রাখুন। ব্যথা থাকলে দন্ত চিকিৎসকের কাছে যান।"),
         ("রক্তচাপ নিয়ন্ত্রণে সহায়ক", "রসুন", "কম লবণ খান ও নিয়মিত হাঁটুন; রসুন খাদ্যতালিকায় সহায়ক হতে পারে। ডাক্তারের ওষুধ নিজে বন্ধ করবেন না।"),
         ("ওজন নিয়ন্ত্রণে সহায়ক", "লেবু, মধু", "হালকা গরম পানিতে লেবুর রস দিন। সঙ্গে সুষম খাবার ও নিয়মিত ব্যায়াম জরুরি।"),
         ("কৃমির সমস্যা", "পেঁপে, রসুন", "খাদ্যতালিকায় পেঁপে ও রসুন রাখুন। কৃমির সন্দেহ হলে ডাক্তারের পরামর্শে কৃমিনাশক ওষুধ নিন।"),
         ("চুলকানি ও ত্বকের সমস্যা", "নিম, হলুদ", "নিম পাতা ও হলুদ বেটে আক্রান্ত স্থানে লাগাতে পারেন। সমস্যা না কমলে চর্মরোগ বিশেষজ্ঞকে দেখান।"),
         ("প্রস্রাবে জ্বালাপোড়া", "ধনে বীজ, ডাবের পানি", "ধনে বীজ ভেজানো পানি ও ডাবের পানি পান করুন। জ্বর বা ব্যথা থাকলে দ্রুত ডাক্তার দেখান।"),
         ("চুল পড়া ও খুশকি", "আমলকী, রিঠা", "আমলকী ও রিঠা ফোটানো পানিতে চুল ধুতে পারেন।"),
         ("রক্তস্বল্পতা", "ডালিম, খেজুর, পালং শাক", "আয়রনসমৃদ্ধ খাবার খান এবং রক্ত পরীক্ষা করিয়ে ডাক্তারের পরামর্শ নিন।"),
         ("মুখের দুর্গন্ধ", "দারুচিনি, এলাচ", "খাওয়ার পর এলাচ বা দারুচিনি চিবান এবং নিয়মিত দাঁত ও জিব পরিষ্কার করুন।")]

with T[5]:
    head("স্বাস্থ্য সঙ্গী", "BMI ও রক্তচাপ যাচাই করুন এবং সাধারণ সমস্যায় ঘরোয়া পরামর্শ দেখুন।")
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("#### ⚖️ BMI")
        w = st.number_input("ওজন (কেজি)", 10.0, 200.0, 60.0, 0.5, key="bw")
        h = st.number_input("উচ্চতা (সেমি)", 50.0, 250.0, 160.0, 0.5, key="bh")
        bmi = w / ((h / 100) ** 2)
        cat, ico = ("কম ওজন", "🟡") if bmi < 18.5 else ("স্বাভাবিক", "🟢") if bmi < 25 else ("বেশি ওজন", "🟠") if bmi < 30 else ("স্থূলতা", "🔴")
        st.metric("আপনার BMI", bn(f"{bmi:.1f}"), f"{ico} {cat}", delta_color="off")
        st.progress(min(bmi / 40, 1.0))
    with b2:
        st.markdown("#### 🩺 রক্তচাপ")
        s = st.number_input("সিস্টোলিক", 60, 250, 120, key="bs")
        d = st.number_input("ডায়াস্টোলিক", 40, 150, 80, key="bd")
        if s >= 180 or d >= 120: msg, fn = "অতি উচ্চ — এখনই চিকিৎসকের কাছে যান", st.error
        elif s >= 140 or d >= 90: msg, fn = "উচ্চ রক্তচাপ — চিকিৎসকের পরামর্শ নিন", st.warning
        elif s >= 130 or d >= 80: msg, fn = "স্বাভাবিকের চেয়ে কিছুটা বেশি", st.warning
        elif s < 90 or d < 60: msg, fn = "রক্তচাপ কম — লক্ষণ থাকলে ডাক্তার দেখান", st.warning
        else: msg, fn = "স্বাভাবিক রক্তচাপ ✅", st.success
        st.metric("রক্তচাপ", f"{bn(s)}/{bn(d)}")
        fn(msg)
    st.markdown("---")
    st.markdown("#### 🌿 ঘরোয়া ও ভেষজ পরামর্শ")
    st.warning("এগুলো সাধারণ তথ্য, চিকিৎসার বিকল্প নয়। গর্ভাবস্থা, শিশু বা দীর্ঘমেয়াদি রোগে এবং লক্ষণ গুরুতর হলে ডাক্তারের পরামর্শ নিন।")
    hq = st.text_input("সমস্যার নাম লিখে খুঁজুন", key="hq", placeholder="যেমন: গ্যাস্ট্রিক")
    shown = [x for x in HERBS if hq.strip() in x[0] or hq.strip() in x[1]]
    hc = st.columns(2)
    for i, (dis, herb, how) in enumerate(shown):
        hc[i % 2].markdown(card(dis, [f"🌿 <b>উপাদান:</b> {herb}", f"💡 {how}"]), unsafe_allow_html=True)
    if not shown:
        st.info("এই নামে কোনো সমস্যা পাওয়া যায়নি।")

# ---------- ৭. দোকানদার প্যানেল ----------
with T[6]:
    head("দোকানদার প্যানেল", "দোকান আইডি দিয়ে প্রবেশ করে ক্রেতাদের স্টক অনুরোধের উত্তর দিন।")
    sid = st.text_input("দোকান আইডি", placeholder="যেমন: S-126", key="own_id").strip().upper()
    if sid:
        info = None
        if df_stores is not None:
            mt = df_stores[df_stores["দোকান আইডি"].astype(str).str.strip().str.upper() == sid]
            info = mt.iloc[0] if len(mt) else None
        if info is None:
            st.error(f"'{sid}' আইডি পাওয়া যায়নি। 'দোকান তালিকা' ট্যাব থেকে সঠিক আইডি দেখে নিন।")
        else:
            st.markdown(card(f"✅ স্বাগতম, {esc(info['দোকানের নাম'])}", [f"📍 {esc(info['এলাকা'])} · {esc(info['ঠিকানা'])}", f"📂 {esc(info['ক্যাটাগরি'])} · 📞 {esc(info['যোগাযোগ নম্বর'])}"], badge=esc(sid)), unsafe_allow_html=True)
            allr = read_json(REQ_F)
            mine = [(i, r) for i, r in enumerate(allr) if str(r.get("store_id", "")).upper() == sid]
            pend = [(i, r) for i, r in mine if is_pending(r)]
            m1, m2 = st.columns(2)
            m1.metric("উত্তরের অপেক্ষায়", bn(len(pend)))
            m2.metric("উত্তর দেওয়া হয়েছে", bn(len(mine) - len(pend)))
            if not pend:
                st.info("📭 এই মুহূর্তে কোনো নতুন স্টক অনুরোধ নেই।")
            for i, r in pend:
                st.markdown(card(f"📦 {esc(r.get('product'))}", [f"⏱️ {esc(r.get('time'))}"], badge="নতুন", badge_cls="amber", tone="amber"), unsafe_allow_html=True)
                y, n = st.columns(2)
                for col, state, label, text in [(y, "yes", "🟢 স্টক আছে", "স্টক আছে ✅"), (n, "no", "🔴 স্টক নেই", "স্টক নেই ❌")]:
                    if col.button(label, key=f"{state}_{sid}_{i}", use_container_width=True):
                        allr[i].update({"status": text, "state": state, "answered": now()})
                        write_json(REQ_F, allr)
                        st.rerun()
            st.markdown("---")
            st.markdown("#### 📈 বাজার বিশ্লেষণ")
            an = pd.DataFrame([("নাজিরশাইল চাল", 65, 72, 92, "বাড়ছে ↗️"), ("সয়াবিন তেল", 168, 175, 85, "স্থির ➡️"), ("মসুর ডাল", 135, 145, 78, "বাড়ছে ↗️"),
                               ("চিনি", 130, 140, 70, "স্থির ➡️"), ("পেঁয়াজ", 80, 90, 95, "দ্রুত বাড়ছে ⬆️"), ("আলু", 42, 50, 88, "কমছে ↘️")],
                              columns=["পণ্য", "পাইকারি (৳)", "খুচরা (৳)", "চাহিদা (১০০ এর মধ্যে)", "মূল্য প্রবণতা"])
            an["লাভের হার (%)"] = ((an["খুচরা (৳)"] - an["পাইকারি (৳)"]) / an["পাইকারি (৳)"] * 100).round(1)
            g1, g2 = st.columns(2)
            g1.markdown("**পাইকারি বনাম খুচরা দাম**")
            g1.bar_chart(an.set_index("পণ্য")[["পাইকারি (৳)", "খুচরা (৳)"]], color=["#2b7bb9", "#f2a93b"])
            g2.markdown("**চাহিদা সূচক**")
            g2.area_chart(an.set_index("পণ্য")[["চাহিদা (১০০ এর মধ্যে)"]], color="#14665a")
            st.dataframe(an, use_container_width=True, hide_index=True)

# ---------- ৮. সরকারি প্যানেল ----------
with T[7]:
    head("সরকারি কর্মকর্তা প্যানেল", "অভিযোগ দেখুন, অবস্থা হালনাগাদ করুন এবং তথ্য ডাউনলোড করুন।")
    if st.session_state.get("admin_ok"):
        if st.button("🔓 লগআউট"):
            st.session_state.admin_ok = False
            st.rerun()
        cs = read_json(COMP_F)
        STAT = ["জমা হয়েছে", "তদন্তাধীন", "নিষ্পত্তি হয়েছে"]
        k = st.columns(3)
        k[0].metric("মোট অভিযোগ", bn(len(cs)))
        k[1].metric("তদন্তাধীন", bn(sum(c.get("status") == "তদন্তাধীন" for c in cs)))
        k[2].metric("নিষ্পত্তি হয়েছে", bn(sum(c.get("status") == "নিষ্পত্তি হয়েছে" for c in cs)))
        if not cs:
            st.info("📭 এখনো কোনো অভিযোগ জমা হয়নি।")
        else:
            flt = st.multiselect("অবস্থা অনুযায়ী ফিল্টার", STAT, default=STAT)
            st.download_button("⬇️ সব অভিযোগ (CSV)", pd.DataFrame(cs).to_csv(index=False).encode("utf-8-sig"), "abhijog.csv", "text/csv")
            for i, c in enumerate(cs):
                stt = c.get("status", "জমা হয়েছে")
                if stt not in flt:
                    continue
                tone = {"জমা হয়েছে": "red", "তদন্তাধীন": "amber", "নিষ্পত্তি হয়েছে": ""}.get(stt, "red")
                st.markdown(card(f"🚨 {esc(c.get('shop'))}", [f"🏙️ {esc(c.get('area'))} · {esc(c.get('kind', 'অন্যান্য'))}", f"📝 {esc(c.get('details'))}", f"<small>নম্বর: {esc(c.get('id', '—'))} · {esc(c.get('time'))}</small>"],
                                badge=esc(stt), badge_cls="red" if tone == "red" else "amber" if tone == "amber" else "green", tone=tone), unsafe_allow_html=True)
                with st.expander("অবস্থা পরিবর্তন করুন"):
                    new = st.selectbox("নতুন অবস্থা", STAT, index=STAT.index(stt) if stt in STAT else 0, key=f"st_{i}")
                    if st.button("সংরক্ষণ করুন", key=f"sv_{i}"):
                        cs[i]["status"] = new
                        write_json(COMP_F, cs)
                        st.rerun()
    else:
        pw = st.text_input("অফিসার পাসওয়ার্ড", type="password", key="adm_pw")
        if pw:
            if hmac.compare_digest(pw, ADMIN_PASS):
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("পাসওয়ার্ড সঠিক নয়। আবার চেষ্টা করুন।")

st.markdown("---")
st.markdown('<div style="text-align:center;color:#5b6b63;padding:.6rem">🛰️ <b>মানব সাথি ২.০</b> · কালিয়াগঞ্জ নাজিরতন উচ্চ বিদ্যালয় (SOUNDARJYA)</div>', unsafe_allow_html=True)
