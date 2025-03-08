import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from search import search_companies
from sheets import save_to_google_sheets

# UI Initialization
root = tb.Window(themename="darkly")
root.title("Company Search Tool")
root.state("zoomed")
root.configure(bg="#181818")

# Layout Setup
frame = tk.Frame(root, padx=30, pady=30, bg="#181818")
frame.grid(row=0, column=0, sticky="nsew")
frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

# Search Bar
search_frame = tk.Frame(frame, bg="#181818")
search_frame.grid(row=0, column=0, sticky="ew", pady=10)
search_frame.columnconfigure(1, weight=1)

tb.Label(search_frame, text="Enter Search Query:", font=("Arial", 14), background="#181818", foreground="white").grid(row=0, column=0, padx=10)
search_entry = tb.Entry(search_frame, font=("Arial", 14), bootstyle="dark")
search_entry.grid(row=0, column=1, padx=10, sticky="ew")

search_button = tb.Button(search_frame, text="Search", command=lambda: start_search(), bootstyle="success-outline", padding=10)
search_button.grid(row=0, column=2, padx=10)

save_button = tb.Button(search_frame, text="Save to Google Sheets", command=lambda: save_results(), bootstyle="primary-outline", padding=10)
save_button.grid(row=0, column=3, padx=10)

# Table Setup (Full Screen)
columns = ("Company Name", "Website", "Description")
table = ttk.Treeview(frame, columns=columns, show="headings", style="dark.Treeview")
table.grid(row=1, column=0, sticky="nsew")

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center")

# **New Dynamic Status Bar**
status_bar = tb.Label(root, text="Ready", font=("Arial", 12), anchor="w", bootstyle="dark-inverse")
status_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

# Spinner Animation
spinner_label = tb.Label(root, text="⏳", font=("Arial", 20), background="#181818", foreground="white")
spinner_active = False

def update_status(message):
    """Update the status bar with a given message."""
    status_bar.config(text=message)

def start_spinner():
    """Starts the spinner animation."""
    global spinner_active
    spinner_active = True
    spinner_label.grid(row=3, column=0, sticky="e", padx=20, pady=5)

    def animate():
        spin_chars = ["⏳", "🔄", "⌛", "🔁"]
        while spinner_active:
            for char in spin_chars:
                spinner_label.config(text=char)
                time.sleep(0.2)
    
    threading.Thread(target=animate, daemon=True).start()

def stop_spinner():
    """Stops the spinner animation."""
    global spinner_active
    spinner_active = False
    spinner_label.grid_remove()

def start_search():
    """Handles the search operation in a separate thread."""
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Warning", "Please enter a search query.")
        return

    update_status("Searching...")
    start_spinner()
    search_button.config(state=tk.DISABLED)

    def perform_search():
        try:
            results = search_companies(query)
            display_results(results)
            update_status("Search Completed")
        except Exception as e:
            update_status(f"Error: {str(e)}")

        search_button.config(state=tk.NORMAL)
        stop_spinner()

    threading.Thread(target=perform_search, daemon=True).start()

def display_results(results):
    """Displays search results in the table."""
    table.delete(*table.get_children())
    for result in results:
        table.insert("", "end", values=result)

def save_results():
    """Saves the search results to Google Sheets."""
    data = [table.item(item, "values") for item in table.get_children()]
    if not data:
        messagebox.showwarning("Warning", "No data to save.")
        return

    update_status("Saving to Google Sheets...")
    start_spinner()
    save_button.config(state=tk.DISABLED)

    def perform_save():
        try:
            save_to_google_sheets(data)
            update_status("Saved to Google Sheets ✅")
        except Exception as e:
            update_status(f"Save Error: {str(e)}")

        save_button.config(state=tk.NORMAL)
        stop_spinner()

    threading.Thread(target=perform_save, daemon=True).start()

# Start UI
root.mainloop()
