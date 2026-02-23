import streamlit as st
import pandas as pd
from database import init_db, get_all_destinations, add_destination, get_connection
import os
from dotenv import load_dotenv

# Initialize basic UI config
st.set_page_config(page_title="Flight Price Tracker", page_icon="✈️", layout="wide")
init_db()

st.title("✈️ Flight Price Tracker Dashboard")
st.markdown("Monitor flight prices and get notified via Telegram when they drop below your target threshold.")

st.sidebar.header("Add New Destination")

with st.sidebar.form("add_destination_form"):
    st.write("Enter IATA Airport Codes (e.g., LON, JFK, DXB)")
    col1, col2 = st.columns(2)
    with col1:
        dep_code = st.text_input("From (Code)", max_chars=3).upper()
    with col2:
        dest_code = st.text_input("To (Code)", max_chars=3).upper()
        
    target_price = st.number_input("Target Price Alert ($)", min_value=1.0, value=500.0, step=10.0)
    
    st.write("Optional Date Constraints (leave blank for flexible dates)")
    date_from = st.date_input("Earliest Departure", value=None)
    date_to = st.date_input("Latest Departure", value=None)
    
    submitted = st.form_submit_button("Start Tracking")
    
    if submitted:
        if dep_code and dest_code:
            d_from_str = date_from.strftime("%d/%m/%Y") if date_from else None
            d_to_str = date_to.strftime("%d/%m/%Y") if date_to else None
            
            add_destination(dep_code, dest_code, target_price, d_from_str, d_to_str)
            st.success(f"Now tracking {dep_code} ➡️ {dest_code} below ${target_price}")
            st.rerun() # Refresh table
        else:
            st.error("Please provide both Departure and Destination codes.")

# Main area: Table of current tracked destinations
st.subheader("Currently Tracked Flights")
destinations = get_all_destinations()

if destinations:
    # Convert to Pandas DataFrame for a nice Streamlit table
    df = pd.DataFrame(destinations)
    # Reorder/rename columns for display
    display_df = df.rename(columns={
        "departure_city_code": "From",
        "destination_city_code": "To",
        "target_price": "Target Price ($)",
        "lowest_price_seen": "Lowest Historical ($)",
        "date_from": "Earliest Date",
        "date_to": "Latest Date"
    })
    
    display_cols = ["From", "To", "Target Price ($)", "Lowest Historical ($)", "Earliest Date", "Latest Date"]
    
    st.dataframe(display_df[display_cols], use_container_width=True, hide_index=True)
    
    # Simple form to delete a row if needed
    st.write("---")
    with st.expander("Delete Tracked Flight"):
        id_to_delete = st.selectbox("Select tracking ID to remove", df['id'].tolist(), format_func=lambda x: f"{df[df['id']==x]['departure_city_code'].values[0]} to {df[df['id']==x]['destination_city_code'].values[0]}")
        if st.button("Delete Strategy"):
             conn = get_connection()
             c = conn.cursor()
             c.execute('DELETE FROM destinations WHERE id = ?', (id_to_delete,))
             conn.commit()
             conn.close()
             st.success("Deleted successfully.")
             st.rerun()
else:
    st.info("You aren't tracking any flights yet. Add one securely using the sidebar!")

# API Configuration check
st.write("---")
st.subheader("System Status")
load_dotenv()
if not os.environ.get("AMADEUS_API_KEY") or os.environ.get("AMADEUS_API_KEY") == "your_amadeus_api_key_here":
    st.error("❌ Amadeus API Key is missing! Check your `.env` file.")
else:
    st.success("✅ Amadeus API Key loaded.")

if not os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN") == "your_telegram_bot_token_here":
    st.error("❌ Telegram Bot Token is missing! Check your `.env` file.")
else:
     st.success("✅ Telegram Notifier enabled.")

st.caption("Note: Run `python main.py` in a separate terminal process to keep the background checking active.")
