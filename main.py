import time
import schedule
import logging
from datetime import datetime
from database import init_db, get_all_destinations, update_lowest_price
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
        
        # Check if we should notify the user
        # We notify IF:
        # 1. Price is at or below target price
        # AND
        # 2. We haven't seen this price or lower before (to avoid spamming)
        
        if current_price <= target_price:
            if lowest_seen is None or current_price < lowest_seen:
                # We have a NEW lowest price that meets the threshold!
                
                msg = f"📉 <b>FLIGHT PRICE DROP ALERT!</b> 📉\n\n"
                msg += f"<b>{flight['departure_city_name']} ({flight['departure_airport_iata_code']}) ➡️ {flight['arrival_city_name']} ({flight['arrival_airport_iata_code']})</b>\n\n"
                msg += f"🔥 <b>New Price: ${current_price}</b>\n"
                msg += f"🎯 Your Target: ${target_price}\n\n"
                msg += f"🛫 Outbound: {flight['outbound_date']}\n"
                if flight['inbound_date']:
                    msg += f"🛬 Inbound:  {flight['inbound_date']}\n\n"
                else:
                    msg += "\n"
                msg += f"<a href='{flight['deep_link']}'>✈️ Book on Google Flights</a>"
                
                logging.info(f"  >>> Sending notification for new low price: ${current_price}")
                
                success = send_telegram_message(msg)
                if success:
                    # Update database so we don't alert again unless it drops further
                    update_lowest_price(dest['id'], current_price)
            else:
                logging.info(f"  Price meets target, but we've already notified about a price this low or lower (${lowest_seen}).")
        else:
             logging.info("  Price is above target threshold.")

def start_scheduler():
    # Run once immediately on startup
    init_db()
    job()
    
    # Schedule to run every 12 hours
    schedule.every(12).hours.do(job)
    
    logging.info("Scheduler activated. Listening for drops (Checking every 12 hours)...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()
