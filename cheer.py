import requests
import streamlit as st
import datetime
from datetime import timedelta

st.set_page_config(page_title="USD to TWD Converter")

def get_last_business_day(date):
    check_date = date - timedelta(days=1)
    for _ in range(7):
        if check_date.weekday() < 5:
            return check_date.strftime("%Y-%m-%d")
        check_date -= timedelta(days=1)
    return None

st.title("USD to TWD Converter - Bank of Taiwan Historical Rate")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Select date", value=datetime.date(2026, 4, 10))
with col2:
    usd_amount = st.number_input("Enter amount (USD)", min_value=0.0, value=100.0)

if st.button("Convert"):
    date_str = date.strftime("%Y-%m-%d")
    url = f"https://cdn.jsdelivr.net/gh/haotool/app@data/public/rates/history/{date_str}.json"

    try:
        response = requests.get(url)
        if response.status_code == 404:
            last_bd = get_last_business_day(date)
            st.warning(f"{date_str} is a holiday. Using last business day: {last_bd}")
            url = f"https://cdn.jsdelivr.net/gh/haotool/app@data/public/rates/history/{last_bd}.json"
            date_str = last_bd

        data = response.json()
        rate = data['details']['USD']['cash']['sell']
        twd_result = usd_amount * rate

        st.success(f"**Date:** {date_str}")
        st.metric("USD Cash Sell Rate", f"{rate} TWD")
        st.metric("Result", f"{usd_amount:.2f} USD = {twd_result:.2f} TWD")
    except Exception as e:
        st.error(f"An error occurred: {e}")
