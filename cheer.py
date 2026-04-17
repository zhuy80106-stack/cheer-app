import requests
import streamlit as st
import datetime
from datetime import timedelta
import pandas as pd
from io import StringIO

st.set_page_config(page_title="USD to TWD Converter")

def get_last_business_day(date):
    check_date = date - timedelta(days=1)
    for _ in range(7):
        if check_date.weekday() < 5:
            return check_date
        check_date -= timedelta(days=1)
    return None

@st.cache_data
def get_rates_from_bot(month_str):
    url = f"https://rate.bot.com.tw/xrt/flcsv/0/{month_str}/USD"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    lines = response.text.strip().split("\n")
    
    data = []
    for line in lines[1:]:
        cols = line.split(",")
        if len(cols) >= 16 and cols[1] == "USD":
            data.append({
                "date": cols[0],
                "cash_buy": cols[3],
                "spot_buy": cols[4],
                "cash_sell": cols[15],
                "spot_sell": cols[14],
            })
    return pd.DataFrame(data)

st.title("USD to TWD Converter - Bank of Taiwan Historical Rate")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Select date", value=datetime.date(2026, 4, 10))
with col2:
    usd_amount = st.number_input("Enter amount (USD)", min_value=0.0, value=100.0)

rate_type = st.radio("Rate type", ["Cash", "Spot"], horizontal=True)

if st.button("Convert"):
    month_str = date.strftime("%Y-%m")
    date_str = date.strftime("%Y%m%d")
    
    try:
        df = get_rates_from_bot(month_str)
        row = df[df["date"].str.contains(date_str)]
        
        if row.empty:
            last_bd = get_last_business_day(date)
            st.warning(f"{date_str} is a holiday. Using last business day: {last_bd.strftime('%Y-%m-%d')}")
            date = last_bd
            month_str = date.strftime("%Y-%m")
            date_str = date.strftime("%Y%m%d")
            df = get_rates_from_bot(month_str)
            row = df[df["date"].str.contains(date_str)]
        
        if not row.empty:
            key = "cash_sell" if rate_type == "Cash" else "spot_sell"
            rate = float(row[key].values[0])
            twd_result = usd_amount * rate
            st.success(f"**Date:** {date.strftime('%Y-%m-%d')}")
            st.metric(f"USD {rate_type} Sell Rate", f"{rate} TWD")
            st.metric("Result", f"{usd_amount:.2f} USD = {twd_result:.2f} TWD")
        else:
            st.error("Failed to get rate data")
    except Exception as e:
        st.error(f"Error: {e}")