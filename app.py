import streamlit as st
import pandas as pd
from database import init_db, get_all_destinations, add_destination, get_connection, get_setting, set_setting
import os
from dotenv import load_dotenv

load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="Flight Price Tracker", page_icon="✈️", layout="wide")
init_db()

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global overrides */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Main headings */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }
    h1 { color: #ffffff !important; }
    h2 { color: #e0e0ff !important; }
    h3 { color: #c0c0ff !important; }

    /* Text */
    p, span, label, .stMarkdown {
        color: #d0d0e8 !important;
    }

    /* Glass card styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0 4px 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9ca3af !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* Form submit button */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #e0e0ff !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #e0e0ff !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a3e 0%, #0f0c29 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 10px !important;
        color: #c0c0ff !important;
    }

    /* Success/error/info messages */
    .stSuccess { border-radius: 10px !important; }
    .stError { border-radius: 10px !important; }
    .stInfo { border-radius: 10px !important; }

    /* Divider */
    hr { border-color: rgba(255, 255, 255, 0.08) !important; }

    /* Login specific styles */
    .login-container {
        max-width: 420px;
        margin: 80px auto;
        text-align: center;
    }
    .login-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .login-subtitle {
        color: #9ca3af !important;
        font-size: 1rem;
        margin-bottom: 40px;
    }
    .otp-input input {
        font-size: 1.8rem !important;
        text-align: center !important;
        letter-spacing: 12px !important;
        font-weight: 700 !important;
    }

    /* Status dots */
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    .status-dot.green { background: #34d399; }
    .status-dot.red { background: #f87171; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


def show_dashboard():
    """Renders the main dashboard after authentication."""

    # --- Header ---
    st.markdown("""
        <h1 style="margin-bottom: 0;">✈️ Flight Price Tracker</h1>
        <p style="font-size: 1.05rem; color: #9ca3af !important; margin-top: 4px;">
            Monitor prices & get notified via Telegram when they drop
        </p>
    """, unsafe_allow_html=True)

    st.write("")

    # --- Metrics Row ---
    destinations = get_all_destinations()
    total_tracked = len(destinations)
    prices = [d['lowest_price_seen'] for d in destinations if d['lowest_price_seen'] is not None]
    lowest_overall = f"${min(prices):,.0f}" if prices else "—"
    freq_minutes = int(get_setting('check_frequency_minutes') or 60)
    freq_display = f"{freq_minutes}min" if freq_minutes < 60 else f"{freq_minutes // 60}hr"

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Routes Tracked</div>
                <div class="metric-value">{total_tracked}</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Best Price Found</div>
                <div class="metric-value">{lowest_overall}</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Check Frequency</div>
                <div class="metric-value">{freq_display}</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # --- Sidebar: Add Destination ---
    with st.sidebar:
        st.markdown("""
            <h2 style="margin-bottom: 4px;">➕ Add Route</h2>
            <p style="font-size: 0.85rem; color: #9ca3af !important;">Enter IATA codes (e.g. YYZ, DEL, JFK)</p>
        """, unsafe_allow_html=True)

        with st.form("add_destination_form"):
            col1, col2 = st.columns(2)
            with col1:
                dep_code = st.text_input("From", max_chars=3, placeholder="YYZ").upper()
            with col2:
                dest_code = st.text_input("To", max_chars=3, placeholder="DEL").upper()

            target_price = st.number_input("Target Price ($)", min_value=1.0, value=500.0, step=10.0)

            st.markdown("<p style='font-size: 0.8rem; color: #9ca3af !important; margin-top: 12px;'>Date Range (optional)</p>", unsafe_allow_html=True)
            date_from = st.date_input("Earliest", value=None)
            date_to = st.date_input("Latest", value=None)

            submitted = st.form_submit_button("🛫 Start Tracking")

            if submitted:
                if dep_code and dest_code:
                    d_from_str = date_from.strftime("%d/%m/%Y") if date_from else None
                    d_to_str = date_to.strftime("%d/%m/%Y") if date_to else None
                    add_destination(dep_code, dest_code, target_price, d_from_str, d_to_str)
                    st.success(f"Tracking {dep_code} ➡️ {dest_code} below ${target_price}")
                    st.rerun()
                else:
                    st.error("Please provide both codes.")

        st.write("---")

        # --- Sidebar: Settings ---
        st.markdown("<h2>⚙️ Settings</h2>", unsafe_allow_html=True)

        frequency_options = {
            "Every 15 minutes": 15,
            "Every 30 minutes": 30,
            "Every 1 hour": 60,
            "Every 2 hours": 120,
            "Every 4 hours": 240,
            "Every 12 hours": 720
        }

        current_freq = int(get_setting('check_frequency_minutes') or 60)
        current_label = next((k for k, v in frequency_options.items() if v == current_freq), "Every 1 hour")

        selected_freq = st.selectbox(
            "Check Frequency",
            options=list(frequency_options.keys()),
            index=list(frequency_options.keys()).index(current_label)
        )

        if frequency_options[selected_freq] != current_freq:
            set_setting('check_frequency_minutes', frequency_options[selected_freq])
            st.success(f"✅ Updated to {selected_freq}")
            st.rerun()

    # --- Main: Tracked Flights ---
    st.markdown("<h2>📋 Tracked Flights</h2>", unsafe_allow_html=True)

    if destinations:
        df = pd.DataFrame(destinations)
        display_df = df.rename(columns={
            "departure_city_code": "From",
            "destination_city_code": "To",
            "target_price": "Target ($)",
            "lowest_price_seen": "Lowest ($)",
            "date_from": "Earliest",
            "date_to": "Latest"
        })

        display_cols = ["From", "To", "Target ($)", "Lowest ($)", "Earliest", "Latest"]
        st.dataframe(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Target ($)": st.column_config.NumberColumn(format="$%.0f"),
                "Lowest ($)": st.column_config.NumberColumn(format="$%.0f"),
            }
        )

        with st.expander("🗑️ Remove a tracked flight"):
            id_to_delete = st.selectbox(
                "Select route to remove",
                df['id'].tolist(),
                format_func=lambda x: f"{df[df['id']==x]['departure_city_code'].values[0]} → {df[df['id']==x]['destination_city_code'].values[0]}"
            )
            if st.button("Delete Route"):
                conn = get_connection()
                c = conn.cursor()
                c.execute('DELETE FROM destinations WHERE id = ?', (id_to_delete,))
                conn.commit()
                conn.close()
                st.success("Deleted!")
                st.rerun()
    else:
        st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 48px;">
                <div style="font-size: 3rem; margin-bottom: 12px;">🌍</div>
                <h3 style="color: #e0e0ff !important;">No flights tracked yet</h3>
                <p style="color: #9ca3af !important;">Add a route using the sidebar to get started</p>
            </div>
        """, unsafe_allow_html=True)

    # --- System Status ---
    st.write("")
    st.markdown("<h2>📡 System Status</h2>", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        has_amadeus = os.environ.get("AMADEUS_API_KEY") and os.environ.get("AMADEUS_API_KEY") != "your_amadeus_api_key_here"
        if has_amadeus:
            st.markdown('<p><span class="status-dot green"></span> Amadeus API connected</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p><span class="status-dot red"></span> Amadeus API key missing</p>', unsafe_allow_html=True)
    with s2:
        has_telegram = os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_BOT_TOKEN") != "your_telegram_bot_token_here"
        if has_telegram:
            st.markdown('<p><span class="status-dot green"></span> Telegram notifications active</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p><span class="status-dot red"></span> Telegram bot token missing</p>', unsafe_allow_html=True)

    st.caption("Run `python main.py` in a separate terminal to keep the background price checker active.")


# ============================================================
# MAIN ENTRY POINT
# ============================================================
show_dashboard()
