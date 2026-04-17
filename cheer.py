import requests
import streamlit as st
import datetime
from datetime import timedelta
from bs4 import BeautifulSoup

st.set_page_config(page_title="USD to TWD Converter")

def get_last_business_day(date):
    check_date = date - timedelta(days=1)
    for _ in range(7):
        if check_date.weekday() < 5:
            return check_date
        check_date -= timedelta(days=1)
    return None

def get_rate_from_bot(date):
    url = f"https://rate.bot.com.tw/xrt/quote/{date.strftime('%Y-%m')}/USD"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")
    
    date_str = date.strftime("%Y/%m/%d")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 5 and date_str in row.text:
            return {
                "cash_buy": float(cells[0].text.strip()),
                "cash_sell": float(cells[1].text.strip()),
                "spot_buy": float(cells[2].text.strip()),
                "spot_sell": float(cells[3].text.strip()),
            }
    return None

st.title("USD to TWD Converter - Bank of Taiwan Historical Rate")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Select date", value=datetime.date(2026, 4, 10))
with col2:
    usd_amount = st.number_input("Enter amount (USD)", min_value=0.0, value=100.0)

rate_type = st.radio("Rate type", ["Cash", "Spot"], horizontal=True)

if st.button("Convert"):
    rate_data = get_rate_from_bot(date)
    
    if rate_data is None:
        last_bd = get_last_business_day(date)
        st.warning(f"{date} is a holiday. Using last business day: {last_bd.strftime('%Y-%m-%d')}")
        date = last_bd
        rate_data = get_rate_from_bot(date)
    
    if rate_data:
        key = "cash_sell" if rate_type == "Cash" else "spot_sell"
        rate = rate_data[key]
        twd_result = usd_amount * rate
        st.success(f"**Date:** {date.strftime('%Y-%m-%d')}")
        st.metric(f"USD {rate_type} Sell Rate", f"{rate} TWD")
        st.metric("Result", f"{usd_amount:.2f} USD = {twd_result:.2f} TWD")
    else:
        st.error("Failed to get rate data")