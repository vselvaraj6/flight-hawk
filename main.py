import time
import logging
from database import init_db, get_all_destinations, update_lowest_price, get_setting
from flight_search import check_flights
from notifier import send_telegram_message

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("flight_tracker.log"),
        logging.StreamHandler()
    ]
)

def job():
    logging.info("Running flight price check...")
    
    destinations = get_all_destinations()
    
    if not destinations:
        logging.info("No destinations configured yet.")
        return
        
    for dest in destinations:
        logging.info(f"Checking flights: {dest['departure_city_code']} -> {dest['destination_city_code']}")
        
        # Adding a small delay to avoid hitting rate limits
        time.sleep(2)
        
        flight = check_flights(
            origin_city_code=dest['departure_city_code'],
            destination_city_code=dest['destination_city_code'],
            from_time=dest['date_from'],
            to_time=dest['date_to']
        )
        
        if flight is None:
            logging.info(f"  No flights found for {dest['destination_city_code']}.")
            continue
            
        current_price = flight['price']
        target_price = dest['target_price']
        lowest_seen = dest['lowest_price_seen']
        
        logging.info(f"  Current Price: ${current_price} | Target: ${target_price} | Lowest Seen: {f'${lowest_seen}' if lowest_seen else 'N/A'}")
        
        # Always update the lowest price seen for dashboard visibility
        if lowest_seen is None or current_price < lowest_seen:
            update_lowest_price(dest['id'], current_price)
            logging.info(f"  Updated lowest price seen to ${current_price}")
        
        # Build and send notification every check
        if current_price <= target_price:
            # Price is at or below target — highlight it!
            msg = f"📉 <b>FLIGHT PRICE DROP ALERT!</b> 📉\n\n"
            msg += f"<b>{flight['departure_city_name']} ({flight['departure_airport_iata_code']}) ➡️ {flight['arrival_city_name']} ({flight['arrival_airport_iata_code']})</b>\n\n"
            msg += f"🔥 <b>Current Price: ${current_price}</b>\n"
            msg += f"🎯 Your Target: ${target_price}\n"
            msg += f"📊 Lowest Seen: {f'${lowest_seen}' if lowest_seen else 'N/A'}\n\n"
            msg += f"🛫 Outbound: {flight['outbound_date']}\n"
            if flight['inbound_date']:
                msg += f"🛬 Inbound:  {flight['inbound_date']}\n\n"
            else:
                msg += "\n"
            msg += f"<a href='{flight['deep_link']}'>✈️ Book on Google Flights</a>"
        else:
            # Price is above target — send a regular update
            msg = f"✈️ <b>Hourly Price Update</b>\n\n"
            msg += f"<b>{flight['departure_city_name']} ({flight['departure_airport_iata_code']}) ➡️ {flight['arrival_city_name']} ({flight['arrival_airport_iata_code']})</b>\n\n"
            msg += f"💰 <b>Current Price: ${current_price}</b>\n"
            msg += f"🎯 Your Target: ${target_price}\n"
            msg += f"📊 Lowest Seen: {f'${lowest_seen}' if lowest_seen else 'N/A'}\n\n"
            msg += f"🛫 Outbound: {flight['outbound_date']}\n"
            if flight['inbound_date']:
                msg += f"🛬 Inbound:  {flight['inbound_date']}\n\n"
            else:
                msg += "\n"
            msg += f"<a href='{flight['deep_link']}'>✈️ Book on Google Flights</a>"
        
        logging.info(f"  Sending hourly price notification: ${current_price}")
        send_telegram_message(msg)

def start_scheduler():
    # Run once immediately on startup
    init_db()
    job()
    
    logging.info("Scheduler activated. Frequency is read dynamically from the database.")
    try:
        last_run = time.time()
        while True:
            # Read frequency from database on every loop so dashboard changes take effect live
            freq_minutes = int(get_setting('check_frequency_minutes') or 60)
            elapsed = time.time() - last_run
            
            if elapsed >= freq_minutes * 60:
                logging.info(f"Running scheduled check (frequency: every {freq_minutes} minutes)...")
                job()
                last_run = time.time()
            
            time.sleep(30)  # Check every 30 seconds if it's time to run
    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()
