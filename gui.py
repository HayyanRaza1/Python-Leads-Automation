import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from search import search_companies
from sheets import save_to_google_sheets

# Initialize App with Dark Theme
root = tb.Window(themename="darkly")
root.title("Company Search Tool")
root.state("zoomed")  # Fullscreen mode
root.configure(bg="#181818")

# Configure root grid layout for responsiveness
root.rowconfigure(1, weight=1)  # Table takes most of the space
root.columnconfigure(0, weight=1)

# Main Frame
frame = tk.Frame(root, padx=30, pady=30, bg="#181818")
frame.grid(row=0, column=0, sticky="nsew")
frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)  # Table expands fully

# Search Bar (Top)
search_frame = tk.Frame(frame, bg="#181818")
search_frame.grid(row=0, column=0, sticky="ew", pady=10)
search_frame.columnconfigure(1, weight=1)

tb.Label(search_frame, text="Enter Search Query:", font=("Arial", 14), background="#181818", foreground="white").grid(row=0, column=0, padx=10)
search_entry = tb.Entry(search_frame, font=("Arial", 14), bootstyle="dark")
search_entry.grid(row=0, column=1, padx=10, sticky="ew")

search_button = tb.Button(search_frame, text="Search", command=lambda: start_search(), bootstyle="success-outline", padding=10)
search_button.grid(row=0, column=2, padx=10)

# Loading Label (Initially Hidden)
loading_label = tb.Label(frame, text="🔄 Searching...", font=("Arial", 14), background="#181818", foreground="#28a745")

# Saving Label (Initially Hidden)
saving_label = tb.Label(frame, text="💾 Saving...", font=("Arial", 14), background="#181818", foreground="#17a2b8")

# Table Frame (Expands to Full Height)
table_frame = tk.Frame(frame, bg="#181818")
table_frame.grid(row=1, column=0, sticky="nsew", pady=10)
table_frame.columnconfigure(0, weight=1)
table_frame.rowconfigure(0, weight=1)  # This ensures the table stretches to full height

# Table (Expands Fully)
columns = ("Company Name", "Website", "Description")
table = ttk.Treeview(table_frame, columns=columns, show="headings", style="dark.Treeview")
table.grid(row=0, column=0, sticky="nsew")  # Table expands fully

# Make Table Columns Adjustable
for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center")

# Scrollbars
y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview)
table.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)
y_scroll.grid(row=0, column=1, sticky="ns")
x_scroll.grid(row=1, column=0, sticky="ew")

# Save Button (Bottom Right)
button_frame = tk.Frame(frame, bg="#181818")
button_frame.grid(row=2, column=0, sticky="se", pady=20, padx=20)  # Stays at bottom right

save_button = tb.Button(button_frame, text="Save to Google Sheets", command=lambda: start_saving(), bootstyle="info-outline", padding=10)
save_button.pack(anchor="se")

# Function Definitions
def start_search():
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Warning", "Please enter a search query.")
        return
    search_button.config(state=tk.DISABLED)
    save_button.config(state=tk.DISABLED)
    loading_label.grid(row=3, column=0, pady=10)

    def perform_search():
        results = search_companies(query)
        display_results(results)
        search_button.config(state=tk.NORMAL)
        save_button.config(state=tk.NORMAL)
        loading_label.grid_forget()

    threading.Thread(target=perform_search, daemon=True).start()

def display_results(results):
    for row in table.get_children():
        table.delete(row)
    for result in results:
        table.insert("", "end", values=result)

def start_saving():
    data = [table.item(row)["values"] for row in table.get_children()]
    if not data:
        messagebox.showwarning("Warning", "No data to save!")
        return
    save_button.config(state=tk.DISABLED)
    saving_label.grid(row=4, column=0, pady=10)

    def perform_saving():
        save_to_google_sheets(data)
        messagebox.showinfo("Success", "Data saved successfully!")
        save_button.config(state=tk.NORMAL)
        saving_label.grid_forget()

    threading.Thread(target=perform_saving, daemon=True).start()

# Start the UI
root.mainloop()
