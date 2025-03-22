"""Streamlit web interface for AI-powered web scraping and content parsing."""

import streamlit as st
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content

st.title("AI Web Scraper")
url = st.text_input("Enter the URL of the website you want to scrape:")

# Step 1: Scrape the Website
if st.button("Scrape Website"):
    if url:
        st.write("Scraping the website...")

        # Scrape the website
        dom_content = scrape_website(url)
        BODY_CONTENT = extract_body_content(dom_content)
        CLEANED_CONTENT = clean_body_content(BODY_CONTENT)

        # Store the DOM content in Streamlit session state
        st.session_state.dom_content = CLEANED_CONTENT

        # Display the DOM content in an expandable text box
        with st.expander("View DOM Content"):
            st.text_area("DOM Content", CLEANED_CONTENT, height=300)

# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")

            dom_chunks = split_dom_content(st.session_state.dom_content)
