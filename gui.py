import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from search import search_companies
from sheets import save_to_google_sheets

# UI Initialization with Darkly Theme
root = tb.Window(themename="darkly")
root.title("Company Search Tool")
root.state("zoomed")
root.configure(bg="#222222")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Layout Setup
frame = tk.Frame(root, padx=30, pady=30, bg="#222222")
frame.grid(row=0, column=0, sticky="nsew")
frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

# Search Bar
search_frame = tk.Frame(frame, bg="#222222")
search_frame.grid(row=0, column=0, sticky="ew", pady=10)
search_frame.columnconfigure(1, weight=1)

tb.Label(search_frame, text="Enter Search Query:", font=("Arial", 14), background="#222222", foreground="white").grid(row=0, column=0, padx=10)
search_entry = tb.Entry(search_frame, font=("Arial", 14), bootstyle="dark")
search_entry.grid(row=0, column=1, padx=10, sticky="ew")

search_button = tb.Button(search_frame, text="Search", command=lambda: start_search(), bootstyle="success-outline", padding=10)
search_button.grid(row=0, column=2, padx=10)

save_button = tb.Button(search_frame, text="Save to Google Sheets", command=lambda: save_results(), bootstyle="primary-outline", padding=10)
save_button.grid(row=0, column=3, padx=10)

# Table Setup (Expands to Full Screen)
columns = ("Company Name", "Website", "Description")
table = ttk.Treeview(frame, columns=columns, show="headings", style="darkly.Treeview")
table.grid(row=1, column=0, sticky="nsew")

frame.rowconfigure(1, weight=1)
frame.columnconfigure(0, weight=1)

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", stretch=True)

# **Status Bar with Emoji Spinner**
status_frame = tk.Frame(root, bg="#222222")
status_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
status_frame.columnconfigure(0, weight=1)

status_bar = tb.Label(status_frame, text="Ready", font=("Arial", 12), anchor="w", bootstyle="dark-inverse")
status_bar.grid(row=0, column=0, sticky="w")

spinner_label = tb.Label(status_frame, text="", font=("Arial", 14), background="#222222", foreground="white")
spinner_label.grid(row=0, column=1, sticky="e", padx=10)

def update_status(message):
    """Update the status bar message."""
    status_bar.config(text=message)

def start_spinner():
    """Starts the emoji spinner animation."""
    def animate():
        emojis = ["⏳", "🔄", "⌛", "🔁"]
        i = 0
        while spinner_label.running:
            spinner_label.config(text=emojis[i % len(emojis)])
            i += 1
            time.sleep(0.3)
    
    spinner_label.running = True
    threading.Thread(target=animate, daemon=True).start()

def stop_spinner():
    """Stops the emoji spinner animation."""
    spinner_label.running = False
    spinner_label.config(text="")

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
            update_status("Search Completed ✅")
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
