import requests
import streamlit as st
import datetime
from datetime import timedelta
import pandas as pd

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
    url = f"https://rate.bot.com.tw/xrt/quote/{month_str}/USD"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    tables = pd.read_html(response.text)
    df = tables[0]
    df.columns = ["date", "currency", "cash_buy", "cash_sell", "spot_buy", "spot_sell"]
    df = df[["date", "cash_buy", "cash_sell", "spot_buy", "spot_sell"]]
    return df

st.title("USD to TWD Converter - Bank of Taiwan Historical Rate")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Select date", value=datetime.date(2026, 4, 10))
with col2:
    usd_amount = st.number_input("Enter amount (USD)", min_value=0.0, value=100.0)

rate_type = st.radio("Rate type", ["Cash", "Spot"], horizontal=True)

if st.button("Convert"):
    month_str = date.strftime("%Y-%m")
    date_str = date.strftime("%Y/%m/%d")
    
    try:
        df = get_rates_from_bot(month_str)
        row = df[df["date"].str.contains(date_str)]
        
        if row.empty:
            last_bd = get_last_business_day(date)
            st.warning(f"{date_str} is a holiday. Using last business day: {last_bd.strftime('%Y-%m-%d')}")
            date = last_bd
            month_str = date.strftime("%Y-%m")
            date_str = date.strftime("%Y/%m/%d")
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