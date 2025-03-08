import requests
from config import API_KEY, CSE_ID

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

def search_companies(query, num_results=20):
    """Searches companies using Google Custom Search API."""
    params = {
        "q": query,
        "key": API_KEY,
        "cx": CSE_ID,
        "num": num_results
    }
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return []
    
    results = []
    for item in data.get("items", []):
        title = item.get("title", "N/A")
        link = item.get("link", "N/A")
        snippet = item.get("snippet", "N/A")
        results.append([title, link, snippet])
    
    return results
