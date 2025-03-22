"""Streamlit web interface for AI-powered web scraping and content parsing."""

import os
import json
from datetime import datetime

import streamlit as st

from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content
from parse import parse_with_ollama
from cache_manager import CACHE_DIR, clean_expired_cache

st.set_page_config(page_title="AI Web Scraper", layout="wide")
st.title("AI Web Scraper")

# Initialize session state for cache settings if not already present
if 'use_cache' not in st.session_state:
    st.session_state.use_cache = True
if 'cache_expiry' not in st.session_state:
    st.session_state.cache_expiry = 24

# Sidebar for cache settings
with st.sidebar:
    st.header("Cache Settings")
    
    # Cache toggle
    use_cache = st.checkbox("Use Cache", value=st.session_state.use_cache,
                           help="Load previously scraped websites from cache when enabled")
    st.session_state.use_cache = use_cache
    
    # Cache expiry setting
    cache_expiry = st.slider("Cache Expiry (hours)", min_value=1, max_value=168, 
                             value=st.session_state.cache_expiry,
                             help="How long to keep cached content before re-scraping")
    st.session_state.cache_expiry = cache_expiry
    
    # Cache cleanup button
    if st.button("Clear Expired Cache"):
        clean_expired_cache()
        st.success("Expired cache entries removed")
    
    # View cache stats
    st.header("Cache Statistics")
    
    # Get cache statistics if the cache directory exists
    if os.path.exists(CACHE_DIR):
        index_path = os.path.join(CACHE_DIR, "index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                current_time = datetime.now()
                ACTIVE_ENTRIES = 0
                EXPIRED_ENTRIES = 0
                
                for _, info in index_data.items():
                    expiry_time = datetime.fromisoformat(info['expiry'])
                    if current_time <= expiry_time:
                        ACTIVE_ENTRIES += 1
                    else:
                        EXPIRED_ENTRIES += 1
                
                st.metric("Active Cache Entries", ACTIVE_ENTRIES)
                st.metric("Expired Cache Entries", EXPIRED_ENTRIES)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                st.error("Error reading cache index")
        else:
            st.info("No cache index found")
    else:
        st.info("No cache directory exists yet")

# Main content area
url = st.text_input("Enter the URL of the website you want to scrape:")

# Cache status indicator
if url and st.session_state.use_cache:
    from cache_manager import generate_cache_key, get_cache_path
    
    CACHE_KEY = generate_cache_key(url)
    cache_path = get_cache_path(CACHE_KEY)
    
    if os.path.exists(cache_path):
        st.info("📦 This URL exists in cache and will be loaded quickly")

# Step 1: Scrape the Website
col1, col2 = st.columns([1, 3])

with col1:
    scrape_button = st.button("Scrape Website", type="primary")

# Display cache settings being used
with col2:
    if url:
        CACHE_STATUS = "🟢 Using cache" if st.session_state.use_cache else "🔴 Cache disabled"
        HOURS_TEXT = f"{st.session_state.cache_expiry} hours"
        EXPIRY_INFO = f", expiry: {HOURS_TEXT}" if st.session_state.use_cache else ""
        st.caption(f"{CACHE_STATUS}{EXPIRY_INFO}")

if scrape_button:
    if url:
        with st.spinner("Scraping the website..."):
            # Scrape the website with cache settings from session state
            dom_content = scrape_website(
                url, 
                use_cache=st.session_state.use_cache,
                cache_expiry_hours=st.session_state.cache_expiry
            )
            BODY_CONTENT = extract_body_content(dom_content)
            CLEANED_CONTENT = clean_body_content(BODY_CONTENT)

            # Store the DOM content in Streamlit session state
            st.session_state.dom_content = CLEANED_CONTENT
            st.session_state.current_url = url

            # Display the DOM content in an expandable text box
            with st.expander("View DOM Content"):
                st.text_area("DOM Content", CLEANED_CONTENT, height=300)
            
            st.success("Website scraped successfully!")
    else:
        st.error("Please enter a URL first")

# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    st.subheader(f"Parsing content from: {st.session_state.get('current_url', 'Unknown URL')}")
    
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            with st.spinner("Parsing the content..."):
                dom_chunks = split_dom_content(st.session_state.dom_content)
                PARSED_RESULT = parse_with_ollama(dom_chunks, parse_description)
                
                st.subheader("Parsed Result")
                st.write(PARSED_RESULT)
        else:
            st.error("Please enter a description of what to parse")
