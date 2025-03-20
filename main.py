import streamlit as st

st.title("AI Web Scraper")
url = st.text_input("Enter the URL of the website you want to scrape:")

if st.button("Scrape Website"):
    st.write(f"Scraping website")



