import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

try:
    # Authentication
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(credentials)
    
    # Display current spreadsheet info
    if SPREADSHEET_ID:
        print(f"Current SPREADSHEET_ID: {SPREADSHEET_ID}")
        print(f"Direct URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        
        try:
            sheet = client.open_by_key(SPREADSHEET_ID)
            print(f"Title: {sheet.title}")
            print("Status: Accessible ✓")
        except (gspread.exceptions.SpreadsheetNotFound, 
                gspread.exceptions.APIError, 
                FileNotFoundError) as e:
            print(f"Status: Not accessible ✗ ({e})")
    else:
        print("No SPREADSHEET_ID found in .env file")

    # List all accessible spreadsheets
    print("\nAll accessible spreadsheets:")
    all_sheets = client.openall()
    if all_sheets:
        for i, sheet in enumerate(all_sheets, 1):
            print(f"{i}. {sheet.title} (ID: {sheet.id})")
            print(f"   URL: https://docs.google.com/spreadsheets/d/{sheet.id}")
    else:
        print("No spreadsheets found or accessible with this service account")
        
except (gspread.exceptions.SpreadsheetNotFound, 
        gspread.exceptions.APIError, 
        FileNotFoundError) as e:
    print(f"Error: {e}")
