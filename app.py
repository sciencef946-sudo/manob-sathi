# -*- coding: utf-8 -*-
"""মানব সাথি ৩.০ — স্যাটেলাইট ম্যাপে দোকান খুঁজুন, স্টক জানুন, ন্যায্য দামে কিনুন।"""
import base64, hmac, html, json, os, uuid, zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    import altair as alt
except Exception:  # altair না থাকলে চার্ট বাদ যাবে, অ্যাপ চলবে
    alt = None

st.set_page_config(page_title="মানব সাথি", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

# ======================================================================
#  কনফিগ
# ======================================================================
DB_FILE = "Unique_Named_Bangla_Store_Distribution.xlsx"
REQ_F, COMP_F, REV_F = "stock_requests.json", "complaints.json", "reviews.json"
BASE = (25.85, 88.60)
AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_FILES = {"open": "opening.mp3", "bazar": "bazar_dor.mp3", "dokan": "dokan_talika.mp3", "ovijog": "ovijog_helpline.mp3"}
BD = timezone(timedelta(hours=6))  # বাংলাদেশ সময়

try:
    ADMIN_PASS = st.secrets.get("ADMIN_PASSWORD", None)
except Exception:
    ADMIN_PASS = None
DEFAULT_PASS = not (ADMIN_PASS or os.environ.get("ADMIN_PASSWORD"))
ADMIN_PASS = str(ADMIN_PASS or os.environ.get("ADMIN_PASSWORD", "admin123"))


def _ver():
    try:
        return tuple(int(p) for p in st.__version__.split(".")[:2])
    except Exception:
        return (1, 0)


STRETCH = {"width": "stretch"} if _ver() >= (1, 50) else {"use_container_width": True}

# ======================================================================
#  স্টাইল (iOS-ধাঁচের স্প্রিং অ্যানিমেশন, গ্লাস ইফেক্ট, বহুরঙা থিম)
# ======================================================================
CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+Da+2:wght@500;600;700;800&family=Hind+Siliguri:wght@400;500;600;700&display=swap');
:root{--ink:#0a1226;--mut:#5d6b86;--ios:cubic-bezier(.32,.72,0,1);--spring:cubic-bezier(.34,1.56,.64,1)}
html,body,[class*="css"],.stApp{font-family:'Hind Siliguri',sans-serif}
h1,h2,h3,h4{font-family:'Baloo Da 2','Hind Siliguri',sans-serif;color:var(--ink);letter-spacing:-.2px}
#MainMenu,footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.stApp{background:#f1f4fb}
.stApp::before{content:"";position:fixed;inset:-20%;z-index:0;pointer-events:none;background:radial-gradient(40% 35% at 14% 10%,rgba(79,70,229,.17),transparent 70%),radial-gradient(35% 30% at 88% 14%,rgba(15,181,166,.19),transparent 70%),radial-gradient(40% 35% at 72% 92%,rgba(255,176,32,.17),transparent 70%),radial-gradient(35% 30% at 8% 86%,rgba(255,92,154,.13),transparent 70%);animation:drift 28s ease-in-out infinite alternate}
.block-container{position:relative;z-index:1;max-width:1180px;padding-top:1rem;padding-bottom:3rem}
div[data-testid="stElementContainer"]:has(iframe[height="1"]){position:absolute;width:0;height:0;overflow:hidden;margin:0}

/* ---------- স্প্ল্যাশ (অ্যাপ খোলার অ্যানিমেশন) ---------- */
#ms-splash{position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;flex-direction:column;text-align:center;color:#fff;overflow:hidden;background:radial-gradient(120% 90% at 50% 0%,#1d2b73 0%,#0a1226 58%,#050914 100%);animation:splashFallback .6s ease 10s forwards}
#ms-splash.out{animation:splashOut .95s var(--ios) forwards}
#ms-splash .blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.55;animation:blob 9s ease-in-out infinite alternate}
#ms-splash .b1{width:46vmax;height:46vmax;background:#4f46e5;left:-14vmax;top:-16vmax}
#ms-splash .b2{width:40vmax;height:40vmax;background:#0fb5a6;right:-16vmax;top:8vmax;animation-delay:-3s}
#ms-splash .b3{width:34vmax;height:34vmax;background:#ff5c9a;left:18vmax;bottom:-18vmax;opacity:.42;animation-delay:-6s}
#ms-splash .b4{width:26vmax;height:26vmax;background:#ffb020;right:6vmax;bottom:-10vmax;opacity:.35;animation-delay:-4s}
#ms-splash .sp-in{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center}
#ms-splash .logo{position:relative;width:132px;height:132px;border-radius:36px;display:grid;place-items:center;font-size:4rem;background:linear-gradient(145deg,#22d3b6,#4f46e5 60%,#8b5cf6);box-shadow:0 34px 70px -12px rgba(79,70,229,.65),inset 0 2px 0 rgba(255,255,255,.45);animation:logoIn 1.3s var(--spring) both}
#ms-splash .gl{animation:float 3.6s ease-in-out infinite;display:inline-block}
#ms-splash .ring{position:absolute;inset:-12px;border-radius:46px;border:2px solid rgba(255,255,255,.4);animation:ring 2.6s ease-out infinite}
#ms-splash .ring.r2{animation-delay:1.1s}
#ms-splash .sp-t{font-family:'Baloo Da 2',sans-serif;font-size:clamp(2.6rem,9vw,3.6rem);font-weight:800;margin-top:1.5rem;line-height:1.1}
#ms-splash .sp-t span{display:inline-block;opacity:0;animation:letter .9s var(--ios) both;animation-delay:calc(.7s + var(--i)*.18s)}
#ms-splash .sp-s{margin-top:.3rem;color:#c3d3ff;font-size:1.02rem;opacity:0;animation:fadeUp .9s var(--ios) 1.6s forwards}
#ms-splash .sp-bar{width:min(260px,64vw);height:5px;border-radius:9px;background:rgba(255,255,255,.14);margin-top:2.2rem;overflow:hidden;opacity:0;animation:fadeUp .6s ease 1.7s forwards}
#ms-splash .sp-bar i{display:block;height:100%;width:0;border-radius:9px;background:linear-gradient(90deg,#22d3b6,#ffb020,#ff5c9a)}
#ms-splash.run .sp-bar i{animation:fill 4.6s cubic-bezier(.4,0,.2,1) forwards}
#ms-splash .sp-tap{display:none;margin-top:1.5rem;padding:.7rem 1.5rem;border-radius:999px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.32);backdrop-filter:blur(12px);font-weight:600;animation:breath 1.7s ease-in-out infinite}
#ms-splash.need .sp-tap{display:inline-block}
#ms-splash.need .sp-bar{display:none}
#ms-splash .sp-sc{position:absolute;bottom:5vh;z-index:2;font-size:.85rem;color:rgba(255,255,255,.6);padding:0 1rem}

/* ---------- হিরো ---------- */
.hero{position:relative;overflow:hidden;border-radius:32px;padding:2.3rem 1.8rem 1.9rem;color:#fff;margin:.2rem 0 1.2rem;background:linear-gradient(125deg,#14206b 0%,#4f46e5 28%,#0fb5a6 64%,#22a6f2 100%);background-size:260% 260%;box-shadow:0 30px 60px -26px rgba(79,70,229,.6);animation:aurora 16s ease-in-out infinite,heroIn 1s var(--ios) 10.5s both}
body.ms-ready .hero{animation:aurora 16s ease-in-out infinite,heroIn 1s var(--ios) 0s both}
.hero::before{content:"";position:absolute;width:420px;height:420px;right:-120px;top:-170px;border-radius:50%;background:radial-gradient(circle,rgba(255,176,32,.6),transparent 65%);animation:float 9s ease-in-out infinite}
.hero::after{content:"";position:absolute;width:360px;height:360px;left:-130px;bottom:-200px;border-radius:50%;background:radial-gradient(circle,rgba(255,92,154,.5),transparent 65%);animation:float 11s ease-in-out infinite reverse}
.hero>*{position:relative;z-index:1}
.hello{display:inline-flex;gap:.4rem;align-items:center;padding:.3rem .95rem;border-radius:999px;background:rgba(255,255,255,.16);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.3);font-weight:500;font-size:.92rem}
.hero h1{font-size:clamp(2.3rem,6vw,3.7rem);margin:.7rem 0 .2rem;line-height:1.1;font-weight:800;background:linear-gradient(90deg,#fff,#ffe6a6,#fff);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;animation:shine 6s linear infinite}
.hero p{margin:0;color:#e4ecff;font-size:1.05rem;max-width:640px}
.hch{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1rem}
.hch span{padding:.38rem .9rem;border-radius:999px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.26);font-size:.86rem;font-weight:600;backdrop-filter:blur(8px);transition:transform .45s var(--spring)}
.hch span:hover{transform:translateY(-3px) scale(1.05)}
.hst{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem;margin-top:1.3rem;max-width:540px}
.hst div{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.26);border-radius:20px;padding:.6rem .85rem;backdrop-filter:blur(10px)}
.hst b{display:block;font-family:'Baloo Da 2',sans-serif;font-size:1.7rem;line-height:1.1}
.hst span{font-size:.8rem;color:#dbe6ff}

/* ---------- ট্যাব (iOS সেগমেন্টেড কন্ট্রোল) ---------- */
div[data-baseweb="tab-list"]{gap:4px;padding:6px;border-radius:22px;background:rgba(255,255,255,.7);backdrop-filter:blur(18px) saturate(1.5);border:1px solid rgba(255,255,255,.9);box-shadow:0 12px 30px -16px rgba(20,30,70,.3);overflow-x:auto;scrollbar-width:none}
div[data-baseweb="tab-list"]::-webkit-scrollbar{display:none}
div[data-baseweb="tab-highlight"],div[data-baseweb="tab-border"]{display:none!important}
button[data-baseweb="tab"]{border-radius:16px;padding:.55rem 1rem;height:auto;white-space:nowrap;transition:background .5s var(--ios),color .35s ease,transform .5s var(--spring),box-shadow .5s var(--ios)}
button[data-baseweb="tab"] p{color:inherit!important;font-weight:600;margin:0;font-size:.95rem}
button[data-baseweb="tab"]:hover{background:rgba(79,70,229,.08)}
button[data-baseweb="tab"]:active{transform:scale(.94)}
button[data-baseweb="tab"][aria-selected="true"]{background:var(--tg,linear-gradient(135deg,#4f46e5,#22a6f2));color:#fff!important;transform:scale(1.04);box-shadow:0 10px 22px -8px var(--tc,#4f46e5)}
button[data-baseweb="tab"]:nth-of-type(1){--tg:linear-gradient(135deg,#0fb5a6,#22c55e);--tc:#0fb5a6}
button[data-baseweb="tab"]:nth-of-type(2){--tg:linear-gradient(135deg,#4f46e5,#22a6f2);--tc:#4f46e5}
button[data-baseweb="tab"]:nth-of-type(3){--tg:linear-gradient(135deg,#ffb020,#ff7a1a);--tc:#ff9a1a}
button[data-baseweb="tab"]:nth-of-type(4){--tg:linear-gradient(135deg,#ff5c9a,#ff8a5c);--tc:#ff5c9a}
button[data-baseweb="tab"]:nth-of-type(5){--tg:linear-gradient(135deg,#ff5d5d,#d6336c);--tc:#ff5d5d}
button[data-baseweb="tab"]:nth-of-type(6){--tg:linear-gradient(135deg,#16a34a,#7ddc5a);--tc:#22c55e}
button[data-baseweb="tab"]:nth-of-type(7){--tg:linear-gradient(135deg,#8b5cf6,#c026d3);--tc:#8b5cf6}
button[data-baseweb="tab"]:nth-of-type(8){--tg:linear-gradient(135deg,#14206b,#06b6d4);--tc:#0e7aa8}
.stTabs [data-baseweb="tab-panel"]{padding-top:.6rem;animation:sheet .65s var(--ios) both}

/* ---------- সেকশন ব্যানার ---------- */
.sec{position:relative;overflow:hidden;display:flex;align-items:center;gap:.9rem;margin:.6rem 0 1rem;padding:.95rem 1.1rem;border-radius:24px;color:#fff;background:linear-gradient(120deg,var(--c1),var(--c2));box-shadow:0 20px 36px -20px var(--c1)}
.sec::after{content:"";position:absolute;right:-30px;top:-44px;width:160px;height:160px;border-radius:50%;background:rgba(255,255,255,.17)}
.sec .ic{flex:none;width:54px;height:54px;border-radius:18px;display:grid;place-items:center;font-size:1.8rem;background:rgba(255,255,255,.22);backdrop-filter:blur(8px);animation:pop .8s var(--spring) both}
.sec h2{margin:0;color:#fff;font-size:1.5rem;line-height:1.15}
.sec p{margin:.15rem 0 0;color:rgba(255,255,255,.9);font-size:.94rem}

/* ---------- KPI টাইল ---------- */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.8rem;margin:.4rem 0 1rem}
.kpi{position:relative;overflow:hidden;border-radius:24px;padding:.95rem 1rem;color:#fff;background:linear-gradient(135deg,var(--a),var(--b));box-shadow:0 18px 30px -18px var(--a);animation:pop .75s var(--spring) both;animation-delay:var(--d,0ms);transition:transform .5s var(--spring)}
.kpi:hover{transform:translateY(-4px) scale(1.02)}
.kpi:active{transform:scale(.97)}
.kpi::after{content:"";position:absolute;inset:0;background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.3) 50%,transparent 70%);transform:translateX(-130%);transition:transform .9s var(--ios)}
.kpi:hover::after{transform:translateX(130%)}
.kl{font-size:.86rem;opacity:.93;font-weight:500}
.kv{font-family:'Baloo Da 2',sans-serif;font-size:1.9rem;font-weight:700;line-height:1.2}
.ks{font-size:.78rem;opacity:.86}
.ki{position:absolute;right:.75rem;top:.5rem;font-size:1.6rem;animation:float 5s ease-in-out infinite}

/* ---------- কার্ড ---------- */
.card{position:relative;border-radius:22px;padding:1rem 1.15rem 1rem 1.3rem;margin:.65rem 0;background:rgba(255,255,255,.84);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.95);box-shadow:0 12px 30px -16px rgba(20,30,70,.3);animation:rise .7s var(--ios) both;animation-delay:var(--d,0ms);transition:transform .5s var(--spring),box-shadow .5s var(--ios)}
.card::before{content:"";position:absolute;left:0;top:16px;bottom:16px;width:5px;border-radius:0 6px 6px 0;background:var(--tc,#4f46e5)}
.card:hover{transform:translateY(-3px);box-shadow:0 18px 34px -16px rgba(20,30,70,.35)}
.card.teal{--tc:#0fb5a6}.card.blue{--tc:#22a6f2}.card.amber{--tc:#ffb020}.card.red{--tc:#ff5d5d}.card.violet{--tc:#8b5cf6}.card.rose{--tc:#ff5c9a}.card.green{--tc:#22c55e}.card.indigo{--tc:#4f46e5}
.card-h{display:flex;justify-content:space-between;align-items:center;gap:.6rem;margin-bottom:.3rem}
.card h4{margin:0;font-size:1.1rem}
.card p{margin:.22rem 0;color:#33415c;font-size:.96rem}
.badge{background:#e8eefc;color:#2a3a78;padding:2px 12px;border-radius:999px;font-size:.8rem;font-weight:700;white-space:nowrap}
.badge.red{background:#fde8e8;color:#b03030}.badge.amber{background:#fff1d6;color:#8a5a00}.badge.green{background:#dcf7e5;color:#17703a}.badge.blue{background:#e1f0fb;color:#1f5f8f}
.pill{display:inline-block;background:#fff1d6;color:#8a5a00;padding:5px 12px;border-radius:12px;font-weight:600;margin-top:.4rem;font-size:.88rem}

/* ---------- দোকান কার্ড ---------- */
.scard{position:relative;border-radius:28px;padding:1.05rem 1.1rem 1rem;margin:.8rem 0 .35rem;border:1px solid rgba(255,255,255,.95);background:linear-gradient(160deg,var(--b1),#fff 72%);box-shadow:0 16px 36px -20px var(--sh);animation:rise .7s var(--ios) both;animation-delay:var(--d,0ms);transition:transform .5s var(--spring)}
.scard:hover{transform:translateY(-3px)}
.scard.green{--b1:#d9f7e4;--sh:#16a34a}.scard.amber{--b1:#fdf0c6;--sh:#d97706}.scard.red{--b1:#fddede;--sh:#dc2626}
.sc-top{display:flex;align-items:center;gap:.75rem}
.sc-ico{flex:none;width:50px;height:50px;border-radius:17px;display:grid;place-items:center;font-size:1.6rem;color:#fff;background:linear-gradient(135deg,var(--ac),#4f46e5);box-shadow:0 10px 18px -8px var(--ac)}
.sc-t h4{margin:0;font-size:1.12rem;line-height:1.25}
.sc-t small{color:var(--mut);font-size:.82rem}
.walk{margin-left:auto;white-space:nowrap;padding:.3rem .75rem;border-radius:999px;background:rgba(255,255,255,.85);font-weight:700;font-size:.82rem;color:#2a3a78;box-shadow:0 4px 10px -6px rgba(0,0,0,.3)}
.sc-ad{margin:.55rem 0 .2rem;color:#33415c;font-size:.93rem}
.tg{display:flex;flex-wrap:wrap;gap:.4rem;margin:.4rem 0}
.tg span{padding:.22rem .7rem;border-radius:10px;background:rgba(255,255,255,.85);font-size:.84rem;font-weight:600;color:#33415c}
.mt{display:flex;align-items:center;gap:.6rem;margin:.4rem 0}
.mt label{width:42px;font-size:.84rem;font-weight:600;color:#33415c}
.tr{position:relative;flex:1;height:24px;border-radius:999px;background:rgba(10,18,38,.09);overflow:hidden}
.fl{height:100%;width:var(--w);border-radius:999px;background:var(--c);animation:grow 1.2s var(--ios) both}
.tr b{position:absolute;right:10px;top:0;line-height:24px;font-size:.8rem;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.4)}
.op{color:#16a34a;font-weight:700}.cl2{color:#dc2626;font-weight:700}
.acts{display:flex;gap:.5rem;margin-top:.65rem}
.acts a{flex:1;text-align:center;padding:.55rem .6rem;border-radius:15px;font-weight:700;font-size:.9rem;text-decoration:none;color:#fff!important;transition:transform .35s var(--spring)}
.acts a:active{transform:scale(.95)}
.acts .g1{background:linear-gradient(135deg,#0fb5a6,#22c55e)}.acts .g2{background:linear-gradient(135deg,#4f46e5,#8b5cf6)}

/* ---------- বাজার দর টাইল ---------- */
.ptg{display:grid;grid-template-columns:repeat(auto-fill,minmax(148px,1fr));gap:.75rem;margin:.4rem 0 1rem}
.pt{position:relative;border-radius:22px;padding:.8rem .9rem;background:rgba(255,255,255,.88);border:1px solid rgba(255,255,255,.95);box-shadow:0 12px 26px -18px rgba(20,30,70,.4);animation:pop .7s var(--spring) both;animation-delay:var(--d,0ms);transition:transform .5s var(--spring)}
.pt:hover{transform:translateY(-4px)}
.pt::after{content:"";position:absolute;left:14px;right:14px;bottom:0;height:4px;border-radius:4px 4px 0 0;background:var(--pc)}
.pt.green{--pc:#22c55e}.pt.amber{--pc:#ffb020}.pt.red{--pc:#ff5d5d}
.pt .pe{font-size:1.5rem}.pt .pn{font-weight:700;color:var(--ink);font-size:.95rem}.pt .pu{font-size:.76rem;color:var(--mut)}
.pt .pp{font-family:'Baloo Da 2',sans-serif;font-size:1.5rem;font-weight:700;color:var(--ink);line-height:1.2}
.pt .pg{font-size:.78rem;color:var(--mut);margin-bottom:.3rem}

/* ---------- স্টেপার, স্কেল, চার্ট শিরোনাম ---------- */
.stp{display:flex;margin:.9rem 0 .4rem}
.stp .st{flex:1;position:relative;text-align:center;font-size:.84rem;color:#8a95ad}
.stp .st::before{content:"";position:absolute;top:16px;left:-50%;width:100%;height:4px;background:#e2e7f3}
.stp .st:first-child::before{display:none}
.stp .st i{position:relative;z-index:1;display:grid;place-items:center;width:36px;height:36px;margin:0 auto .3rem;border-radius:50%;background:#e2e7f3;font-style:normal;font-weight:700;transition:all .6s var(--spring)}
.stp .done::before,.stp .cur::before{background:linear-gradient(90deg,#4f46e5,#0fb5a6)}
.stp .done i,.stp .cur i{background:linear-gradient(135deg,#4f46e5,#0fb5a6);color:#fff}
.stp .cur i{animation:pulse 1.8s ease-in-out infinite}
.stp .done,.stp .cur{color:var(--ink);font-weight:600}
.scl{position:relative;margin:2rem 0 .5rem}
.scl .sb{height:14px;border-radius:99px}
.scl .mk{position:absolute;top:-31px;transform:translateX(-50%);transition:left .9s var(--ios);text-align:center}
.scl .mk b{display:block;background:var(--ink);color:#fff;padding:1px 10px;border-radius:10px;font-size:.82rem}
.scl .mk::after{content:"";display:block;margin:0 auto;border:6px solid transparent;border-top-color:var(--ink)}
.sl{display:flex;justify-content:space-between;font-size:.76rem;color:var(--mut)}
.ct{margin:.9rem 0 .2rem}.ct b{font-family:'Baloo Da 2',sans-serif;font-size:1.1rem;color:var(--ink);display:block;line-height:1.2}.ct span{font-size:.82rem;color:var(--mut)}
div[data-testid="stVegaLiteChart"]{background:rgba(255,255,255,.8);border-radius:22px;padding:12px;border:1px solid rgba(255,255,255,.95);box-shadow:0 12px 28px -18px rgba(20,30,70,.3)}

/* ---------- ইনপুট, বাটন, মেট্রিক ---------- */
div[data-baseweb="select"]>div,.stTextInput input,.stTextArea textarea,.stNumberInput input{border-radius:14px!important}
div[data-testid="stForm"]{background:rgba(255,255,255,.72);backdrop-filter:blur(12px);border-radius:24px;border:1px solid rgba(255,255,255,.95);padding:1.1rem;box-shadow:0 12px 28px -18px rgba(20,30,70,.3)}
.stButton>button,.stDownloadButton>button,div[data-testid="stFormSubmitButton"]>button{border-radius:16px;font-weight:700;border:1px solid rgba(79,70,229,.18);background:rgba(255,255,255,.9);color:#2a3a78;transition:transform .45s var(--spring),box-shadow .45s var(--ios),background .3s ease}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);box-shadow:0 12px 22px -10px rgba(79,70,229,.5);border-color:rgba(79,70,229,.4)}
.stButton>button:active,.stDownloadButton>button:active,div[data-testid="stFormSubmitButton"]>button:active{transform:scale(.95)}
.stButton>button[kind="primary"],div[data-testid="stFormSubmitButton"]>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"],div[data-testid="stFormSubmitButton"]>button[data-testid="stBaseButton-primaryFormSubmit"]{background:linear-gradient(135deg,#4f46e5,#22a6f2);color:#fff;border:0}
div[data-testid="stMetric"]{background:rgba(255,255,255,.85);border:1px solid rgba(255,255,255,.95);border-radius:20px;padding:.8rem 1rem;box-shadow:0 10px 24px -16px rgba(20,30,70,.3)}
div[data-testid="stAlert"]{border-radius:18px}
div[data-testid="stExpander"]{border-radius:18px;background:rgba(255,255,255,.7)}

/* ---------- সাইডবার ---------- */
section[data-testid="stSidebar"]{background:linear-gradient(185deg,#0a1226 0%,#14246a 58%,#0e4a5e 100%)}
section[data-testid="stSidebar"] *{color:#e8efff}
.sbb{display:flex;align-items:center;gap:.7rem;margin-bottom:.8rem}
.sbl{width:48px;height:48px;border-radius:16px;display:grid;place-items:center;font-size:1.6rem;background:linear-gradient(145deg,#22d3b6,#4f46e5 60%,#8b5cf6);box-shadow:0 12px 22px -10px rgba(79,70,229,.8)}
.sbb b{font-family:'Baloo Da 2',sans-serif;font-size:1.35rem;display:block;line-height:1.1}.sbb small{font-size:.78rem;opacity:.75}
.sbs{display:flex;align-items:center;gap:.7rem;padding:.65rem .85rem;border-radius:18px;margin:.45rem 0;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.13);transition:transform .45s var(--spring)}
.sbs:hover{transform:translateX(4px)}
.sbs i{font-style:normal;font-size:1.3rem}.sbs b{font-family:'Baloo Da 2',sans-serif;font-size:1.35rem;line-height:1}.sbs span{display:block;font-size:.76rem;opacity:.75}
.how{font-size:.9rem;line-height:1.7}
.how b{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:linear-gradient(135deg,#ffb020,#ff7a1a);color:#fff!important;font-size:.78rem;margin-right:.4rem}
.foot{text-align:center;color:var(--mut);padding:1.4rem .6rem 0;font-size:.9rem}

/* ---------- কীফ্রেম ---------- */
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.88) translateY(10px)}to{opacity:1;transform:none}}
@keyframes sheet{from{opacity:0;transform:translateY(22px) scale(.985);filter:blur(5px)}to{opacity:1;transform:none;filter:none}}
@keyframes grow{from{width:0}to{width:var(--w)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
@keyframes aurora{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@keyframes shine{to{background-position:-200% 0}}
@keyframes drift{to{transform:translate3d(3%,-2%,0) scale(1.08)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(79,70,229,.45)}50%{box-shadow:0 0 0 10px rgba(79,70,229,0)}}
@keyframes heroIn{from{opacity:0;transform:translateY(26px) scale(.96);filter:blur(8px)}to{opacity:1;transform:none;filter:none}}
@keyframes blob{to{transform:translate3d(6vmax,4vmax,0) scale(1.15)}}
@keyframes logoIn{0%{opacity:0;transform:scale(.3) rotate(-14deg)}60%{opacity:1;transform:scale(1.1) rotate(3deg)}100%{transform:none}}
@keyframes ring{0%{transform:scale(.9);opacity:.8}100%{transform:scale(1.7);opacity:0}}
@keyframes letter{from{opacity:0;transform:translateY(22px);filter:blur(10px)}to{opacity:1;transform:none;filter:none}}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes fill{to{width:100%}}
@keyframes breath{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.06);opacity:1}}
@keyframes splashOut{0%{opacity:1;transform:scale(1);filter:none}100%{opacity:0;transform:scale(1.18);filter:blur(16px);visibility:hidden}}
@keyframes splashFallback{to{opacity:0;visibility:hidden;pointer-events:none}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
@media (max-width:640px){.block-container{padding:.6rem .6rem 3rem}.hero{padding:1.7rem 1.1rem 1.4rem;border-radius:26px}.sec h2{font-size:1.25rem}.walk{display:none}}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

# ======================================================================
#  সাউন্ড + স্প্ল্যাশ নিয়ন্ত্রণ (শুধু সেশনের প্রথমবার)
# ======================================================================
SPLASH = """<div id="ms-splash"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="blob b4"></div>
<div class="sp-in"><div class="logo"><span class="ring"></span><span class="ring r2"></span><span class="gl">🛰️</span></div>
<div class="sp-t"><span style="--i:0">মানব</span> <span style="--i:1">সাথি</span></div>
<div class="sp-s">দোকান · দাম · সেবা — সব এক জায়গায়</div>
<div class="sp-bar"><i></i></div><div class="sp-tap">👆 স্পর্শ করে শুরু করুন</div></div>
<div class="sp-sc">কালিয়াগঞ্জ নাজিরতন উচ্চ বিদ্যালয় (SOUNDARJYA)</div></div>"""

SOUND_JS = r"""(function(){
var W=window;
if(W.__manab){ if(W.__manab.begin) W.__manab.begin(); return; }
W.__manab={};
try{W.__manabMute=(W.localStorage.getItem('ms_mute')==='1');}catch(e){W.__manabMute=false;}
var AUD=__AUD__, snd={}, started=false;
Object.keys(AUD).forEach(function(k){var a=new Audio(AUD[k]);a.preload='auto';a.volume=(k==='open')?0.95:0.85;snd[k]=a;});
function play(k){
  if(W.__manabMute||!snd[k])return;
  try{Object.keys(snd).forEach(function(x){if(x!==k)snd[x].pause();});
  var a=snd[k];a.currentTime=0;var p=a.play();if(p&&p.catch)p.catch(function(){});}catch(e){}
}
W.__manab.play=play;
document.addEventListener('click',function(e){
  var t=e.target&&e.target.closest?e.target.closest('button[data-baseweb="tab"],button[role="tab"]'):null;
  if(!t||t.getAttribute('aria-selected')==='true')return;
  var x=t.textContent||'',k=null;
  if(x.indexOf('বাজার দর')>-1)k='bazar';
  else if(x.indexOf('দোকান তালিকা')>-1)k='dokan';
  else if(x.indexOf('অভিযোগ')>-1)k='ovijog';
  if(k)play(k);
},true);
function sp(){return document.getElementById('ms-splash');}
function ready(){document.body.classList.add('ms-ready');}
function run(){
  var s=sp();if(!s||started)return;started=true;
  s.classList.remove('need');s.classList.add('run');
  setTimeout(function(){s.classList.add('out');ready();},5000);
  setTimeout(function(){var x=sp();if(x)x.remove();},6400);
}
function arm(){
  var ev=['pointerdown','touchstart','keydown','click'];
  var h=function(){
    ev.forEach(function(n){document.removeEventListener(n,h,true);});
    if(sp()&&!started){try{snd.open.currentTime=0;var p=snd.open.play();if(p&&p.catch)p.catch(function(){});}catch(e){}run();}
  };
  ev.forEach(function(n){document.addEventListener(n,h,true);});
}
function begin(){
  started=false;var tries=0;
  (function wait(){
    var s=sp();
    if(!s){if(tries++<40){setTimeout(wait,100);}else{ready();}return;}
    if(!snd.open||W.__manabMute){run();return;}
    var p;try{p=snd.open.play();}catch(e){}
    if(p&&p.then){p.then(run).catch(function(){s.classList.add('need');arm();});}else{run();}
  })();
}
W.__manab.begin=begin;
begin();
})();"""


@st.cache_resource(show_spinner=False)
def load_audio():
    out = {}
    for key, fname in AUDIO_FILES.items():
        p = AUDIO_DIR / fname
        if p.exists():
            out[key] = "data:audio/mpeg;base64," + base64.b64encode(p.read_bytes()).decode()
    return out


def boot_html():
    code = SOUND_JS.replace("__AUD__", json.dumps(load_audio())).replace("</", "<\\/")
    return ("<script>try{var P=window.parent;var s=P.document.createElement('script');s.id='ms-sound-js';"
            "s.textContent=" + json.dumps(code).replace("</", "<\\/") + ";P.document.head.appendChild(s);}catch(e){}</script>")


MUTE_HTML = """<link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@500;600&display=swap" rel="stylesheet">
<style>body{margin:0;font-family:'Hind Siliguri',sans-serif}.row{display:flex;align-items:center;justify-content:space-between;padding:.5rem .85rem;border-radius:18px;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.15);color:#e8efff;font-size:14px;font-weight:600}
.sw{width:48px;height:28px;border:0;border-radius:99px;background:#22c55e;position:relative;cursor:pointer;transition:background .4s cubic-bezier(.32,.72,0,1)}
.sw i{position:absolute;top:3px;left:23px;width:22px;height:22px;border-radius:50%;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.35);transition:left .45s cubic-bezier(.34,1.56,.64,1)}
.sw.off{background:#5b6788}.sw.off i{left:3px}.sw:active i{width:27px}</style>
<div class="row"><span id="lb">🔊 সাউন্ড চালু</span><button class="sw" id="sw" aria-label="সাউন্ড"><i></i></button></div>
<script>var P=window.parent,b=document.getElementById('sw'),l=document.getElementById('lb');
function r(){var m=!!P.__manabMute;b.className='sw'+(m?' off':'');l.textContent=m?'🔇 সাউন্ড বন্ধ':'🔊 সাউন্ড চালু'}
setTimeout(r,300);
b.onclick=function(){P.__manabMute=!P.__manabMute;try{P.localStorage.setItem('ms_mute',P.__manabMute?'1':'0')}catch(e){}r()};r();</script>"""

# ======================================================================
#  সহায়ক ফাংশন
# ======================================================================
MONTHS = ["জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল", "মে", "জুন", "জুলাই", "আগস্ট", "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"]
WEEK = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"]


def bn(x):
    return str(x).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


def now_dt():
    return datetime.now(BD)


def period(h):
    return "ভোর" if 4 <= h < 6 else "সকাল" if 6 <= h < 12 else "দুপুর" if 12 <= h < 15 else "বিকাল" if 15 <= h < 17 else "সন্ধ্যা" if 17 <= h < 19 else "রাত"


def now():
    d = now_dt()
    mm = f"{d.minute:02d}"
    return f"{bn(d.day)} {MONTHS[d.month - 1]} {bn(d.year)}, {period(d.hour)} {bn(d.hour % 12 or 12)}:{bn(mm)}"


def greet():
    return {"ভোর": "শুভ ভোর", "সকাল": "শুভ সকাল", "দুপুর": "শুভ দুপুর", "বিকাল": "শুভ অপরাহ্ন", "সন্ধ্যা": "শুভ সন্ধ্যা", "রাত": "শুভ রাত্রি"}[period(now_dt().hour)]


def txt(v):
    return "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v).strip()


def esc(v):
    t = txt(v)
    return html.escape(t) if t else "—"


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


G = {"teal": ("#0fb5a6", "#22c55e"), "indigo": ("#4f46e5", "#22a6f2"), "amber": ("#ffb020", "#ff7a1a"), "rose": ("#ff5c9a", "#ff8a5c"),
     "violet": ("#8b5cf6", "#c026d3"), "red": ("#ff5d5d", "#d6336c"), "navy": ("#14206b", "#06b6d4"), "green": ("#16a34a", "#7ddc5a"), "sky": ("#22a6f2", "#4f46e5")}


def head(title, sub, icon, g):
    c1, c2 = G[g]
    st.markdown(f'<div class="sec" style="--c1:{c1};--c2:{c2}"><div class="ic">{icon}</div><div><h2>{title}</h2><p>{sub}</p></div></div>', unsafe_allow_html=True)


def kpis(items):
    out = []
    for n, (label, value, sub, icon, g) in enumerate(items):
        a, b = G[g]
        out.append(f'<div class="kpi" style="--a:{a};--b:{b};--d:{n * 90}ms"><span class="ki">{icon}</span><div class="kl">{label}</div><div class="kv">{value}</div><div class="ks">{sub}</div></div>')
    st.markdown('<div class="kpis">' + "".join(out) + "</div>", unsafe_allow_html=True)


def card(title, lines, badge="", badge_cls="", extra="", tone="indigo", i=0):
    b = f'<span class="badge {badge_cls}">{badge}</span>' if badge else ""
    body = "".join(f"<p>{l}</p>" for l in lines)
    return f'<div class="card {tone}" style="--d:{i * 70}ms"><div class="card-h"><h4>{title}</h4>{b}</div>{body}{extra}</div>'


def ctitle(t, s=""):
    st.markdown(f'<div class="ct"><b>{t}</b><span>{s}</span></div>', unsafe_allow_html=True)


def table(df, **kw):
    st.dataframe(df, hide_index=True, **STRETCH, **kw)


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
    pts = np.array([np.random.default_rng(zlib.crc32(str(i).strip().upper().encode())).uniform(-0.03, 0.03, 2) for i in d["দোকান আইডি"]]).reshape(-1, 2)
    d["lat"], d["lon"] = BASE[0] + pts[:, 0], BASE[1] + pts[:, 1]
    d["distance_km"] = np.round(np.hypot(pts[:, 0], pts[:, 1] * np.cos(np.radians(BASE[0]))) * 111, 2)
    d["name"] = d["দোকানের নাম"].astype(str)
    return d


HOURS = [((7, 22), "সকাল ৭টা – রাত ১০টা"), ((6, 21), "সকাল ৬টা – রাত ৯টা"), ((8, 23), "সকাল ৮টা – রাত ১১টা"), ((9, 21), "সকাল ৯টা – রাত ৯টা"), ((0, 24), "২৪ ঘণ্টা খোলা")]


def demo_meta(sid):
    """ডেমো সূচক: স্টক %, ভিড়, খোলার সময় (দোকান আইডি থেকে নির্ধারিত)।"""
    rng = np.random.default_rng(zlib.crc32(("meta:" + sid.strip().upper()).encode()))
    (o, c), label = HOURS[int(rng.integers(0, len(HOURS)))]
    t = now_dt()
    hh = t.hour + t.minute / 60
    return {"stock": int(rng.integers(12, 98)), "crowd": int(rng.choice([0, 1, 2], p=[.45, .35, .2])), "hours": label, "open": bool(o <= hh < c)}


def req_state(r):
    s = r.get("state")
    if s in ("pending", "yes", "no"):
        return s
    t = str(r.get("status", ""))
    return "pending" if "অপেক্ষা" in t else ("no" if "নেই" in t else "yes")


def is_pending(r):
    return req_state(r) == "pending"


def req_for(reqs, sid, product):
    for r in reqs:
        if str(r.get("store_id", "")).upper() == sid.upper() and r.get("product") == product:
            return r
    return None


def store_payload(df, reqs, product=None):
    out = []
    for _, r in df.iterrows():
        sid = txt(r.get("দোকান আইডি"))
        m = demo_meta(sid)
        stock, src = m["stock"], "demo"
        if product:
            q = req_for(reqs, sid, product)
            s = req_state(q) if q else None
            if s == "yes":
                stock, src = 96, "yes"
            elif s == "no":
                stock, src = 4, "no"
        prod = ""
        if product:
            prod = f'{txt(r.get("প্রোডাক্টের নাম"))} ({txt(r.get("ওজন/সাইজ"))}) · {txt(r.get("ব্র্যান্ড"))}'
        out.append({"id": sid, "name": txt(r.get("দোকানের নাম")), "addr": txt(r.get("ঠিকানা")), "phone": txt(r.get("যোগাযোগ নম্বর")),
                    "lat": round(float(r["lat"]), 6), "lon": round(float(r["lon"]), 6), "stock": stock, "src": src, "crowd": m["crowd"],
                    "hours": m["hours"], "open": m["open"], "d": float(r["distance_km"]), "prod": prod})
    return out


# ======================================================================
#  ইন্টার‍্যাক্টিভ ম্যাপ (Leaflet: স্যাটেলাইট/হাইব্রিড/রাস্তা/ডার্ক + আপনার লোকেশন)
# ======================================================================
MAP_TPL = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.css">
<link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Baloo+Da+2:wght@700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:transparent;font-family:'Hind Siliguri',sans-serif}
#wrap{position:relative;height:__H__px;border-radius:26px;overflow:hidden;background:#dfe6f3;box-shadow:0 0 0 1px rgba(255,255,255,.8),0 18px 36px -20px rgba(10,18,38,.5)}
#map{position:absolute;inset:0;background:#cfd8ea}
.glass{background:rgba(255,255,255,.84);-webkit-backdrop-filter:blur(14px) saturate(1.5);backdrop-filter:blur(14px) saturate(1.5);border:1px solid rgba(255,255,255,.9);box-shadow:0 10px 26px rgba(10,18,38,.25)}
#seg{position:absolute;left:12px;top:12px;z-index:1200;display:flex;gap:2px;padding:4px;border-radius:18px}
#seg button{border:0;background:transparent;padding:7px 11px;border-radius:14px;font:600 12.5px 'Hind Siliguri';color:#33415c;cursor:pointer;transition:all .45s cubic-bezier(.34,1.56,.64,1)}
#seg button.on{background:linear-gradient(135deg,#4f46e5,#22a6f2);color:#fff;transform:scale(1.05);box-shadow:0 8px 16px -6px rgba(79,70,229,.7)}
#cnt{position:absolute;right:12px;top:12px;z-index:1200;padding:8px 14px;border-radius:16px;font:700 13px 'Hind Siliguri';color:#0a1226}
#tools{position:absolute;right:12px;top:58px;z-index:1200;display:flex;flex-direction:column;gap:8px}
#tools button{width:42px;height:42px;border-radius:15px;font:700 18px 'Hind Siliguri';color:#33415c;cursor:pointer;border:1px solid rgba(255,255,255,.9);transition:transform .4s cubic-bezier(.34,1.56,.64,1),background .3s}
#tools button:active{transform:scale(.88)}
#loc.on{background:linear-gradient(135deg,#2f7bff,#22a6f2);color:#fff}
#lg{position:absolute;left:12px;bottom:12px;z-index:1200;display:flex;flex-wrap:wrap;gap:4px 11px;padding:7px 12px;border-radius:15px;font:500 11.5px 'Hind Siliguri';color:#33415c;max-width:calc(100% - 80px)}
#lg i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}
#near,#toast{position:absolute;z-index:1250;padding:8px 14px;border-radius:16px;font:500 13px 'Hind Siliguri';color:#0a1226;opacity:0;pointer-events:none;transition:opacity .5s ease,transform .6s cubic-bezier(.32,.72,0,1)}
#near{left:12px;top:60px;max-width:calc(100% - 80px);transform:translateY(-10px);cursor:pointer}
#near.on{opacity:1;transform:none;pointer-events:auto}
#toast{left:50%;bottom:62px;transform:translate(-50%,16px);white-space:nowrap}
#toast.on{opacity:1;transform:translate(-50%,0)}
#sheet{position:absolute;left:10px;right:10px;bottom:10px;z-index:1300;max-width:540px;margin:0 auto;border-radius:26px;padding:10px 15px 15px;transform:translateY(125%);transition:transform .65s cubic-bezier(.32,.72,0,1)}
#sheet.on{transform:none}
.grab{width:40px;height:5px;border-radius:9px;background:#c9d1e4;margin:0 auto 9px}
.hd{display:flex;align-items:center;gap:11px}
.av{width:48px;height:48px;border-radius:16px;display:grid;place-items:center;font-size:24px;flex:none;background:linear-gradient(135deg,var(--c),#4f46e5);box-shadow:0 10px 18px -8px var(--c)}
.hd b{display:block;font:700 16px 'Hind Siliguri';color:#0a1226;line-height:1.25}.hd small{color:#5d6b86;font-size:12px}
.op{color:#16a34a;font-weight:700}.cl2{color:#dc2626;font-weight:700}
.x{margin-left:auto;border:0;background:#e6eaf5;width:30px;height:30px;border-radius:50%;cursor:pointer;font-size:13px;color:#33415c;flex:none}
.ad{margin:8px 0 2px;color:#33415c;font-size:13px;line-height:1.5}.ad em{font-style:normal}
.mt{display:flex;align-items:center;gap:8px;margin:6px 0;font-size:12px;font-weight:600;color:#33415c}.mt span{width:36px}
.tr{flex:1;height:21px;border-radius:99px;background:#e3e8f4;position:relative;overflow:hidden}
.fl{height:100%;width:0;border-radius:99px;transition:width 1s cubic-bezier(.32,.72,0,1)}
.tr b{position:absolute;right:9px;top:0;line-height:21px;font-size:11.5px;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.4)}
.ac{display:flex;gap:8px;margin-top:11px}
.ac a{flex:1;text-align:center;padding:10px 6px;border-radius:15px;text-decoration:none;font:700 13px 'Hind Siliguri';color:#fff;transition:transform .35s cubic-bezier(.34,1.56,.64,1)}
.ac a:active{transform:scale(.94)}.a1{background:linear-gradient(135deg,#0fb5a6,#22c55e)}.a2{background:linear-gradient(135deg,#4f46e5,#8b5cf6)}
.pin{position:relative;width:26px;height:26px;margin:2px;border-radius:50%;background:var(--c);border:3px solid #fff;box-shadow:0 7px 14px rgba(0,0,0,.4);transition:transform .35s cubic-bezier(.34,1.56,.64,1)}
.pin:hover{transform:scale(1.25)}
.pin i{position:absolute;inset:4px;border-radius:50%;background:rgba(255,255,255,.92)}
.pin::after{content:"";position:absolute;inset:-3px;border-radius:50%;border:2px solid var(--c);opacity:0}
.pin.pu::after{animation:ping 2.2s ease-out infinite}
@keyframes ping{0%{transform:scale(.9);opacity:.95}100%{transform:scale(2.5);opacity:0}}
.cl{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;color:#fff;font:700 15px 'Baloo Da 2';background:radial-gradient(circle at 30% 25%,#7c8cff,#4f46e5 60%,#2a2fa8);border:3px solid rgba(255,255,255,.95);box-shadow:0 0 0 7px rgba(79,70,229,.28),0 10px 20px rgba(10,18,38,.4);transition:transform .35s cubic-bezier(.34,1.56,.64,1)}
.cl:hover{transform:scale(1.12)}
.me{position:relative;width:26px;height:26px}
.me i{position:absolute;inset:3px;border-radius:50%;background:#2f7bff;border:3px solid #fff;box-shadow:0 3px 10px rgba(0,0,0,.45)}
.me span{position:absolute;inset:-12px;border-radius:50%;background:rgba(47,123,255,.3);animation:ping 2s ease-out infinite}
.route{animation:dash 1.2s linear infinite}
@keyframes dash{to{stroke-dashoffset:-28}}
.leaflet-tooltip{border:0;border-radius:12px;font:600 12.5px 'Hind Siliguri';box-shadow:0 8px 18px rgba(0,0,0,.25)}
.leaflet-control-attribution{font-size:9px!important;background:rgba(255,255,255,.7)!important;border-radius:10px 0 0 0}
</style></head><body>
<div id="wrap"><div id="map"></div>
<div id="seg" class="glass"><button data-b="hybrid">🛰️ স্যাটেলাইট</button><button data-b="street">🗺️ রাস্তা</button><button data-b="dark">🌙 ডার্ক</button></div>
<div id="cnt" class="glass"></div>
<div id="tools"><button id="loc" class="glass" title="আমার অবস্থান">📍</button><button id="fit" class="glass" title="সব দেখুন">⤢</button><button id="zi" class="glass">+</button><button id="zo" class="glass">−</button><button id="lock" class="glass" title="ম্যাপ টানা চালু/বন্ধ" style="display:none">✋</button></div>
<div id="near" class="glass"></div><div id="toast" class="glass"></div>
<div id="lg" class="glass"><span><i style="background:#22c55e"></i>স্টক ভালো</span><span><i style="background:#f59e0b"></i>মাঝারি</span><span><i style="background:#ef4444"></i>কম/নেই</span><span><i style="background:#2f7bff"></i>আপনি</span></div>
<div id="sheet" class="glass"></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js"></script>
<script>
(function(){
if(typeof L==='undefined'){document.getElementById('map').innerHTML='<div style="padding:26px;font:600 14px Hind Siliguri;color:#33415c">ম্যাপ লোড হয়নি — ইন্টারনেট সংযোগ দেখুন।</div>';return;}
var DATA=__DATA__,BASE0='__BASE__',PULSE=__PULSE__,USER=null,meM=null,accC=null,nearLine=null;
function bn(s){return String(s).replace(/[0-9]/g,function(d){return '০১২৩৪৫৬৭৮৯'.charAt(d)})}
function E(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function hav(a,b,c,d){var p=Math.PI/180,x=(c-a)*p,y=(d-b)*p,h=Math.sin(x/2)*Math.sin(x/2)+Math.cos(a*p)*Math.cos(c*p)*Math.sin(y/2)*Math.sin(y/2);return 12742*Math.asin(Math.sqrt(h))}
function fmt(k){return k<1?bn(Math.round(k*1000))+' মিটার':bn(k.toFixed(1))+' কিমি'}
function col(v){return v>=60?'#22c55e':v>=30?'#f59e0b':'#ef4444'}
var $=function(i){return document.getElementById(i)};
var CEN=DATA.length?[DATA.reduce(function(a,s){return a+s.lat},0)/DATA.length,DATA.reduce(function(a,s){return a+s.lon},0)/DATA.length]:[25.85,88.6];
var mobile=L.Browser.mobile;
var map=L.map('map',{zoomControl:false,attributionControl:false,zoomSnap:.25,zoomDelta:.5,wheelPxPerZoomLevel:110,scrollWheelZoom:false,dragging:!mobile,inertia:true,maxZoom:20}).setView(CEN,13);
L.control.attribution({prefix:false,position:'bottomright'}).addTo(map);
var ES='https://server.arcgisonline.com/ArcGIS/rest/services/';
var img=L.tileLayer(ES+'World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:20,maxNativeZoom:18,attribution:'Imagery © Esri, Maxar, Earthstar Geographics'});
var trn=L.tileLayer(ES+'Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}',{maxZoom:20,maxNativeZoom:17,opacity:.85});
var plc=L.tileLayer(ES+'Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',{maxZoom:20,maxNativeZoom:17});
var voy=L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',{subdomains:'abcd',maxZoom:20,attribution:'© OpenStreetMap © CARTO'});
var drk=L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{subdomains:'abcd',maxZoom:20,attribution:'© OpenStreetMap © CARTO'});
var SETS={hybrid:[img,trn,plc],street:[voy],dark:[drk]},cur=[];
function setBase(k){cur.forEach(function(l){map.removeLayer(l)});cur=SETS[k]||SETS.hybrid;cur.forEach(function(l){l.addTo(map)});
 var b=document.querySelectorAll('#seg button');for(var i=0;i<b.length;i++){b[i].classList.toggle('on',b[i].getAttribute('data-b')===k)}}
var sb=document.querySelectorAll('#seg button');for(var i=0;i<sb.length;i++){sb[i].onclick=function(){setBase(this.getAttribute('data-b'))}}
setBase(SETS[BASE0]?BASE0:'hybrid');
$('cnt').innerHTML='🏪 '+bn(DATA.length)+'টি দোকান';
function toast(t){var e=$('toast');e.textContent=t;e.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(function(){e.classList.remove('on')},2800)}
var sheet=$('sheet');
function closeSheet(){sheet.classList.remove('on')}
function meter(l,p,t,c){return '<div class="mt"><span>'+l+'</span><div class="tr"><div class="fl" data-w="'+p+'" style="background:'+c+'"></div><b>'+t+'</b></div></div>'}
function openSheet(s){
 var cr=[['কম',24,'#22c55e'],['মাঝারি',58,'#f59e0b'],['বেশি',90,'#ef4444']][s.crowd||0];
 var stT=s.src==='yes'?'আছে ✓':s.src==='no'?'নেই':bn(s.stock)+'%';
 var du='';if(USER){var d=hav(USER.lat,USER.lon,s.lat,s.lon);if(d<80)du='<br>🚶 আপনার থেকে '+fmt(d)}
 var dir='https://www.google.com/maps/dir/?api=1&destination='+s.lat+','+s.lon+(USER?'&origin='+USER.lat+','+USER.lon:'');
 var ph=String(s.phone||'').replace(/[^0-9+]/g,'');
 var tag=s.src==='demo'?'আনুমানিক (ডেমো সূচক)':'দোকানদার নিশ্চিত করেছেন';
 sheet.innerHTML='<div class="grab"></div><div class="hd"><div class="av" style="--c:'+col(s.stock)+'">🏪</div><div><b>'+E(s.name)+'</b><small><span class="'+(s.open?'op':'cl2')+'">'+(s.open?'এখন খোলা':'এখন বন্ধ')+'</span> · '+E(s.hours)+'</small></div><button class="x" id="xs">✕</button></div>'
 +'<div class="ad">📍 '+E(s.addr||'ঠিকানা নেই')+'<br>🧭 ম্যাপ কেন্দ্র থেকে '+fmt(s.d)+du+'</div>'
 +(s.prod?'<div class="ad">📦 '+E(s.prod)+'</div>':'')
 +meter('স্টক',Math.max(s.stock,8),stT,col(s.stock))+meter('ভিড়',cr[1],cr[0],cr[2])
 +'<div class="ad" style="font-size:11px;color:#8591aa">স্টক ও ভিড়: '+tag+'</div>'
 +'<div class="ac"><a class="a1" target="_blank" rel="noopener" href="'+dir+'">🧭 দিকনির্দেশ</a>'+(ph?'<a class="a2" target="_blank" href="tel:'+ph+'">📞 কল করুন</a>':'')+'</div>';
 sheet.classList.add('on');$('xs').onclick=closeSheet;
 requestAnimationFrame(function(){requestAnimationFrame(function(){var f=sheet.querySelectorAll('.fl');for(var i=0;i<f.length;i++)f[i].style.width=f[i].getAttribute('data-w')+'%'})});
}
var grp=(L.markerClusterGroup?L.markerClusterGroup({showCoverageOnHover:false,maxClusterRadius:46,spiderfyOnMaxZoom:true,animate:true,iconCreateFunction:function(c){return L.divIcon({className:'',html:'<div class="cl">'+bn(c.getChildCount())+'</div>',iconSize:[46,46]})}}):L.layerGroup()).addTo(map);
DATA.forEach(function(s){
 var ic=L.divIcon({className:'',html:'<div class="pin'+(PULSE?' pu':'')+'" style="--c:'+col(s.stock)+'"><i></i></div>',iconSize:[32,32],iconAnchor:[16,16]});
 var m=L.marker([s.lat,s.lon],{icon:ic,riseOnHover:true,keyboard:false});
 m.bindTooltip(E(s.name),{direction:'top',offset:[0,-14]});
 m.on('click',function(){openSheet(s);map.flyTo([s.lat,s.lon],Math.max(map.getZoom(),16),{duration:1});});
 grp.addLayer(m);
});
var BOUNDS=DATA.length?L.latLngBounds(DATA.map(function(s){return [s.lat,s.lon]})):null;
function fitAll(fly){if(!BOUNDS)return;var o={padding:[60,60],maxZoom:15};if(fly){o.duration=1.1;map.flyToBounds(BOUNDS,o)}else map.fitBounds(BOUNDS,o)}
fitAll(false);
map.on('click',function(){closeSheet();map.scrollWheelZoom.enable()});
map.on('mouseout',function(){map.scrollWheelZoom.disable()});
$('fit').onclick=function(){fitAll(true)};
$('zi').onclick=function(){map.zoomIn(1)};$('zo').onclick=function(){map.zoomOut(1)};
if(mobile){var lk=$('lock');lk.style.display='block';lk.onclick=function(){if(map.dragging.enabled()){map.dragging.disable();lk.textContent='✋'}else{map.dragging.enable();lk.textContent='🔒';toast('ম্যাপ টানা চালু — আবার চাপলে পেজ স্ক্রল')}}}
var meIcon=L.divIcon({className:'',html:'<div class="me"><span></span><i></i></div>',iconSize:[26,26],iconAnchor:[13,13]});
function onLoc(p){
 var la=p.coords.latitude,lo=p.coords.longitude,ac=p.coords.accuracy||30,first=!USER;USER={lat:la,lon:lo};
 if(!meM){meM=L.marker([la,lo],{icon:meIcon,zIndexOffset:5000,keyboard:false}).addTo(map);meM.bindTooltip('আপনি এখানে',{direction:'top',offset:[0,-14]});
  accC=L.circle([la,lo],{radius:ac,color:'#2f7bff',weight:1,fillColor:'#2f7bff',fillOpacity:.1,interactive:false}).addTo(map)}
 else{meM.setLatLng([la,lo]);accC.setLatLng([la,lo]);accC.setRadius(ac)}
 $('loc').classList.add('on');
 if(!first)return;
 var best=null;DATA.forEach(function(s){var d=hav(la,lo,s.lat,s.lon);if(!best||d<best.d)best={s:s,d:d}});
 if(best&&best.d<60){
  var n=$('near');n.innerHTML='📍 সবচেয়ে কাছে: <b>'+E(best.s.name)+'</b> · '+fmt(best.d);n.classList.add('on');
  n.onclick=function(){openSheet(best.s);map.flyTo([best.s.lat,best.s.lon],16,{duration:1.1})};
  nearLine=L.polyline([[la,lo],[best.s.lat,best.s.lon]],{color:'#2f7bff',weight:3,dashArray:'8 6',opacity:.95,className:'route',interactive:false}).addTo(map);
  map.flyToBounds(L.latLngBounds([[la,lo],[best.s.lat,best.s.lon]]).pad(.6),{maxZoom:16,duration:1.4});
 }else{toast('📍 আপনার অবস্থান ম্যাপে চিহ্নিত হয়েছে — ডান পাশের 📍 চাপুন')}
}
function geo(){
 var gs=[];try{if(navigator.geolocation)gs.push(navigator.geolocation)}catch(e){}
 try{if(window.parent.navigator.geolocation)gs.push(window.parent.navigator.geolocation)}catch(e){}
 var i=0;(function next(){var g=gs[i++];if(!g){toast('লোকেশন পাওয়া যায়নি — ব্রাউজারে অনুমতি দিন');return}
  g.getCurrentPosition(function(p){onLoc(p);try{g.watchPosition(onLoc,function(){},{enableHighAccuracy:true,maximumAge:8000})}catch(e){}},function(){next()},{enableHighAccuracy:true,timeout:9000,maximumAge:30000})})();
}
$('loc').onclick=function(){if(USER){map.flyTo([USER.lat,USER.lon],16,{duration:1.2})}else{toast('আপনার অবস্থান খোঁজা হচ্ছে…');geo()}};
geo();
})();
</script></body></html>"""


def embed_map(stores, height=480, base="hybrid", pulse=True):
    if not stores:
        return
    src = (MAP_TPL.replace("__DATA__", json.dumps(stores, ensure_ascii=False).replace("</", "<\\/"))
           .replace("__H__", str(height)).replace("__BASE__", base).replace("__PULSE__", "true" if pulse else "false"))
    components.html(src, height=height + 6)


# ======================================================================
#  চার্ট (Altair) — গ্রেডিয়েন্ট, গোল কোণা, টুলটিপ
# ======================================================================
FONT = "Hind Siliguri"
PAL = ["#4f46e5", "#0fb5a6", "#ffb020", "#ff5c9a", "#22a6f2", "#8b5cf6", "#ff7a1a", "#22c55e", "#ff5d5d"]


def _cfg(ch, h):
    return (ch.properties(height=h, background="rgba(0,0,0,0)").configure_view(strokeWidth=0)
            .configure_axis(labelFont=FONT, titleFont=FONT, labelColor="#5d6b86", titleColor="#33415c", gridColor="#e8ecf6", domain=False, tickColor="rgba(0,0,0,0)", labelFontSize=12)
            .configure_legend(labelFont=FONT, titleFont=FONT, orient="top", labelFontSize=12, symbolType="circle", padding=4)
            .configure_title(font=FONT))


def gv(c1, c2):
    return alt.Gradient(gradient="linear", stops=[alt.GradientStop(color=c1, offset=0), alt.GradientStop(color=c2, offset=1)], x1=1, x2=1, y1=1, y2=0)


def gh(c1, c2):
    return alt.Gradient(gradient="linear", stops=[alt.GradientStop(color=c1, offset=0), alt.GradientStop(color=c2, offset=1)], x1=0, x2=1, y1=0, y2=0)


def draw(build):
    if alt is None:
        st.caption("চার্ট দেখতে `pip install altair` করুন।")
        return
    try:
        st.altair_chart(build(), theme=None, **STRETCH)
    except Exception:
        st.caption("চার্ট দেখানো যায়নি — `altair` সংস্করণ হালনাগাদ করুন।")


def ch_grouped(df, cat, grp, val, colors, h=300):
    ch = alt.Chart(df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
        x=alt.X(cat, type="nominal", sort=None, axis=alt.Axis(title=None, labelAngle=-30, labelLimit=120)),
        xOffset=alt.XOffset(grp, type="nominal"),
        y=alt.Y(val, type="quantitative", axis=alt.Axis(title=None)),
        color=alt.Color(grp, type="nominal", scale=alt.Scale(domain=list(colors), range=list(colors.values())), legend=alt.Legend(title=None)),
        tooltip=[alt.Tooltip(cat, type="nominal"), alt.Tooltip(grp, type="nominal"), alt.Tooltip(val, type="quantitative")])
    return _cfg(ch, h)


def ch_hbar(df, cat, val, c1, c2, h=260, sort="-x"):
    bars = alt.Chart(df).mark_bar(cornerRadiusTopRight=10, cornerRadiusBottomRight=10, size=18, color=gh(c1, c2)).encode(
        y=alt.Y(cat, type="nominal", sort=sort, axis=alt.Axis(title=None, labelLimit=170)),
        x=alt.X(val, type="quantitative", axis=alt.Axis(title=None)),
        tooltip=[alt.Tooltip(cat, type="nominal"), alt.Tooltip(val, type="quantitative")])
    lab = alt.Chart(df).mark_text(align="left", dx=6, font=FONT, fontWeight=600, color="#33415c").encode(
        y=alt.Y(cat, type="nominal", sort=sort), x=alt.X(val, type="quantitative"), text=alt.Text(val, type="quantitative"))
    return _cfg(alt.layer(bars, lab), h)


def ch_status(df, cat, val, cat_col, colors, h=260):
    bars = alt.Chart(df).mark_bar(cornerRadiusTopRight=10, cornerRadiusBottomRight=10, size=18).encode(
        y=alt.Y(cat, type="nominal", sort="-x", axis=alt.Axis(title=None, labelLimit=170)),
        x=alt.X(val, type="quantitative", axis=alt.Axis(title=None)),
        color=alt.Color(cat_col, type="nominal", scale=alt.Scale(domain=list(colors), range=list(colors.values())), legend=alt.Legend(title=None)),
        tooltip=[alt.Tooltip(cat, type="nominal"), alt.Tooltip(val, type="quantitative"), alt.Tooltip(cat_col, type="nominal")])
    return _cfg(bars, h)


def ch_donut(df, cat, val, colors=None, center="", h=270):
    rng = list(colors.values()) if colors else PAL
    dom = list(colors) if colors else None
    sc = alt.Scale(domain=dom, range=rng) if dom else alt.Scale(range=rng)
    arc = alt.Chart(df).mark_arc(innerRadius=62, outerRadius=105, cornerRadius=7, padAngle=0.025).encode(
        theta=alt.Theta(val, type="quantitative", stack=True), color=alt.Color(cat, type="nominal", scale=sc, legend=alt.Legend(title=None, orient="bottom")),
        tooltip=[alt.Tooltip(cat, type="nominal"), alt.Tooltip(val, type="quantitative")])
    mid = alt.Chart(pd.DataFrame({"t": [str(center)]})).mark_text(size=30, font="Baloo Da 2", fontWeight=700, color="#0a1226").encode(text=alt.Text("t", type="nominal"))
    return _cfg(alt.layer(arc, mid), h)


def ch_trend(df, gov, color="#ff7a1a", h=280):
    lo, hi = float(min(df["দাম"].min(), gov)) * 0.96, float(df["দাম"].max()) * 1.04
    y = alt.Y("দাম", type="quantitative", scale=alt.Scale(domain=[lo, hi]), axis=alt.Axis(title=None))
    x = alt.X("তারিখ", type="temporal", axis=alt.Axis(title=None, format="%d %b", labelAngle=0, tickCount=6))
    fill = alt.Gradient(gradient="linear", stops=[alt.GradientStop(color="rgba(255,122,26,0.38)", offset=0), alt.GradientStop(color="rgba(255,122,26,0.02)", offset=1)], x1=1, x2=1, y1=0, y2=1)
    area = alt.Chart(df).mark_area(interpolate="monotone", color=fill).encode(x=x, y=y, y2=alt.value(h))
    line = alt.Chart(df).mark_line(interpolate="monotone", strokeWidth=3.5, color=color).encode(x=x, y=y)
    pts = alt.Chart(df).mark_circle(size=34, color=color).encode(x=x, y=y, tooltip=[alt.Tooltip("তারিখ", type="temporal", format="%d %b"), alt.Tooltip("দাম", type="quantitative")])
    rule = alt.Chart(pd.DataFrame({"y": [gov]})).mark_rule(strokeDash=[7, 5], strokeWidth=2, color="#ef4444").encode(y=alt.Y("y", type="quantitative"))
    return _cfg(alt.layer(area, line, pts, rule), h)


def ch_area(df, cat, val, h=260):
    x = alt.X(cat, type="nominal", sort=None, axis=alt.Axis(title=None, labelAngle=-30))
    y = alt.Y(val, type="quantitative", axis=alt.Axis(title=None))
    fill = alt.Gradient(gradient="linear", stops=[alt.GradientStop(color="rgba(15,181,166,0.45)", offset=0), alt.GradientStop(color="rgba(15,181,166,0.03)", offset=1)], x1=1, x2=1, y1=0, y2=1)
    a = alt.Chart(df).mark_area(interpolate="monotone", color=fill).encode(x=x, y=y)
    l = alt.Chart(df).mark_line(interpolate="monotone", strokeWidth=3.5, color="#0fb5a6", point=alt.OverlayMarkDef(filled=True, fill="#fff", stroke="#0fb5a6", size=70, strokeWidth=2.5)).encode(
        x=x, y=y, tooltip=[alt.Tooltip(cat, type="nominal"), alt.Tooltip(val, type="quantitative")])
    return _cfg(alt.layer(a, l), h)


def scale(val, lo, hi, zones, label):
    stops, prev = [], lo
    for ub, c in zones:
        a = (prev - lo) / (hi - lo) * 100
        b = (min(ub, hi) - lo) / (hi - lo) * 100
        stops.append(f"{c} {a:.1f}% {b:.1f}%")
        prev = ub
    pos = (min(max(val, lo), hi) - lo) / (hi - lo) * 100
    grad = ",".join(stops)
    return f'<div class="scl"><div class="sb" style="background:linear-gradient(90deg,{grad})"></div><div class="mk" style="left:{pos:.1f}%"><b>{label}</b></div></div>'


def stepper(stt):
    steps = ["জমা হয়েছে", "তদন্তাধীন", "নিষ্পত্তি হয়েছে"]
    cur = steps.index(stt) if stt in steps else 0
    parts = []
    for n, s in enumerate(steps):
        cls = "done" if n < cur else "cur" if n == cur else ""
        mark = "✓" if n < cur or (n == cur and n == 2) else bn(n + 1)
        parts.append(f'<div class="st {cls}"><i>{mark}</i>{s}</div>')
    return '<div class="stp">' + "".join(parts) + "</div>"


# ======================================================================
#  ডাটা লোড
# ======================================================================
df_stores, df_map = load_database()
db_ok = df_stores is not None and df_map is not None

# ======================================================================
#  স্প্ল্যাশ (সেশনের প্রথমবার) + সাইডবার
# ======================================================================
if not st.session_state.get("boot"):
    st.session_state["boot"] = True
    st.markdown(SPLASH, unsafe_allow_html=True)
    components.html(boot_html(), height=1)

with st.sidebar:
    st.markdown('<div class="sbb"><div class="sbl">🛰️</div><div><b>মানব সাথি</b><small>আপনার এলাকার দোকান, দাম ও সেবার সঙ্গী</small></div></div>', unsafe_allow_html=True)
    if db_ok:
        st.markdown(
            f'<div class="sbs"><i>🏪</i><div><b>{bn(len(df_stores))}</b><span>নিবন্ধিত দোকান</span></div></div>'
            f'<div class="sbs"><i>📍</i><div><b>{bn(df_stores["এলাকা"].nunique())}</b><span>এলাকা</span></div></div>'
            f'<div class="sbs"><i>📦</i><div><b>{bn(df_map["প্রোডাক্টের নাম"].nunique())}</b><span>পণ্যের ধরন</span></div></div>', unsafe_allow_html=True)
    components.html(MUTE_HTML, height=54)
    st.markdown("---")
    st.markdown('**কীভাবে ব্যবহার করবেন**')
    st.markdown('<div class="how"><b>১</b>এলাকা ও পণ্য বেছে দোকান খুঁজুন<br><b>২</b>ম্যাপে দোকানে চাপ দিয়ে স্টক, ভিড় ও দিকনির্দেশ দেখুন<br><b>৩</b>স্টক নিশ্চিত করতে অনুরোধ পাঠান<br><b>৪</b>দাম বা সেবায় সমস্যা হলে অভিযোগ জানান</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("তৈরি করেছে: কালিয়াগঞ্জ নাজিরতন উচ্চ বিদ্যালয় (SOUNDARJYA)")

# ======================================================================
#  হিরো
# ======================================================================
nd = now_dt()
stats = ""
if db_ok:
    stats = (f'<div class="hst"><div><b>{bn(len(df_stores))}</b><span>দোকান</span></div><div><b>{bn(df_stores["এলাকা"].nunique())}</b><span>এলাকা</span></div>'
             f'<div><b>{bn(df_map["প্রোডাক্টের নাম"].nunique())}</b><span>পণ্য</span></div></div>')
st.markdown(
    f'<div class="hero"><span class="hello">👋 {greet()} · {WEEK[nd.weekday()]}, {bn(nd.day)} {MONTHS[nd.month - 1]} {bn(nd.year)}</span>'
    f'<h1>মানব সাথি</h1><p>স্যাটেলাইট ম্যাপে দোকান খুঁজুন, স্টক ও ভিড় জানুন, ন্যায্য দামে কিনুন।</p>'
    f'<div class="hch"><span>🛰️ স্যাটেলাইট ম্যাপ</span><span>📍 আমার লোকেশন</span><span>📦 লাইভ স্টক</span><span>⚖️ ন্যায্য দাম</span><span>🚨 সরাসরি অভিযোগ</span><span>🏥 স্বাস্থ্য সঙ্গী</span></div>{stats}</div>',
    unsafe_allow_html=True)

T = st.tabs(["🔎 পণ্য খুঁজুন", "🏪 দোকান তালিকা", "📊 বাজার দর", "⭐ রিভিউ", "🚨 অভিযোগ ও হেল্পলাইন", "🏥 স্বাস্থ্য সঙ্গী", "🧾 দোকানদার প্যানেল", "🏛️ সরকারি প্যানেল"])

# ======================================================================
#  ১. পণ্য খুঁজুন
# ======================================================================
with T[0]:
    head("পণ্য খুঁজুন", "এলাকা ও পণ্য বেছে নিন — কাছের দোকান স্যাটেলাইট ম্যাপে দেখুন এবং স্টক যাচাই করুন।", "🔎", "teal")
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

        sig = f"{area}|{product}|{sort_by}"
        if st.session_state.get("s_sig") != sig:
            st.session_state["s_sig"], st.session_state["s_limit"] = sig, 8

        res = in_area[in_area["প্রোডাক্টের নাম"].astype(str).str.strip() == product].copy() if product else pd.DataFrame()
        if res.empty:
            st.warning("এই এলাকায় পণ্যটি বিক্রি করে এমন কোনো দোকান ডাটাবেজে নেই। অন্য এলাকা বা পণ্য বেছে দেখুন।")
        else:
            res = add_geo(res).sort_values("distance_km" if "কাছের" in sort_by else "name")
            reqs = read_json(REQ_F)
            pay = store_payload(res, reqs, product)
            open_n = sum(1 for p in pay if p["open"])
            confirmed = sum(1 for p in pay if p["src"] == "yes")
            near = res.distance_km.min()
            near_t = f"{bn(int(near * 1000))} মিটার" if near < 1 else f"{bn(round(near, 1))} কিমি"
            kpis([("পাওয়া গেছে", f"{bn(len(res))}টি", "দোকান আছে", "🏪", "teal"), ("সবচেয়ে কাছের", near_t, "ম্যাপ কেন্দ্র থেকে", "📏", "indigo"),
                  ("এখন খোলা", f"{bn(open_n)}টি", "বর্তমান সময় অনুযায়ী", "🟢", "amber"), ("স্টক নিশ্চিত", f"{bn(confirmed)}টি", "দোকানদার জানিয়েছেন", "✅", "violet")])
            embed_map(pay, 480, "hybrid", pulse=len(pay) <= 50)
            st.caption("📍 ম্যাপে অনুমতি দিলে আপনার অবস্থান দেখাবে। দোকানের অবস্থান, দূরত্ব, স্টক % ও ভিড় আনুমানিক (ডেমো); দোকানদার নিশ্চিত করলে আসল তথ্য বসে যায়।")

            ctitle("আপনার কাছের দোকান", f"{area} · {product}")
            lim = st.session_state.get("s_limit", 8)
            for n, (idx, row) in enumerate(res.head(lim).iterrows()):
                sid = txt(row.get("দোকান আইডি"))
                p = next((x for x in pay if x["id"] == sid), None) or {}
                d = float(row["distance_km"])
                dist = f"{bn(int(d * 1000))} মিটার" if d < 1 else f"{bn(round(d, 1))} কিমি"
                stock, src = p.get("stock", 50), p.get("src", "demo")
                tone = "green" if stock >= 60 else "amber" if stock >= 30 else "red"
                ac = {"green": "#22c55e", "amber": "#f59e0b", "red": "#ef4444"}[tone]
                crowd = [("কম", 24, "#22c55e"), ("মাঝারি", 58, "#f59e0b"), ("বেশি", 90, "#ef4444")][p.get("crowd", 0)]
                stock_t = "আছে ✓" if src == "yes" else "নেই" if src == "no" else f"{bn(stock)}%"
                q = req_for(reqs, sid, product)
                note = ""
                if q:
                    note = f'<span class="pill">📢 সর্বশেষ স্টক খবর: {esc(q.get("status"))} ({esc(q.get("time"))})</span>'
                elif src == "demo":
                    note = '<span class="pill" style="background:#e8eefc;color:#2a3a78">ℹ️ স্টক ও ভিড় আনুমানিক — নিশ্চিত করতে অনুরোধ পাঠান</span>'
                phone = "".join(ch for ch in txt(row.get("যোগাযোগ নম্বর")) if ch.isdigit() or ch == "+")
                links = f'<a class="g1" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination={row["lat"]:.6f},{row["lon"]:.6f}">🧭 দিকনির্দেশ</a>'
                if phone:
                    links += f'<a class="g2" href="tel:{phone}">📞 কল করুন</a>'
                badge_open = '<span class="op">এখন খোলা</span>' if p.get("open") else '<span class="cl2">এখন বন্ধ</span>'
                st.markdown(
                    f'<div class="scard {tone}" style="--ac:{ac};--d:{(n % 8) * 70}ms"><div class="sc-top"><div class="sc-ico">🏪</div>'
                    f'<div class="sc-t"><h4>{esc(row.get("দোকানের নাম"))}</h4><small>{badge_open} · {html.escape(p.get("hours", ""))} · আইডি {esc(sid)}</small></div>'
                    f'<div class="walk">🚶 {bn(int(d * 12) + 1)} মিনিট</div></div>'
                    f'<div class="sc-ad">📍 {esc(row.get("ঠিকানা"))} · 📏 {dist}</div>'
                    f'<div class="tg"><span>📦 {esc(row.get("প্রোডাক্টের নাম"))} ({esc(row.get("ওজন/সাইজ"))})</span><span>🏷️ {esc(row.get("ব্র্যান্ড"))} · {esc(row.get("কোম্পানি"))}</span><span>📞 {esc(row.get("যোগাযোগ নম্বর"))}</span></div>'
                    f'<div class="mt"><label>স্টক</label><div class="tr"><div class="fl" style="--w:{max(stock, 8)}%;--c:{ac}"></div><b>{stock_t}</b></div></div>'
                    f'<div class="mt"><label>ভিড়</label><div class="tr"><div class="fl" style="--w:{crowd[1]}%;--c:{crowd[2]}"></div><b>{crowd[0]}</b></div></div>'
                    f'{note}<div class="acts">{links}</div></div>', unsafe_allow_html=True)
                if st.button("🔍 স্টক আছে কি না জানতে চাই", key=f"rq_{sid}_{idx}", **STRETCH):
                    if any(is_pending(r) and str(r.get("store_id")).upper() == sid.upper() and r.get("product") == product for r in reqs):
                        st.toast("এই পণ্যের জন্য অনুরোধ আগেই পাঠানো হয়েছে, উত্তরের অপেক্ষা করুন।", icon="⏳")
                    else:
                        reqs.insert(0, {"id": uuid.uuid4().hex[:8], "store_id": sid.upper(), "store_name": txt(row.get("দোকানের নাম")), "product": product,
                                        "time": now(), "status": "মালিকের উত্তরের অপেক্ষায় ⏳", "state": "pending"})
                        write_json(REQ_F, reqs)
                        st.toast("অনুরোধ পাঠানো হয়েছে। দোকানদার উত্তর দিলে এখানে দেখা যাবে।", icon="✅")
            if len(res) > lim:
                if st.button(f"⬇️ আরও দেখান ({bn(len(res) - lim)}টি বাকি)", key="more_s", **STRETCH):
                    st.session_state["s_limit"] = lim + 8
                    st.rerun()

# ======================================================================
#  ২. দোকান তালিকা
# ======================================================================
with T[1]:
    head("দোকান তালিকা", "এলাকা বা নাম দিয়ে খুঁজুন, ম্যাপে ক্লাস্টার দেখুন এবং তালিকা ডাউনলোড করুন।", "🏪", "indigo")
    if not db_ok:
        st.error("দোকানের ডাটাবেজ ফাইল পাওয়া যায়নি।")
    else:
        has_cat = "ক্যাটাগরি" in df_stores.columns
        f1, f2, f3 = st.columns([1.2, 1.2, 2]) if has_cat else (*st.columns([1, 2]), None)
        a = f1.selectbox("এলাকা", ["সব এলাকা"] + sorted(df_stores["এলাকা"].dropna().astype(str).unique()), key="l_area")
        cat_sel = f2.selectbox("ক্যাটাগরি", ["সব ক্যাটাগরি"] + sorted(df_stores["ক্যাটাগরি"].dropna().astype(str).unique()), key="l_cat") if has_cat else "সব ক্যাটাগরি"
        q = (f3 or f2).text_input("দোকানের নাম বা আইডি লিখে খুঁজুন", key="l_q", placeholder="যেমন: S-126")
        view = df_stores if a == "সব এলাকা" else df_stores[df_stores["এলাকা"].astype(str) == a]
        if has_cat and cat_sel != "সব ক্যাটাগরি":
            view = view[view["ক্যাটাগরি"].astype(str) == cat_sel]
        if q.strip():
            mask = view["দোকানের নাম"].astype(str).str.contains(q.strip(), case=False, na=False) | view["দোকান আইডি"].astype(str).str.contains(q.strip(), case=False, na=False)
            view = view[mask]
        if view.empty:
            st.info("কোনো দোকান মেলেনি। অন্য শব্দ দিয়ে চেষ্টা করুন।")
        else:
            gv_df = add_geo(view)
            pay = store_payload(gv_df, [], None)
            kpis([("মোট দোকান", f"{bn(len(view))}টি", "ফিল্টার অনুযায়ী", "🏪", "indigo"), ("এলাকা", f"{bn(view['এলাকা'].nunique())}টি", "এই তালিকায়", "📍", "teal"),
                  ("এখন খোলা", f"{bn(sum(1 for p in pay if p['open']))}টি", "বর্তমান সময়ে", "🟢", "green"), ("ক্যাটাগরি", f"{bn(view['ক্যাটাগরি'].nunique()) if has_cat else '—'}টি", "ধরন", "🗂️", "violet")])
            embed_map(pay, 500, "hybrid", pulse=False)
            ch1, ch2 = st.columns(2)
            with ch1:
                ctitle("এলাকা অনুযায়ী দোকান", "কোন এলাকায় কতগুলো")
                ad = view.groupby(view["এলাকা"].astype(str)).size().reset_index(name="সংখ্যা").rename(columns={"এলাকা": "এলাকা"})
                draw(lambda: ch_hbar(ad.sort_values("সংখ্যা", ascending=False).head(10), "এলাকা", "সংখ্যা", "#4f46e5", "#22a6f2", h=max(180, 34 * min(len(ad), 10))))
            with ch2:
                if has_cat:
                    ctitle("ক্যাটাগরি ভাগ", "দোকানের ধরন")
                    cd = view.groupby(view["ক্যাটাগরি"].astype(str)).size().reset_index(name="সংখ্যা")
                    draw(lambda: ch_donut(cd, "ক্যাটাগরি", "সংখ্যা", center=bn(len(view))))
            st.markdown(f"**{bn(len(view))}টি দোকান পাওয়া গেছে**")
            cols = [c for c in ["দোকান আইডি", "দোকানের নাম", "এলাকা", "ঠিকানা", "যোগাযোগ নম্বর", "ক্যাটাগরি"] if c in view.columns]
            table(view[cols])
            st.download_button("⬇️ তালিকা ডাউনলোড (CSV)", view[cols].to_csv(index=False).encode("utf-8-sig"), "dokan_talika.csv", "text/csv")

# ======================================================================
#  ৩. বাজার দর
# ======================================================================
PRICES = [("নাজিরশাইল চাল", "কেজি", 70, 72, 5, "🍚"), ("সয়াবিন তেল", "লিটার", 175, 175, 2, "🛢️"), ("মসুর ডাল", "কেজি", 140, 145, 2, "🥣"),
          ("চিনি", "কেজি", 135, 140, 1, "🍬"), ("আটা/ময়দা", "কেজি", 60, 60, 2, "🌾"), ("আলু", "কেজি", 45, 50, 3, "🥔"),
          ("পেঁয়াজ", "কেজি", 85, 90, 2, "🧅"), ("ডিম", "হালি", 48, 50, 2, "🥚"), ("লবণ", "কেজি", 40, 40, 1, "🧂"), ("তরল দুধ", "লিটার", 85, 85, 1, "🥛")]


def price_status(gov, mkt):
    if mkt <= gov:
        return "✅ ন্যায্য মূল্য"
    return "⚠️ সামান্য বেশি" if (mkt - gov) / gov <= 0.05 else "🚨 অতিরিক্ত মূল্য"


with T[2]:
    head("বাজার দর ও খরচ হিসাব", "সরকার নির্ধারিত দামের সাথে খুচরা বাজারের দাম মিলিয়ে দেখুন। (দামগুলো নমুনা; হালনাগাদ রাখুন)", "📊", "amber")
    rows = [{"পণ্য": n, "একক": u, "সরকারি": g, "বাজার": m, "পার্থক্য": m - g, "শতাংশ": round((m - g) / g * 100, 1), "অবস্থা": price_status(g, m), "আইকন": ic} for n, u, g, m, _, ic in PRICES]
    dfp = pd.DataFrame(rows)
    over = int((dfp["পার্থক্য"] > 0).sum())
    avg_over = dfp.loc[dfp["পার্থক্য"] > 0, "শতাংশ"].mean() if over else 0.0
    worst = dfp.sort_values("শতাংশ", ascending=False).iloc[0]
    kpis([("ন্যায্য দামে আছে", f"{bn(len(dfp) - over)}টি", "পণ্য", "✅", "green"), ("বেশি দামে", f"{bn(over)}টি", "পণ্য", "⚠️", "red"),
          ("গড় বাড়তি", f"{bn(round(avg_over, 1))}%", "বেশি দামের পণ্যে", "📈", "amber"), ("সবচেয়ে বেশি", worst["পণ্য"].split("/")[0], f"সরকারি দরের চেয়ে +{bn(worst['শতাংশ'])}%", "🔥", "rose")])

    tiles = []
    for n, r in enumerate(rows):
        cls = "green" if r["পার্থক্য"] <= 0 else "amber" if r["শতাংশ"] <= 5 else "red"
        bc = {"green": "green", "amber": "amber", "red": "red"}[cls]
        tiles.append(f'<div class="pt {cls}" style="--d:{n * 60}ms"><div class="pe">{r["আইকন"]}</div><div class="pn">{r["পণ্য"]}</div><div class="pu">প্রতি {r["একক"]}</div>'
                     f'<div class="pp">{bn(r["বাজার"])}৳</div><div class="pg">সরকারি {bn(r["সরকারি"])}৳</div><span class="badge {bc}">{r["অবস্থা"]}</span></div>')
    st.markdown('<div class="ptg">' + "".join(tiles) + "</div>", unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        ctitle("সরকারি বনাম বাজার দর", "প্রতিটি পণ্যের তুলনা (৳)")
        mdf = dfp.melt(id_vars=["পণ্য"], value_vars=["সরকারি", "বাজার"], var_name="ধরন", value_name="দাম")
        draw(lambda: ch_grouped(mdf, "পণ্য", "ধরন", "দাম", {"সরকারি": "#4f46e5", "বাজার": "#ffb020"}, 300))
    with g2:
        ctitle("কতটা বেশি নেওয়া হচ্ছে?", "সরকারি দরের তুলনায় শতাংশ")
        sdf = dfp[["পণ্য", "শতাংশ", "অবস্থা"]].copy()
        sdf["অবস্থা"] = sdf["অবস্থা"].str.replace(r"^\S+\s", "", regex=True)
        draw(lambda: ch_status(sdf, "পণ্য", "শতাংশ", "অবস্থা", {"ন্যায্য মূল্য": "#22c55e", "সামান্য বেশি": "#ffb020", "অতিরিক্ত মূল্য": "#ff5d5d"}, 300))

    ctitle("৩০ দিনের দামের গতি", "নমুনা প্রবণতা (ডেমো ডেটা) — লাল রেখা সরকারি দর")
    pick = st.selectbox("পণ্য বেছে নিন", [r["পণ্য"] for r in rows], key="trend_p", label_visibility="collapsed")
    pr = next(r for r in rows if r["পণ্য"] == pick)
    rng = np.random.default_rng(zlib.crc32(pick.encode()))
    walk = np.cumsum(rng.normal(0, pr["বাজার"] * 0.008, 30))
    series = pr["বাজার"] + (walk - walk[-1])
    tdf = pd.DataFrame({"তারিখ": pd.date_range(end=pd.Timestamp(now_dt().date()), periods=30), "দাম": np.round(series, 1)})
    draw(lambda: ch_trend(tdf, pr["সরকারি"]))

    st.markdown("### 🧮 মাসিক বাজার খরচ ক্যালকুলেটর")
    cols = st.columns(5)
    qty = [cols[i % 5].number_input(f"{p[5]} {p[0]} ({p[1]})", 0, 100, p[4], key=f"q{i}") for i, p in enumerate(PRICES)]
    total = sum(q * p[3] for q, p in zip(qty, PRICES))
    gov_total = sum(q * p[2] for q, p in zip(qty, PRICES))
    kpis([("বাজার দরে মোট", f"{bn(f'{total:,}')} ৳", "আপনার মাসিক খরচ", "🛒", "indigo"), ("সরকারি দরে মোট", f"{bn(f'{gov_total:,}')} ৳", "ন্যায্য হিসাবে", "🏛️", "teal"),
          ("বাড়তি খরচ", f"{bn(f'{total - gov_total:,}')} ৳", "প্রতি মাসে", "💸", "red"), ("বাড়তি হার", f"{bn(round((total - gov_total) / gov_total * 100, 1)) if gov_total else '০'}%", "সরকারি দরের তুলনায়", "📈", "amber")])
    if total > 0:
        cdf = pd.DataFrame({"পণ্য": [p[0] for p in PRICES], "খরচ": [q * p[3] for q, p in zip(qty, PRICES)]})
        cdf = cdf[cdf["খরচ"] > 0]
        d1, d2 = st.columns(2)
        with d1:
            ctitle("খরচের ভাগ", "কোন পণ্যে কত খরচ")
            draw(lambda: ch_donut(cdf, "পণ্য", "খরচ", center=f"{total:,}৳"))
        with d2:
            ctitle("পণ্য অনুযায়ী খরচ", "বাজার দরে (৳)")
            draw(lambda: ch_hbar(cdf, "পণ্য", "খরচ", "#ffb020", "#ff5c9a", h=max(220, 32 * len(cdf))))

# ======================================================================
#  ৪. রিভিউ
# ======================================================================
with T[3]:
    head("দোকান রিভিউ", "আপনার অভিজ্ঞতা জানান, অন্যরা ভালো দোকান চিনতে পারবে।", "⭐", "rose")
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
            rdf = pd.DataFrame(revs)
            rdf["stars"] = rdf["stars"].astype(int)
            avg_all = rdf["stars"].mean()
            five = int((rdf["stars"] == 5).sum())
            kpis([("মোট রিভিউ", bn(len(rdf)), "এ পর্যন্ত", "💬", "rose"), ("গড় রেটিং", f"{bn(round(avg_all, 1))} ★", "সব দোকান মিলিয়ে", "⭐", "amber"), ("৫ স্টার", f"{bn(round(five / len(rdf) * 100))}%", "মোট রিভিউয়ের", "🏆", "violet")])
        else:
            st.info("এখনো কোনো রিভিউ নেই। প্রথম রিভিউ আপনিই দিন।")
    if revs:
        e1, e2 = st.columns(2)
        with e1:
            ctitle("রেটিং বণ্টন", "কোন স্টারে কতজন")
            dist = rdf["stars"].value_counts().reindex([5, 4, 3, 2, 1], fill_value=0).reset_index()
            dist.columns = ["স্টার", "সংখ্যা"]
            dist["স্টার"] = dist["স্টার"].apply(lambda s: f"{bn(s)} ★")
            order = [f"{bn(s)} ★" for s in [5, 4, 3, 2, 1]]
            draw(lambda: ch_hbar(dist, "স্টার", "সংখ্যা", "#ffb020", "#ff5c9a", h=230, sort=order))
        with e2:
            ctitle("সর্বোচ্চ রেটিং পাওয়া দোকান", "গড় রেটিং")
            top = rdf.groupby("shop")["stars"].mean().round(1).sort_values(ascending=False).head(6).reset_index()
            top.columns = ["দোকান", "গড় রেটিং"]
            top["দোকান"] = top["দোকান"].str.slice(0, 26)
            draw(lambda: ch_hbar(top, "দোকান", "গড় রেটিং", "#8b5cf6", "#ff5c9a", h=230))
    AV = ["linear-gradient(135deg,#ff5c9a,#ff8a5c)", "linear-gradient(135deg,#4f46e5,#22a6f2)", "linear-gradient(135deg,#0fb5a6,#22c55e)", "linear-gradient(135deg,#8b5cf6,#c026d3)", "linear-gradient(135deg,#ffb020,#ff7a1a)"]
    for n, r in enumerate(revs[:8]):
        s = max(1, min(5, int(r.get("stars", 5))))
        nm = str(r.get("shop", "")).split("—")[-1].strip() or "?"
        st.markdown(
            f'<div class="card rose" style="--d:{n * 60}ms"><div style="display:flex;align-items:center;gap:.75rem"><div style="flex:none;width:44px;height:44px;border-radius:15px;display:grid;place-items:center;color:#fff;font-weight:700;font-size:1.2rem;background:{AV[n % 5]}">{html.escape(nm[:1])}</div>'
            f'<div style="flex:1"><h4 style="margin:0">{esc(r.get("shop"))}</h4><span style="color:#ffb020;letter-spacing:2px">{"★" * s}</span><span style="color:#d7dcea;letter-spacing:2px">{"★" * (5 - s)}</span></div>'
            f'<small style="color:#5d6b86">{esc(r.get("time"))}</small></div><p style="margin-top:.5rem">{esc(r.get("comment") or "মন্তব্য নেই")}</p></div>', unsafe_allow_html=True)

# ======================================================================
#  ৫. অভিযোগ ও হেল্পলাইন
# ======================================================================
with T[4]:
    head("অভিযোগ ও হেল্পলাইন", "বেশি দাম, ওজনে কম বা ভেজাল পণ্যের অভিযোগ সরাসরি সরকারি প্যানেলে পাঠান।", "🚨", "red")
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
                    st.success(f"অভিযোগ জমা হয়েছে। আপনার অভিযোগ নম্বর: {cid} — এটি সংরক্ষণ করুন, নিচে অবস্থা ট্র্যাক করতে পারবেন।")
        ctitle("🔎 অভিযোগের অবস্থা ট্র্যাক করুন", "অভিযোগ নম্বর দিন (যেমন: C-1A2B3C)")
        tid = st.text_input("অভিযোগ নম্বর", key="trk", label_visibility="collapsed", placeholder="C-XXXXXX").strip().upper()
        if tid:
            hit = next((c for c in read_json(COMP_F) if str(c.get("id", "")).upper() == tid), None)
            if hit:
                st.markdown(card(f"📄 {esc(hit.get('shop'))}", [f"🏙️ {esc(hit.get('area'))} · {esc(hit.get('kind'))}", f"🕒 জমার সময়: {esc(hit.get('time'))}"], badge=esc(hit.get("status")), badge_cls="blue", tone="indigo",
                                 extra=stepper(hit.get("status"))), unsafe_allow_html=True)
            else:
                st.warning("এই নম্বরে কোনো অভিযোগ পাওয়া যায়নি। নম্বরটি আবার মিলিয়ে দেখুন।")
    with cr:
        HELP = [("ভোক্তা অধিকার অধিদপ্তর", "১৬১২১", "16121", "বেশি দাম বা প্রতারণার অভিযোগ", "red"), ("জাতীয় জরুরি সেবা", "৯৯৯", "999", "পুলিশ, ফায়ার সার্ভিস, অ্যাম্বুলেন্স", "amber"),
                ("স্বাস্থ্য বাতায়ন", "১৬২৬৩", "16263", "স্বাস্থ্য পরামর্শ", "green"), ("দুর্নীতি দমন কমিশন", "১০৬", "106", "দুর্নীতির অভিযোগ", "blue"),
                ("নারী ও শিশু নির্যাতন প্রতিরোধ", "১০৯", "109", "২৪ ঘণ্টা সহায়তা", "rose"), ("জাতীয় আইনগত সহায়তা", "১৬৪৩০", "16430", "বিনামূল্যে আইনি পরামর্শ", "violet"),
                ("জাতীয় তথ্য সেবা", "৩৩৩", "333", "সরকারি সেবার তথ্য", "teal")]
        for n, (nm, num, raw, d, tone) in enumerate(HELP):
            st.markdown(card(f"📞 {nm}", [d], badge=f'<a href="tel:{raw}" style="color:inherit;text-decoration:none">{num} ☎</a>', tone=tone, i=n), unsafe_allow_html=True)
    ctitle("কীভাবে অভিযোগ করবেন?", "প্রমাণ ঠিকঠাক রাখলে নিষ্পত্তি দ্রুত হয়")
    tips = [("🧾", "রশিদ রাখুন", "কেনার ক্যাশ মেমো বা রশিদ সংরক্ষণ করুন।", "teal"), ("📸", "ছবি তুলুন", "দামের তালিকা, পণ্যের মেয়াদ ও ওজনের ছবি তুলে রাখুন।", "indigo"),
            ("⚖️", "ওজন যাচাই", "সন্দেহ হলে অন্য দোকানের নির্ভরযোগ্য দাঁড়িপাল্লায় মেপে দেখুন।", "amber"), ("📝", "সময় ও স্থান লিখুন", "ঘটনার তারিখ, সময় ও দোকানের ঠিকানা স্পষ্ট লিখুন।", "rose")]
    tc = st.columns(4)
    for n, (ic, t, d, tone) in enumerate(tips):
        tc[n].markdown(card(f"{ic} {t}", [d], tone=tone, i=n), unsafe_allow_html=True)

# ======================================================================
#  ৬. স্বাস্থ্য
# ======================================================================
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
DAILY = ["💧 আজ পর্যাপ্ত পানি পান করুন — সারা দিনে অন্তত ৮ গ্লাস।", "🚶 আজ অন্তত ৩০ মিনিট হাঁটুন।", "🧂 খাবারে লবণ কম রাখুন, কাঁচা লবণ এড়িয়ে চলুন।",
         "😴 রাতে ৭–৮ ঘণ্টা ঘুমের চেষ্টা করুন।", "🥗 প্লেটে আজ কয়েক রঙের শাকসবজি রাখুন।", "🧼 খাওয়ার আগে ও পরে সাবান দিয়ে হাত ধুয়ে নিন।", "🧘 কিছুক্ষণ মোবাইল থেকে বিরতি নিয়ে গভীর শ্বাস নিন।"]
TONES = ["green", "teal", "blue", "violet", "amber", "rose", "indigo"]

with T[5]:
    head("স্বাস্থ্য সঙ্গী", "BMI ও রক্তচাপ যাচাই করুন এবং সাধারণ সমস্যায় ঘরোয়া পরামর্শ দেখুন।", "🏥", "green")
    st.markdown(card("আজকের স্বাস্থ্য টিপ", [DAILY[nd.weekday()]], tone="green", badge=WEEK[nd.weekday()], badge_cls="green"), unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("#### ⚖️ BMI")
        w = st.number_input("ওজন (কেজি)", 10.0, 200.0, 60.0, 0.5, key="bw")
        h = st.number_input("উচ্চতা (সেমি)", 50.0, 250.0, 160.0, 0.5, key="bh")
        bmi = w / ((h / 100) ** 2)
        cat, ico = ("কম ওজন", "🟡") if bmi < 18.5 else ("স্বাভাবিক", "🟢") if bmi < 25 else ("বেশি ওজন", "🟠") if bmi < 30 else ("স্থূলতা", "🔴")
        bmi_t = bn(f"{bmi:.1f}")
        st.metric("আপনার BMI", bmi_t, f"{ico} {cat}", delta_color="off")
        st.markdown(scale(bmi, 10, 40, [(18.5, "#fbbf24"), (25, "#22c55e"), (30, "#fb923c"), (40, "#ef4444")], bmi_t) + '<div class="sl"><span>কম</span><span>স্বাভাবিক</span><span>বেশি</span><span>স্থূল</span></div>', unsafe_allow_html=True)
        lo_w, hi_w = 18.5 * (h / 100) ** 2, 24.9 * (h / 100) ** 2
        water = w * 0.033
        st.markdown(card("📌 আপনার জন্য সাধারণ হিসাব", [f"স্বাভাবিক ওজনের পরিসর: <b>{bn(f'{lo_w:.1f}')}–{bn(f'{hi_w:.1f}')} কেজি</b>", f"দৈনিক পানির সাধারণ চাহিদা: প্রায় <b>{bn(f'{water:.1f}')} লিটার</b> (আবহাওয়া ও কাজ অনুযায়ী ভিন্ন হয়)"], tone="teal"), unsafe_allow_html=True)
    with b2:
        st.markdown("#### 🩺 রক্তচাপ")
        s = st.number_input("সিস্টোলিক", 60, 250, 120, key="bs")
        d = st.number_input("ডায়াস্টোলিক", 40, 150, 80, key="bd")
        if s >= 180 or d >= 120:
            msg, fn = "অতি উচ্চ — এখনই চিকিৎসকের কাছে যান", st.error
        elif s >= 140 or d >= 90:
            msg, fn = "উচ্চ রক্তচাপ — চিকিৎসকের পরামর্শ নিন", st.warning
        elif s >= 130 or d >= 80:
            msg, fn = "স্বাভাবিকের চেয়ে কিছুটা বেশি", st.warning
        elif s < 90 or d < 60:
            msg, fn = "রক্তচাপ কম — লক্ষণ থাকলে ডাক্তার দেখান", st.warning
        else:
            msg, fn = "স্বাভাবিক রক্তচাপ ✅", st.success
        st.metric("রক্তচাপ", f"{bn(s)}/{bn(d)}")
        st.markdown(scale(s, 80, 200, [(90, "#60a5fa"), (120, "#22c55e"), (130, "#fbbf24"), (140, "#fb923c"), (200, "#ef4444")], bn(s)) + '<div class="sl"><span>কম</span><span>স্বাভাবিক</span><span>বেশি</span><span>উচ্চ</span></div>', unsafe_allow_html=True)
        fn(msg)
        st.markdown(card("🚑 এই লক্ষণে ঘরোয়া উপায় নয়, দ্রুত চিকিৎসা নিন", ["বুকে চাপ বা ব্যথা, শ্বাসকষ্ট", "হঠাৎ দুর্বলতা, মুখ বেঁকে যাওয়া বা কথা জড়িয়ে যাওয়া", "অজ্ঞান হয়ে যাওয়া বা তীব্র রক্তপাত", "৩ দিনের বেশি উচ্চ জ্বর", "জরুরি সহায়তা: <b>৯৯৯</b>"], tone="red"), unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🌿 ঘরোয়া ও ভেষজ পরামর্শ")
    st.warning("এগুলো সাধারণ তথ্য, চিকিৎসার বিকল্প নয়। গর্ভাবস্থা, শিশু বা দীর্ঘমেয়াদি রোগে এবং লক্ষণ গুরুতর হলে ডাক্তারের পরামর্শ নিন।")
    hq = st.text_input("সমস্যার নাম লিখে খুঁজুন", key="hq", placeholder="যেমন: গ্যাস্ট্রিক")
    shown = [x for x in HERBS if hq.strip() in x[0] or hq.strip() in x[1]]
    hc = st.columns(2)
    for i, (dis, herb, how) in enumerate(shown):
        hc[i % 2].markdown(card(dis, [f"🌿 <b>উপাদান:</b> {herb}", f"💡 {how}"], tone=TONES[i % 7], i=i), unsafe_allow_html=True)
    if not shown:
        st.info("এই নামে কোনো সমস্যা পাওয়া যায়নি।")

# ======================================================================
#  ৭. দোকানদার প্যানেল
# ======================================================================
with T[6]:
    head("দোকানদার প্যানেল", "দোকান আইডি দিয়ে প্রবেশ করে ক্রেতাদের স্টক অনুরোধের উত্তর দিন।", "🧾", "violet")
    sid = st.text_input("দোকান আইডি", placeholder="যেমন: S-126", key="own_id").strip().upper()
    if sid:
        info = None
        if df_stores is not None:
            mt = df_stores[df_stores["দোকান আইডি"].astype(str).str.strip().str.upper() == sid]
            info = mt.iloc[0] if len(mt) else None
        if info is None:
            st.error(f"'{sid}' আইডি পাওয়া যায়নি। 'দোকান তালিকা' ট্যাব থেকে সঠিক আইডি দেখে নিন।")
        else:
            st.markdown(card(f"✅ স্বাগতম, {esc(info['দোকানের নাম'])}", [f"📍 {esc(info['এলাকা'])} · {esc(info['ঠিকানা'])}", f"📂 {esc(info.get('ক্যাটাগরি'))} · 📞 {esc(info.get('যোগাযোগ নম্বর'))}"], badge=esc(sid), tone="violet"), unsafe_allow_html=True)
            allr = read_json(REQ_F)
            mine = [(i, r) for i, r in enumerate(allr) if str(r.get("store_id", "")).upper() == sid]
            pend = [(i, r) for i, r in mine if is_pending(r)]
            done = [(i, r) for i, r in mine if not is_pending(r)]
            rate = round(len(done) / len(mine) * 100) if mine else 0
            kpis([("উত্তরের অপেক্ষায়", bn(len(pend)), "নতুন অনুরোধ", "⏳", "amber"), ("উত্তর দেওয়া হয়েছে", bn(len(done)), "এ পর্যন্ত", "✅", "green"),
                  ("মোট অনুরোধ", bn(len(mine)), "ক্রেতাদের কাছ থেকে", "📨", "indigo"), ("উত্তরের হার", f"{bn(rate)}%", "দ্রুত উত্তর = বেশি আস্থা", "⚡", "violet")])
            if not pend:
                st.info("📭 এই মুহূর্তে কোনো নতুন স্টক অনুরোধ নেই।")
            for i, r in pend:
                st.markdown(card(f"📦 {esc(r.get('product'))}", [f"⏱️ {esc(r.get('time'))}"], badge="নতুন", badge_cls="amber", tone="amber"), unsafe_allow_html=True)
                y, n = st.columns(2)
                for col, state, label, text in [(y, "yes", "🟢 স্টক আছে", "স্টক আছে ✅"), (n, "no", "🔴 স্টক নেই", "স্টক নেই ❌")]:
                    if col.button(label, key=f"{state}_{sid}_{i}", **STRETCH):
                        allr[i].update({"status": text, "state": state, "answered": now()})
                        write_json(REQ_F, allr)
                        st.rerun()
            if done:
                with st.expander(f"🕘 উত্তর দেওয়া অনুরোধ ({bn(len(done))}টি)"):
                    for i, r in done[:10]:
                        st.markdown(card(f"📦 {esc(r.get('product'))}", [f"{esc(r.get('status'))} · {esc(r.get('answered') or r.get('time'))}"], tone="green" if req_state(r) == "yes" else "red"), unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("#### 📈 বাজার বিশ্লেষণ")
            st.caption("নমুনা তথ্য — নিজের হিসাব অনুযায়ী হালনাগাদ করুন।")
            an = pd.DataFrame([("নাজিরশাইল চাল", 65, 72, 92, "বাড়ছে ↗️"), ("সয়াবিন তেল", 168, 175, 85, "স্থির ➡️"), ("মসুর ডাল", 135, 145, 78, "বাড়ছে ↗️"),
                               ("চিনি", 130, 140, 70, "স্থির ➡️"), ("পেঁয়াজ", 80, 90, 95, "দ্রুত বাড়ছে ⬆️"), ("আলু", 42, 50, 88, "কমছে ↘️")],
                              columns=["পণ্য", "পাইকারি (৳)", "খুচরা (৳)", "চাহিদা (১০০ এর মধ্যে)", "মূল্য প্রবণতা"])
            an["লাভের হার (%)"] = ((an["খুচরা (৳)"] - an["পাইকারি (৳)"]) / an["পাইকারি (৳)"] * 100).round(1)
            hot = an.sort_values("চাহিদা (১০০ এর মধ্যে)", ascending=False).iloc[0]
            best = an.sort_values("লাভের হার (%)", ascending=False).iloc[0]
            kpis([("সবচেয়ে চাহিদা", hot["পণ্য"], f"সূচক {bn(hot['চাহিদা (১০০ এর মধ্যে)'])}/১০০", "🔥", "rose"), ("সর্বোচ্চ লাভের হার", f"{bn(best['লাভের হার (%)'])}%", best["পণ্য"], "💹", "green"),
                  ("গড় লাভের হার", f"{bn(round(an['লাভের হার (%)'].mean(), 1))}%", "৬টি পণ্যে", "📊", "indigo")])
            g1, g2 = st.columns(2)
            with g1:
                ctitle("পাইকারি বনাম খুচরা দাম", "৳ প্রতি একক")
                m2 = an.melt(id_vars=["পণ্য"], value_vars=["পাইকারি (৳)", "খুচরা (৳)"], var_name="ধরন", value_name="দাম")
                m2["ধরন"] = m2["ধরন"].str.replace(" (৳)", "", regex=False)
                draw(lambda: ch_grouped(m2, "পণ্য", "ধরন", "দাম", {"পাইকারি": "#22a6f2", "খুচরা": "#ffb020"}, 280))
            with g2:
                ctitle("চাহিদা সূচক", "১০০ এর মধ্যে")
                dd = an[["পণ্য", "চাহিদা (১০০ এর মধ্যে)"]].rename(columns={"চাহিদা (১০০ এর মধ্যে)": "চাহিদা"})
                draw(lambda: ch_area(dd, "পণ্য", "চাহিদা", 280))
            ctitle("লাভের হার (%)", "পণ্য অনুযায়ী")
            pf = an[["পণ্য", "লাভের হার (%)"]].rename(columns={"লাভের হার (%)": "লাভ"})
            draw(lambda: ch_hbar(pf, "পণ্য", "লাভ", "#8b5cf6", "#ff5c9a", h=230))
            table(an)

# ======================================================================
#  ৮. সরকারি প্যানেল
# ======================================================================
with T[7]:
    head("সরকারি কর্মকর্তা প্যানেল", "অভিযোগ দেখুন, অবস্থা হালনাগাদ করুন এবং তথ্য ডাউনলোড করুন।", "🏛️", "navy")
    if st.session_state.get("admin_ok"):
        if st.button("🔓 লগআউট"):
            st.session_state.admin_ok = False
            st.rerun()
        if DEFAULT_PASS:
            st.warning("⚠️ ডিফল্ট পাসওয়ার্ড ব্যবহার হচ্ছে। `st.secrets` বা পরিবেশ চলকে `ADMIN_PASSWORD` সেট করুন।")
        cs = read_json(COMP_F)
        STAT = ["জমা হয়েছে", "তদন্তাধীন", "নিষ্পত্তি হয়েছে"]
        n_new, n_inv, n_done = (sum(c.get("status", "জমা হয়েছে") == s for c in cs) for s in STAT)
        kpis([("মোট অভিযোগ", bn(len(cs)), "এ পর্যন্ত", "📚", "navy"), ("নতুন", bn(n_new), "পদক্ষেপ দরকার", "🆕", "red"), ("তদন্তাধীন", bn(n_inv), "চলমান", "🔍", "amber"), ("নিষ্পত্তি", bn(n_done), f"{bn(round(n_done / len(cs) * 100)) if cs else '০'}% সম্পন্ন", "✅", "green")])
        if not cs:
            st.info("📭 এখনো কোনো অভিযোগ জমা হয়নি।")
        else:
            cdf = pd.DataFrame(cs)
            cdf["status"] = cdf["status"].fillna("জমা হয়েছে")
            a1, a2, a3 = st.columns(3)
            with a1:
                ctitle("অবস্থা", "অভিযোগের বর্তমান ধাপ")
                sd = cdf.groupby("status").size().reset_index(name="সংখ্যা").rename(columns={"status": "অবস্থা"})
                draw(lambda: ch_donut(sd, "অবস্থা", "সংখ্যা", {"জমা হয়েছে": "#ff5d5d", "তদন্তাধীন": "#ffb020", "নিষ্পত্তি হয়েছে": "#22c55e"}, center=bn(len(cs)), h=280))
            with a2:
                ctitle("অভিযোগের ধরন", "কোন সমস্যা বেশি")
                kd = cdf.groupby("kind").size().reset_index(name="সংখ্যা").rename(columns={"kind": "ধরন"})
                draw(lambda: ch_hbar(kd, "ধরন", "সংখ্যা", "#ff5d5d", "#ff8a5c", h=280))
            with a3:
                ctitle("এলাকা অনুযায়ী", "কোথায় বেশি")
                ar = cdf.groupby("area").size().reset_index(name="সংখ্যা").rename(columns={"area": "এলাকা"})
                draw(lambda: ch_hbar(ar, "এলাকা", "সংখ্যা", "#14206b", "#06b6d4", h=280))
            flt = st.multiselect("অবস্থা অনুযায়ী ফিল্টার", STAT, default=STAT)
            st.download_button("⬇️ সব অভিযোগ (CSV)", cdf.to_csv(index=False).encode("utf-8-sig"), "abhijog.csv", "text/csv")
            for i, c in enumerate(cs):
                stt = c.get("status", "জমা হয়েছে")
                if stt not in flt:
                    continue
                tone = {"জমা হয়েছে": "red", "তদন্তাধীন": "amber", "নিষ্পত্তি হয়েছে": "green"}.get(stt, "red")
                st.markdown(card(f"🚨 {esc(c.get('shop'))}", [f"🏙️ {esc(c.get('area'))} · {esc(c.get('kind', 'অন্যান্য'))}", f"📝 {esc(c.get('details'))}", f"<small>নম্বর: {esc(c.get('id', '—'))} · {esc(c.get('time'))}</small>"],
                                 badge=esc(stt), badge_cls=tone, tone=tone, i=min(i, 6)), unsafe_allow_html=True)
                with st.expander("অবস্থা পরিবর্তন করুন"):
                    new = st.selectbox("নতুন অবস্থা", STAT, index=STAT.index(stt) if stt in STAT else 0, key=f"st_{i}")
                    if st.button("সংরক্ষণ করুন", key=f"sv_{i}"):
                        cs[i]["status"] = new
                        write_json(COMP_F, cs)
                        st.rerun()
    else:
        st.markdown(card("🔐 শুধু অনুমোদিত কর্মকর্তা", ["অভিযোগ দেখতে ও অবস্থা হালনাগাদ করতে পাসওয়ার্ড দিন।"], tone="indigo"), unsafe_allow_html=True)
        pw = st.text_input("অফিসার পাসওয়ার্ড", type="password", key="adm_pw")
        if pw:
            if hmac.compare_digest(pw.encode("utf-8"), ADMIN_PASS.encode("utf-8")):
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("পাসওয়ার্ড সঠিক নয়। আবার চেষ্টা করুন।")

st.markdown('<div class="foot">🛰️ <b>মানব সাথি ৩.০</b> · কালিয়াগঞ্জ নাজিরতন উচ্চ বিদ্যালয় (SOUNDARJYA)</div>', unsafe_allow_html=True)
