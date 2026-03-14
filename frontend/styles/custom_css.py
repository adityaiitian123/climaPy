import streamlit as st

def apply_global_styles():
    """Injects ultra-premium CSS — animated grid, glassmorphism, neon glow, sci-fi command center."""
    st.markdown("""
        <style>
        /* ─────────────────────────────────────────────────────────
           FONT IMPORT
        ───────────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;600;700&display=swap');

        /* ─────────────────────────────────────────────────────────
           ROOT & BODY — Animated cyber-grid background
        ───────────────────────────────────────────────────────── */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', sans-serif;
            background-color: #020617 !important;
            color: #e2e8f0;
        }

        /* Animated Hex-Grid & Scanline overlay */
        .stApp::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: 
                linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03)),
                radial-gradient(circle at 25% 35%, rgba(56,189,248,0.08) 0%, transparent 55%);
            background-size: 100% 4px, 3px 100%, 100% 100%;
            pointer-events: none;
            z-index: 100;
            opacity: 0.15;
            animation: scanline 10s linear infinite;
        }

        /* Mission Control Hex Grid */
        .stApp::after {
            content: '';
            position: fixed;
            inset: 0;
            background-image: radial-gradient(rgba(56, 189, 248, 0.15) 1px, transparent 1px);
            background-size: 30px 30px;
            opacity: 0.3;
            pointer-events: none;
            z-index: 0;
        }

        @keyframes scanline {
            0% { background-position: 0 0; }
            100% { background-position: 0 100%; }
        }

        /* ─────────────────────────────────────────────────────────
           SIDEBAR — Premium dark glass
        ───────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0f1e 0%, #060b18 100%) !important;
            border-right: 1px solid rgba(56,189,248,0.12) !important;
            box-shadow: 4px 0 30px rgba(0,0,0,0.5);
        }

        [data-testid="stSidebarNav"] { background-color: transparent !important; }

        /* Sidebar header accent */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            letter-spacing: 0.04em;
        }

        /* ─────────────────────────────────────────────────────────
           TYPOGRAPHY
        ───────────────────────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #38bdf8 !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em;
        }

        h1 {
            font-size: 2.8rem !important;
            background: linear-gradient(100deg, #38bdf8 0%, #818cf8 55%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        p, label, span, div {
            font-family: 'Inter', sans-serif;
        }

        /* ─────────────────────────────────────────────────────────
           APP HEADER BANNER
        ───────────────────────────────────────────────────────── */
        .app-header {
            background: linear-gradient(135deg, rgba(56,189,248,0.07) 0%, rgba(129,140,248,0.07) 100%);
            border: 1px solid rgba(56,189,248,0.18);
            border-radius: 16px;
            padding: 2rem 2.5rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }

        .app-header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, #38bdf8, #818cf8, transparent);
        }

        .app-header::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg, transparent, rgba(56,189,248,0.3), transparent);
        }

        .app-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(100deg, #38bdf8 0%, #818cf8 55%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.04em;
            line-height: 1;
            margin-bottom: 0.3rem;
        }

        .app-tagline {
            font-size: 1rem;
            color: #64748b;
            font-weight: 400;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .app-badge {
            display: inline-block;
            background: rgba(56,189,248,0.12);
            border: 1px solid rgba(56,189,248,0.3);
            border-radius: 20px;
            padding: 0.25rem 0.9rem;
            font-size: 0.75rem;
            font-weight: 600;
            color: #38bdf8;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-right: 0.5rem;
        }

        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            margin-right: 6px;
            box-shadow: 0 0 8px #10b981;
            animation: pulse-dot 2s infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.3); }
        }

        /* ─────────────────────────────────────────────────────────
           HEADER & CARD GLOW — High-end Rotating Border
        ───────────────────────────────────────────────────────── */
        @keyframes rotate-bg {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
        }

        .glass-card, .app-header {
            position: relative;
            background: rgba(10, 15, 30, 0.9) !important;
            border: 1px solid rgba(56, 189, 248, 0.1) !important;
            border-radius: 16px;
            overflow: hidden !important; /* Clip the rotating light to the edges */
        }

        /* The rotating light trail behind the card/header */
        .glass-card::before, .app-header::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 150%;
            height: 400%; /* Very tall to ensure it covers even wide headers */
            background: conic-gradient(
                from 0deg,
                transparent 15%,
                #38bdf8 25%,
                transparent 35%,
                transparent 65%,
                #818cf8 75%,
                transparent 85%
            );
            animation: rotate-bg 6s linear infinite;
            z-index: -2;
            opacity: 0.4;
            filter: blur(15px);
        }

        /* Inner overlay to give the glass feel and keep text readable */
        .glass-card::after, .app-header::after {
            content: '';
            position: absolute;
            inset: 2px;
            background: rgba(10, 15, 30, 0.95);
            border-radius: 14px;
            z-index: -1;
        }

        .app-header {
            padding: 1.8rem 2.5rem;
            margin-bottom: 2.2rem;
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.4), 0 0 15px rgba(56, 189, 248, 0.05);
        }

        /* Rotating Border hover speedup */
        .glass-card:hover::before {
            animation-duration: 3s;
            opacity: 0.7;
        }

        /* API Badge & Logo Pulse */
        .app-title {
            animation: logo-pulse 4s infinite ease-in-out;
        }

        @keyframes logo-pulse {
            0%, 100% { filter: drop-shadow(0 0 2px rgba(56, 189, 248, 0.3)); }
            50% { filter: drop-shadow(0 0 12px rgba(56, 189, 248, 0.6)); transform: scale(1.01); }
        }

        /* ─────────────────────────────────────────────────────────
           KPI CARDS — Neon metric blocks
        ───────────────────────────────────────────────────────── */

        /* ─────────────────────────────────────────────────────────
           KPI CARDS — Neon metric blocks
        ───────────────────────────────────────────────────────── */
        .kpi-card {
            background: linear-gradient(145deg, rgba(15,23,42,0.9), rgba(10,15,30,0.95));
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.06);
            padding: 1.4rem 1.6rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px -8px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.04);
            transition: all 0.3s ease;
        }

        .kpi-card::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0; height: 2px;
            border-radius: 0 0 14px 14px;
        }

        .kpi-card.cyan::after  { background: linear-gradient(90deg, transparent, #38bdf8, transparent); }
        .kpi-card.red::after   { background: linear-gradient(90deg, transparent, #ef4444, transparent); }
        .kpi-card.amber::after { background: linear-gradient(90deg, transparent, #f59e0b, transparent); }
        .kpi-card.blue::after  { background: linear-gradient(90deg, transparent, #3b82f6, transparent); }

        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: rgba(56,189,248,0.15);
        }

        .kpi-label {
            font-size: 0.72rem;
            font-weight: 600;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.6rem;
        }

        .kpi-number {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.4rem;
            font-weight: 700;
            color: #f1f5f9;
            line-height: 1;
            margin-bottom: 0.4rem;
        }

        .kpi-number .kpi-unit {
            font-size: 1rem;
            font-weight: 400;
            color: #475569;
        }

        .kpi-delta {
            font-size: 0.82rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .kpi-delta.pos { color: #10b981; }
        .kpi-delta.neg { color: #ef4444; }
        .kpi-delta.neu { color: #64748b; }

        /* ─────────────────────────────────────────────────────────
           INSIGHT PANEL — Glowing info block
        ───────────────────────────────────────────────────────── */
        .insight-panel {
            background: linear-gradient(135deg,
                rgba(6,182,212,0.08) 0%,
                rgba(8,145,178,0.04) 50%,
                rgba(15,23,42,0.9) 100%);
            border: 1px solid rgba(6,182,212,0.2);
            border-left: 3px solid #06b6d4;
            padding: 1.3rem 1.6rem;
            border-radius: 12px;
            margin: 1.2rem 0;
            font-size: 1rem;
            line-height: 1.7;
            color: #cbd5e1;
            position: relative;
            box-shadow: 0 0 30px -10px rgba(6,182,212,0.15), inset 0 1px 0 rgba(255,255,255,0.03);
        }

        .insight-panel strong {
            color: #06b6d4;
            font-weight: 600;
        }

        /* ─────────────────────────────────────────────────────────
           SIDEBAR CONTROLS
        ───────────────────────────────────────────────────────── */
        .sidebar-section-header {
            font-size: 0.7rem;
            font-weight: 700;
            color: #38bdf8;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            padding: 0.5rem 0 0.3rem;
            border-bottom: 1px solid rgba(56,189,248,0.12);
            margin-bottom: 0.8rem;
        }

        /* Selectbox & Slider styling */
        [data-testid="stSelectbox"] > div > div {
            background: rgba(15,23,42,0.8) !important;
            border: 1px solid rgba(56,189,248,0.15) !important;
            border-radius: 8px !important;
            color: #e2e8f0 !important;
        }

        [data-testid="stSelectbox"] > div > div:hover {
            border-color: rgba(56,189,248,0.4) !important;
        }

        .stSlider > div {
            padding-top: 0.5rem;
        }

        /* ─────────────────────────────────────────────────────────
           TABS — Neon underline tabs
        ───────────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: rgba(10,15,30,0.5) !important;
            border-radius: 10px;
            padding: 0.3rem;
            border: 1px solid rgba(255,255,255,0.05);
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px;
            background: transparent !important;
            border-radius: 8px;
            color: #64748b !important;
            font-weight: 600;
            font-size: 0.88rem;
            padding: 8px 18px;
            border: none !important;
            transition: all 0.2s ease;
            letter-spacing: 0.01em;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #94a3b8 !important;
            background: rgba(255,255,255,0.03) !important;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(56,189,248,0.1) !important;
            color: #38bdf8 !important;
            box-shadow: 0 0 12px rgba(56,189,248,0.15);
        }

        .stTabs [data-baseweb="tab-highlight"] {
            background: #38bdf8 !important;
            height: 2px;
        }

        /* ─────────────────────────────────────────────────────────
           SECTION HEADERS inside pages
        ───────────────────────────────────────────────────────── */
        .section-tag {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 0.5rem;
        }

        .section-tag .tag-line {
            display: inline-block;
            width: 28px;
            height: 3px;
            border-radius: 2px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
        }

        /* ─────────────────────────────────────────────────────────
           EXPANDER
        ───────────────────────────────────────────────────────── */
        [data-testid="stExpander"] {
            border: 1px solid rgba(255,255,255,0.07) !important;
            border-radius: 10px !important;
            background: rgba(15,23,42,0.6) !important;
        }

        /* ─────────────────────────────────────────────────────────
           SCROLLBAR — Thin styled
        ───────────────────────────────────────────────────────── */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #0a0f1e; }
        ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

        /* ─────────────────────────────────────────────────────────
           PLOTLY OVERLAY CLEANUP
        ───────────────────────────────────────────────────────── */
        .js-plotly-plot .plotly {
            border-radius: 12px;
            overflow: hidden;
        }

        /* ─────────────────────────────────────────────────────────
           INTELLIGENCE HUD & OVERLAYS
        ───────────────────────────────────────────────────────── */
        .intel-hud {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 8px;
            padding: 12px;
            z-index: 1000;
            pointer-events: none;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }

        .glass-card {
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255,255,255,0.05);
            animation: slideUpFade 0.8s ease-out forwards;
        }
        .glass-card:hover {
            border: 1px solid rgba(56, 189, 248, 0.5);
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.2);
            transform: translateY(-5px) scale(1.01);
            background: rgba(15, 23, 42, 0.55);
        }

        @keyframes slideUpFade {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .neon-text {
            color: #38bdf8;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }
        .vibrant-tag {
            background: linear-gradient(90deg, #f59e0b, #ef4444, #8b5cf6, #3b82f6);
            background-size: 300% 100%;
            animation: gradient-shift 5s infinite linear;
        }
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            100% { background-position: 100% 50%; }
        }

        .hud-item {
            margin-bottom: 8px;
        }

        .hud-item:last-child {
            margin-bottom: 0;
        }

        .hud-label {
            font-size: 0.65rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: block;
        }

        .hud-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.9rem;
            color: #38bdf8;
            font-weight: 600;
        }

        .scanline-effect {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.01), rgba(0, 255, 0, 0.005), rgba(0, 0, 255, 0.01));
            background-size: 100% 2px, 2px 100%;
            pointer-events: none;
            opacity: 0.3;
            z-index: 5;
        }

        /* ─────────────────────────────────────────────────────────
           FOOTER
        ───────────────────────────────────────────────────────── */
        .footer {
            text-align: center;
            font-size: 0.75rem;
            color: #1e293b;
            margin-top: 4rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255,255,255,0.04);
            letter-spacing: 0.04em;
        }

        .footer span {
            color: #38bdf8;
            font-weight: 600;
        }

        /* ─────────────────────────────────────────────────────────
           RISK BADGE — color-coded climate risk pill
        ───────────────────────────────────────────────────────── */
        .risk-badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* ─────────────────────────────────────────────────────────
           DELTA HEADLINE — giant glowing change indicator
        ───────────────────────────────────────────────────────── */
        .delta-headline {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3.5rem;
            font-weight: 900;
            letter-spacing: -0.03em;
            line-height: 1;
        }

        /* ─────────────────────────────────────────────────────────
           ANOMALY ALERT — pulsing warning banner
        ───────────────────────────────────────────────────────── */
        .anomaly-alert {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-left: 3px solid #ef4444;
            border-radius: 8px;
            padding: 0.7rem 1rem;
            color: #fca5a5;
            font-size: 0.85rem;
            animation: pulse-alert 2.5s infinite;
        }

        @keyframes pulse-alert {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
            50% { box-shadow: 0 0 20px 4px rgba(239,68,68,0.2); }
        }

        /* ─────────────────────────────────────────────────────────
           FORECAST BAND — subtle purple shading for ML zone
        ───────────────────────────────────────────────────────── */
        .forecast-zone {
            background: rgba(168,85,247,0.08);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 0.72rem;
            color: #a855f7;
            border: 1px solid rgba(168,85,247,0.2);
            display: inline-block;
        }

        /* ─────────────────────────────────────────────────────────
           STORY TOUR STEP INDICATOR
        ───────────────────────────────────────────────────────── */
        .tour-step-active {
            background: #38bdf8;
            box-shadow: 0 0 8px rgba(56,189,248,0.6);
        }

        .tour-step-done {
            background: rgba(56,189,248,0.3);
        }

        .tour-step-upcoming {
            background: #1e293b;
            border: 1px solid #334155;
        }

        /* ─────────────────────────────────────────────────────────
           DID YOU KNOW CARD
        ───────────────────────────────────────────────────────── */
        .fact-card {
            border-radius: 8px;
            padding: 0.9rem 1rem;
            font-size: 0.85rem;
            line-height: 1.55;
            margin-top: 0.8rem;
        }

        </style>
    """, unsafe_allow_html=True)

