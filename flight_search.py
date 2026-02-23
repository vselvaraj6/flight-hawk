import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

AMADEUS_API_KEY = os.environ.get("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.environ.get("AMADEUS_API_SECRET")

def get_amadeus_token():
    """
    Fetches the OAuth2 token required for Amadeus API calls.
    """
    if not AMADEUS_API_KEY or AMADEUS_API_KEY == "your_amadeus_api_key_here":
        return None
        
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Amadeus token: {e}")
        return None

def check_flights(origin_city_code, destination_city_code, from_time=None, to_time=None):
    """
    Queries the Amadeus Flight Offers Search API for the cheapest flight between two cities.
    Returns the price, departure date, airline, and booking link, or None if no flight found.
    """
    token = get_amadeus_token()
    if not token:
        print("Error: Missing or invalid Amadeus credentials in .env file")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    
    # Amadeus requires exact dates. If none provided, let's search for tomorrow
    import datetime as dt
    if not from_time:
        tomorrow = dt.datetime.now() + dt.timedelta(days=1)
        from_time = tomorrow.strftime("%Y-%m-%d")
    else:
        # Convert DD/MM/YYYY from our DB to YYYY-MM-DD for Amadeus
        try:
             parsed_date = dt.datetime.strptime(from_time, "%d/%m/%Y")
             from_time = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
             pass

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    query = {
        "originLocationCode": origin_city_code,
        "destinationLocationCode": destination_city_code,
        "departureDate": from_time,
        "adults": 1,
        "max": 1, # Get only the cheapest option
        "currencyCode": "USD"
    }
    
    # Note: Amadeus Free Tier doesn't do deep links natively like Kiwi, 
    # so we will construct a generic Google Flights deep link for the user
    google_flights_link = f"https://www.google.com/flights?hl=en#flt={origin_city_code}.{destination_city_code}.{from_time}"

    try:
        response = requests.get(
            url=url,
            headers=headers,
            params=query,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if len(data.get('data', [])) == 0:
             return None
                 
        flight_data = data["data"][0]
        
        # Extract pricing
        price = float(flight_data["price"]["total"])
        
        # Extract airport codes
        itineraries = flight_data.get("itineraries", [])
        if not itineraries:
            return None
            
        segments = itineraries[0].get("segments", [])
        if not segments:
            return None
            
        outbound_departure = segments[0]
        outbound_arrival = segments[-1]
        
        dep_iata = outbound_departure["departure"]["iataCode"]
        arr_iata = outbound_arrival["arrival"]["iataCode"]
        dep_date_raw = outbound_departure["departure"]["at"]
        dep_date = dep_date_raw.split("T")[0]
        
        return {
            "price": price,
            "departure_city_name": origin_city_code, # Amadeus uses codes primarily
            "departure_airport_iata_code": dep_iata,
            "arrival_city_name": destination_city_code,
            "arrival_airport_iata_code": arr_iata,
            "outbound_date": dep_date,
            "inbound_date": None, # Kept None for 1-way simplicity on Amadeus
            "deep_link": google_flights_link
        }
    except requests.exceptions.RequestException as e:
        print(f"Error querying Amadeus API: {e}")
        return None

if __name__ == "__main__":
    # Test block
    print("Testing flight search from LON to PAR (Requires a valid .env key)")
    res = check_flights("LON", "PAR")
    if res:
        print(f"Found cheapest flight: ${res['price']}")
        print(res)
    else:
        print("No flights found or API key not configured yet.")
