"""Module for persisting web scraping results using Google Sheets API."""

import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Scope for Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Credentials and configuration
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

def get_client():
    """Get authenticated Google Sheets client."""
    try:
        # Load credentials
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        raise

def init_spreadsheet():
    """Initialize spreadsheet - create if not exists, reuse if exists."""
    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(f"Credentials file not found: {CREDENTIALS_FILE}")
    
    client = get_client()
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    # Case 1: An ID already exists in .env
    if spreadsheet_id:
        try:
            # Try to open the existing spreadsheet
            spreadsheet = client.open_by_key(spreadsheet_id)
            print(f"Reusing existing spreadsheet: {spreadsheet.title}")
            return spreadsheet.id
        except gspread.exceptions.SpreadsheetNotFound:
            # The ID exists but the spreadsheet doesn't exist anymore
            print("Configured spreadsheet no longer exists, creating a new one...")
            spreadsheet_id = None
    
    # Case 2: No ID or invalid ID, creating a new spreadsheet
    if not spreadsheet_id:
        try:
            spreadsheet = client.create("AI Web Scraper Data")
            
            # Share as read-only with everyone (optional)
            spreadsheet.share('', perm_type='anyone', role='reader')
            
            # Save ID to .env file
            update_env_file('SPREADSHEET_ID', spreadsheet.id)
            
            print(f"New spreadsheet created: {spreadsheet.title} (ID: {spreadsheet.id})")
            return spreadsheet.id
        except Exception as e:
            print(f"Error creating spreadsheet: {e}")
            raise


def update_env_file(key, value):
    """Update a specific key in the .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Read current content
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    else:
        lines = []
    
    # Check if key already exists
    key_exists = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_exists = True
            break
    
    # If key doesn't exist, add it
    if not key_exists:
        lines.append(f"{key}={value}\n")
    
    # Write updated content
    with open(env_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)
    
    print(f"Updated .env file: {key}={value}")

def save_scraped_content(url, cache_key=None):
    """Save scraped content metadata to spreadsheet."""
    client = get_client()
    spreadsheet_id = init_spreadsheet()
    if spreadsheet_id is None:
        raise ValueError("Failed to initialize spreadsheet")
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    try:
        worksheet = spreadsheet.worksheet("scraped_content")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet("scraped_content", 1, 4)
        worksheet.update([["id", "url", "timestamp", "cache_key"]])
    
    # Generate ID
    timestamp = datetime.now().isoformat()
    row_id = hash(url + timestamp) % 10000000  # Simple hash for ID
    
    # Check if URL already exists
    try:
        cell = worksheet.find(url)
        if cell:
            # Update existing row
            row = cell.row
            # Update cells individually
            worksheet.update_cell(row, 1, str(row_id))
            worksheet.update_cell(row, 2, str(url))
            worksheet.update_cell(row, 3, str(timestamp))
            worksheet.update_cell(row, 4, str(cache_key) if cache_key is not None else '')
            return row_id
    except gspread.exceptions.APIError:  # Generic API error that includes cell not found
        # Add new row
        worksheet.append_row([row_id, url, timestamp, str(cache_key)])
        return row_id

def save_parsed_result(url, parse_description, result):
    """Save parsed result to spreadsheet."""
    client = get_client()
    spreadsheet_id = init_spreadsheet()
    if spreadsheet_id is None:
        raise ValueError("Failed to initialize spreadsheet")
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    try:
        worksheet = spreadsheet.worksheet("parsed_results")
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet("parsed_results", 1, 5)
        worksheet.update([["id", "url", "parse_description", "result", "timestamp"]])
    
    # Generate ID and prepare data
    timestamp = datetime.now().isoformat()
    row_id = hash(url + parse_description + timestamp) % 10000000
    
    # Truncate result if it's too long (Google Sheets has a cell size limit)
    max_length = 50000
    if len(result) > max_length:
        result = result[:max_length-100] + "... [truncated]"
    
    # Add data
    worksheet.append_row([row_id, url, parse_description, result, timestamp])
    return row_id

def get_parsed_results(url=None, limit=10):
    """Get parsed results with optional filtering."""
    client = get_client()
    spreadsheet_id = init_spreadsheet()
    if spreadsheet_id is None:
        raise ValueError("Failed to initialize spreadsheet")
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    try:
        worksheet = spreadsheet.worksheet("parsed_results")
        all_data = worksheet.get_all_records()
        
        # Filter by URL if provided
        if url:
            filtered_data = [row for row in all_data if row["url"] == url]
        else:
            filtered_data = all_data
        
        # Sort by timestamp (newest first) and apply limit
        filtered_data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return filtered_data[:limit]
        
    except gspread.exceptions.WorksheetNotFound:
        return []

def search_parsed_results(search_term, limit=20):
    """Search for parsed results containing the search term."""
    client = get_client()
    spreadsheet_id = init_spreadsheet()
    if spreadsheet_id is None:
        raise ValueError("Failed to initialize spreadsheet")
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    try:
        worksheet = spreadsheet.worksheet("parsed_results")
        all_data = worksheet.get_all_records()
        
        # Search in parse_description and result columns
        search_results = [
            row for row in all_data 
            if search_term.lower() in str(row.get("parse_description", "")).lower() 
            or search_term.lower() in str(row.get("result", "")).lower()
        ]
        
        # Sort by timestamp (newest first) and apply limit
        search_results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return search_results[:limit]
        
    except gspread.exceptions.WorksheetNotFound:
        return []

# Helper to setup the required credentials
def setup_instructions():
    """Print instructions for setting up Google Sheets API access."""
    print("""
    To use Google Sheets storage, follow these steps:
    
    1. Go to Google Cloud Console (https://console.cloud.google.com/)
    2. Create a new project
    3. Enable Google Sheets API and Google Drive API
    4. Create a service account
    5. Download the JSON credentials file and save it as 'credentials.json' in your project directory
    6. Add these lines to your .env file:
       GOOGLE_CREDENTIALS_FILE=credentials.json
       
    After first run, a SPREADSHEET_ID will be added to your .env file automatically.
    """)
    