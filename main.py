import streamlit as st
from scraper import scrape_website

st.title("AI Web Scraper")
url = st.text_input("Enter the URL of the website you want to scrape:")

if st.button("Scrape Website"):
    st.write(f"Scraping website")
    result = scrape_website(url)
    print(result)


