import requests
import time
import json
import os

titan = "%5B%7B\"i\":96%7D%5D"
ibp = "%5B%7B\"i\":88%7D%5D"
ranges = [[0,0.15],[0.15,0.20],[0.20,0.25],[0.25,0.30],[0.30,0.35],[0.35,0.40],[0.40,0.55],[0.55,1]]
def fetch_current_listings(api_key, sticker):
    """Fetches the current listings from the CSFloat API."""
    url = "https://csfloat.com/api/v1/listings?limit=50"  # This endpoint might not require an API key, double check the docs
    headers = {
        "Authorization": api_key,  # Include the API key in the headers
    }
    listings = []
    try:
        for range in ranges:
                request=url+"&min_float=" + str(range[0]) + "&max_float=" + str(range[1]) + "&stickers=" + sticker
                response = requests.get(request, headers=headers)
                response.raise_for_status()
                for entry in response.json()['data']:
                    listings.append(entry)
                print(f"Response entry count for {sticker} with float ranges {range[0]}-{range[1]}: {len(response.json()['data'])}")
        return listings
    except requests.exceptions.RequestException as e:
        print(f"Error fetching listings: {e}")
        return None

def find_new_listings(previous_listings, current_listings, sticker_name):
    """Compares current listings with previous ones and checks for a specific sticker."""
    new_listings_with_sticker = []
    if current_listings is None:
        return new_listings_with_sticker

    previous_ids = set()
    if previous_listings:
        previous_ids = {listing['id'] for listing in previous_listings}

    for listing in current_listings:
        #has_sticker = any(sticker_name in sticker['name'] for sticker in listing['item']['stickers'])
        if listing['id'] not in previous_ids:
            new_listings_with_sticker.append(listing)
    return new_listings_with_sticker

def load_previous_data(filename="previous_listings.json"):
    """Loads previous listings data from a JSON file."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filename}. Starting with empty data.")
            return {"titan": None, "ibuypower": None}
    return {"titan": None, "ibuypower": None}

def print_new_listings(new_titan_listings, sticker):
    print(f"\n--- New Listings with '{sticker}' Found! ---")
    for listing in new_titan_listings:
        print(f"Item: {listing['item']['market_hash_name']}")
        print(f"Price: $({listing['price']/100})")
        if 'float_value' in listing['item']:
            print(f"Float Value: {listing['item']['float_value']}")
        print(f"Listing ID: {listing['id']}")
        #if 'sticker' in listing['item']:
        print("Stickers:" + sticker)
            #for sticker in listing['item']['stickers']:
             #   print(f"- {sticker['name']}")
        print("-" * 30)

def save_current_data(data, filename):
    """Saves the current listings data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    poll_interval = 6 * 60 * 60
    data_filename_titan = "previous_listings_titan.json"
    data_filename_ibp = "previous_listings_ibp.json"
    #sticker_data = load_previous_data(data_filename)
    titan_data = load_previous_data(data_filename_titan)
    ibp_data = load_previous_data(data_filename_ibp)
    titan_sticker_name = 'Titan (Foil) | Katowice 2014'
    ibuypower_sticker_name = 'iBUYPOWER (Foil) | Katowice 2014'

    #  Get the API key from an environment variable.  This is the most secure way to handle it.
    api_key = os.environ.get("CSFLOAT_API_KEY")
    if not api_key:
        raise ValueError(
            "CSFloat API key not found.  Please set the CSFLOAT_API_KEY environment variable."
        )

    print(f"Starting to monitor for new CSFloat listings with '{titan_sticker_name}'...")
    print(f"Also monitoring for new CSFloat listings with '{ibuypower_sticker_name}'...")


    previous_titan_listings = titan_data.get("titan")
    previous_ibuypower_listings = ibp_data.get("ibuypower")

    current_listings_data_titan = fetch_current_listings(api_key, titan)  # Pass the API key
    new_titan_listings = None
    new_ibuypower_listings = None
    if current_listings_data_titan:
        # Check for new Titan (Foil) listings
        new_titan_listings = find_new_listings(
            previous_titan_listings, current_listings_data_titan, titan_sticker_name
        )

        if new_titan_listings:
            print_new_listings(new_titan_listings, "titan")
    else:
        print(f"Failed to retrieve listings.")
    current_listings_data_ibp = fetch_current_listings(api_key, ibp)  # Pass the API key
        # Check for new iBUYPOWER (Foil) listings
    if current_listings_data_ibp:
        new_ibuypower_listings = find_new_listings(
            previous_ibuypower_listings, current_listings_data_ibp, ibuypower_sticker_name
        )
            
        if new_ibuypower_listings:
            print_new_listings(new_ibuypower_listings, "ibp")
    else:
        print(f"Failed to retrieve listings.")
    # Save the current data for the next run
    if new_titan_listings:
        save_current_data(
            {"titan": current_listings_data_titan},
            data_filename_titan,
        )
    if new_ibuypower_listings:
        save_current_data(
            {"ibuypower": current_listings_data_ibp},
            data_filename_ibp,
        )
    
