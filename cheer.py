import requests
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="USD to TWD Converter")

def get_last_business_day(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    check_date = date - timedelta(days=1)
    for _ in range(7):
        if check_date.weekday() < 5:
            return check_date.strftime("%Y-%m-%d")
        check_date -= timedelta(days=1)
    return None

st.title("USD to TWD Converter - Bank of Taiwan Historical Rate")

date = st.text_input("Enter date (YYYY-MM-DD)", value="2026-04-10")
usd_amount = st.number_input("Enter amount (USD)", min_value=0.0, value=100.0)

if st.button("Convert"):
    url = f"https://cdn.jsdelivr.net/gh/haotool/app@data/public/rates/history/{date}.json"

    try:
        response = requests.get(url)
        if response.status_code == 404:
            last_bd = get_last_business_day(date)
            st.warning(f"{date} is a holiday. Using last business day: {last_bd}")
            url = f"https://cdn.jsdelivr.net/gh/haotool/app@data/public/rates/history/{last_bd}.json"
            date = last_bd

        data = response.json()
        rate = data['details']['USD']['cash']['sell']
        twd_result = usd_amount * rate

        st.success(f"**Date:** {date}")
        st.metric("USD Cash Sell Rate", f"{rate} TWD")
        st.metric("Result", f"{usd_amount:.2f} USD = {twd_result:.2f} TWD")
    except Exception as e:
        st.error(f"An error occurred: {e}")
