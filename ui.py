from datetime import datetime
import streamlit as st
import pandas as pd
from utils import kelvin_to_celsius, get_weather_icon

def display_current_weather(data):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Temperature 🌡", f"{kelvin_to_celsius(data['main']['temp']):.2f} °C")
        st.metric("Humidity 💧", f"{data['main']['humidity']}%")
    with col2:
        st.metric("Pressure 🌌", f"{data['main']['pressure']} hPa")
        st.metric("Wind Speed 🌫", f"{data['wind']['speed']} m/s")

def display_weekly_forecast(data):
    st.write("### Weekly Weather Forecast")
    displayed_dates = set()
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.write("**Day**")
    with c2: st.write("*Desc*")
    with c3: st.write("*Min Temp*")
    with c4: st.write("*Max Temp*")

    for day in data['list']:
        date = datetime.fromtimestamp(day['dt']).strftime('%A, %b %d')
        if date not in displayed_dates:
            displayed_dates.add(date)

            min_temp = kelvin_to_celsius(day['main']['temp_min'])
            max_temp = kelvin_to_celsius(day['main']['temp_max'])
            desc = day['weather'][0]['description']
            icon = get_weather_icon(desc)

            with c1: st.write(date)
            with c2: st.write(f"{icon} {desc.capitalize()}")
            with c3: st.write(f"{min_temp:.1f}°C")
            with c4: st.write(f"{max_temp:.1f}°C")

def plot_temperature_chart(data):
    st.subheader("Temperature Chart")
    chart_data = {"Date": [], "Min Temp (°C)": [], "Max Temp (°C)": []}

    for entry in data['list']:
        date = datetime.fromtimestamp(entry['dt']).strftime('%Y-%m-%d %H:%M')
        chart_data["Date"].append(date)
        chart_data["Min Temp (°C)"].append(kelvin_to_celsius(entry['main']['temp_min']))
        chart_data["Max Temp (°C)"].append(kelvin_to_celsius(entry['main']['temp_max']))

    df = pd.DataFrame(chart_data)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    st.line_chart(df)
