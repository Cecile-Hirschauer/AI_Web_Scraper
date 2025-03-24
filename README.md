# AI Web Scraper

An intelligent web scraping solution that combines automated browser-based scraping with AI-powered content parsing and Google Sheets integration.

## Overview

AI Web Scraper is a Streamlit-based application that handles the complete web scraping workflow:

1. **Automated Scraping**: Uses Selenium with Bright Data proxy to handle anti-bot measures and CAPTCHAs
2. **Intelligent Parsing**: Leverages Ollama LLM (Large Language Model) to extract specific information from web content
3. **Result Storage**: Stores results in both local cache and Google Sheets for easy access and sharing
4. **User-Friendly Interface**: Provides a clean web interface for all scraping operations

## Features

- **CAPTCHA Handling**: Automatically solves CAPTCHAs using Bright Data's Scraping Browser
- **Intelligent Content Extraction**: Uses local LLM to extract exactly what you need from scraped content
- **Caching System**: Efficiently caches scraped content to minimize redundant requests
- **Google Sheets Integration**: Stores and indexes scraped data for collaborative access
- **Search & Retrieve**: Find previously parsed content through text search

## Requirements

- Python 3.8+
- Ollama with the Llama3 model installed locally
- Bright Data account with Scraping Browser access
- Google Cloud Platform account (for Google Sheets integration)

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/AI_Web_Scraper.git
   cd AI_Web_Scraper
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:

   ```
   BRD_AUTH=your_bright_data_auth_key
   GOOGLE_CREDENTIALS_FILE=credentials.json
   ```

4. For Google Sheets integration:
   - Follow instructions in the Google Cloud Console to create a service account
   - Download the credentials JSON file and save as `credentials.json` in the project root

## Usage

1. Start the Streamlit app:

   ```
   streamlit run main.py
   ```

2. Access the web interface at `http://localhost:8501`

3. Enter a URL to scrape

4. Describe the information you want to extract

5. View and search parsed results in the app or Google Sheets

## Project Structure

- `main.py`: Streamlit web interface
- `scrape.py`: Web scraping functionality using Selenium
- `parse.py`: Content parsing using Ollama LLM
- `cache_manager.py`: Local caching system
- `gsheets_storage.py`: Google Sheets integration
- `find_sheet.py`: Utility to find available Google Sheets

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Uses [Bright Data](https://brightdata.com/) for CAPTCHA solving and proxy services
- Powered by [Ollama](https://ollama.ai/) for local LLM inference
- Built with [Streamlit](https://streamlit.io/) for the web interface
- Integrates with [Google Sheets API](https://developers.google.com/sheets/api) for data storage
