import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")
SHEET_ID = os.getenv("SHEET_ID")

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

def search_companies(query, num_results=10):
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
        messagebox.showerror("Error", f"Error fetching search results: {e}")
        return []
    
    results = []
    for item in data.get("items", []):
        title = item.get("title", "N/A")
        link = item.get("link", "N/A")
        snippet = item.get("snippet", "N/A")
        results.append([title, link, snippet])
    
    return results

def save_to_google_sheets(data):
    """Saves company data to Google Sheets."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_file = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "credentials.json")

    if not os.path.exists(credentials_file):
        messagebox.showerror("Error", "Google Sheets credentials file not found.")
        return
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1

    sheet.clear()
    sheet.append_row(["Company Name", "Website", "Description"])
    
    if data:
        sheet.append_rows(data)
    
    messagebox.showinfo("Success", "✅ Data saved to Google Sheets successfully!")

# ----------------- GUI Implementation -----------------

def start_search():
    """Starts the search in a separate thread to avoid freezing UI."""
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Warning", "Please enter a search query.")
        return

    search_button.config(state=tk.DISABLED)
    save_button.config(state=tk.DISABLED)
    loading_label.grid(row=2, column=0, columnspan=3, pady=5)

    def perform_search():
        results = search_companies(query)
        display_results(results)
        search_button.config(state=tk.NORMAL)
        save_button.config(state=tk.NORMAL)
        loading_label.grid_forget()
    
    threading.Thread(target=perform_search, daemon=True).start()

def display_results(results):
    """Displays the search results in the UI table."""
    for row in table.get_children():
        table.delete(row)

    for result in results:
        table.insert("", "end", values=result)

def save_results():
    """Saves the displayed results to Google Sheets."""
    data = [table.item(row)["values"] for row in table.get_children()]
    if not data:
        messagebox.showwarning("Warning", "No data to save!")
        return
    
    save_to_google_sheets(data)

# --------------- UI Setup ---------------
root = tk.Tk()
root.title("Company Search Tool")
root.geometry("700x400")
root.resizable(False, False)

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

# Search Bar
tk.Label(frame, text="Enter Search Query:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
search_entry = tk.Entry(frame, width=40, font=("Arial", 12))
search_entry.grid(row=0, column=1, padx=5, pady=5)
search_button = tk.Button(frame, text="Search", command=start_search, font=("Arial", 12), bg="#4CAF50", fg="white")
search_button.grid(row=0, column=2, padx=5, pady=5)

# Loading Label (Initially Hidden)
loading_label = tk.Label(frame, text="🔄 Searching...", font=("Arial", 12), fg="blue")

# Table (Treeview)
columns = ("Company Name", "Website", "Description")
table = ttk.Treeview(frame, columns=columns, show="headings", height=10)
for col in columns:
    table.heading(col, text=col)
    table.column(col, width=200)
table.grid(row=1, column=0, columnspan=3, pady=10)

# Save Button
save_button = tk.Button(frame, text="Save to Google Sheets", command=save_results, font=("Arial", 12), bg="#008CBA", fg="white")
save_button.grid(row=3, column=0, columnspan=3, pady=10)

# Start GUI
root.mainloop()
