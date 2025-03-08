import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, GOOGLE_CREDENTIALS

def save_to_google_sheets(data):
    """Saves company data to Google Sheets."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    if not os.path.exists(GOOGLE_CREDENTIALS):
        print("Google Sheets credentials file not found.")
        return
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1

    sheet.clear()
    sheet.append_row(["Company Name", "Website", "Description"])
    
    if data:
        sheet.append_rows(data)
    
    print("✅ Data saved to Google Sheets successfully!")
