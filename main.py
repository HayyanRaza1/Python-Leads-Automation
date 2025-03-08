import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import time
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
SHEET_ID = os.getenv("SHEET_ID")

# Google Places API URL
PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

def get_restaurants(query, next_page_token=None):
    """Fetches restaurant leads using Google Places API."""
    params = {
        "query": query,
        "key": GOOGLE_PLACES_API_KEY,
    }
    if next_page_token:
        params["pagetoken"] = next_page_token
        time.sleep(2)  # Delay to handle Google API pagination
    
    response = requests.get(PLACES_URL, params=params)
    data = response.json()
    
    restaurants = []
    for result in data.get("results", []):
        name = result.get("name", "N/A")
        website = result.get("website", "N/A")
        address = result.get("formatted_address", "N/A")
        phone = result.get("formatted_phone_number", "N/A")
        instagram = scrape_instagram(website) if website != "N/A" else "No"
        
        restaurants.append([name, website, address, phone, instagram])
    
    next_token = data.get("next_page_token")
    return restaurants, next_token

def scrape_instagram(url):
    """Checks if a restaurant's website has an Instagram link."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                if "instagram.com" in link["href"]:
                    return "Yes"
    except requests.RequestException:
        pass
    return "No"

def save_to_google_sheets(data):
    """Saves restaurant data to Google Sheets."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    
    sheet.clear()
    sheet.append_row(["Restaurant Name", "Website", "Address", "Phone", "Instagram Exists"])
    sheet.append_rows(data)

if __name__ == "__main__":
    search_query = "Restaurants in Karachi"
    all_restaurants = []
    next_token = None
    
    while True:
        results, next_token = get_restaurants(search_query, next_token)
        all_restaurants.extend(results)
        if not next_token:
            break
    
    save_to_google_sheets(all_restaurants)
    print("Data saved to Google Sheets successfully!")
