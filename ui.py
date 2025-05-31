from datetime import datetime
import streamlit as st
import pandas as pd
from utils import kelvin_to_celsius, get_weather_icon
import folium
from streamlit_folium import st_folium

# Apply custom CSS to style the app
def apply_custom_css():
    st.markdown("""
    <style>
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    .weather-card, .map-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
        text-shadow: 1px 1px 2px black;
    }

    .metric-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        padding: 15px;
        border-radius: 12px;
        margin: 8px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
    }

    .forecast-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: Black;
    }

    .ai-summary {
        background: linear-gradient(145deg, #ff9a9e 0%, #fecfef 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(255, 154, 158, 0.3);
        border-left: 5px solid #ff6b6b;
        color: #2c3e50;
        font-size: 16px;
        font-weight: 500;
    }

    .weather-title {
        font-size: 28px;
        font-weight: bold;
        color: white;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)


def display_current_weather(data: dict):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Temperature 🌡", f"{kelvin_to_celsius(data['main']['temp']):.2f} °C")
        st.metric("Humidity 💧", f"{data['main']['humidity']}%")
    with col2:
        st.metric("Pressure 🌌", f"{data['main']['pressure']} hPa")
        st.metric("Wind Speed 🌫", f"{data['wind']['speed']} m/s")

# Display a styled 7-day forecast summary
def display_weekly_forecast(data: dict):
    try:
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader("📅 Weekly Forecast")

        displayed_dates = set()
        forecast_cards = []

        for entry in data['list']:
            date_str = datetime.fromtimestamp(entry['dt']).strftime('%A, %b %d')
            if date_str in displayed_dates or len(forecast_cards) >= 7:
                continue

            displayed_dates.add(date_str)
            min_temp = kelvin_to_celsius(entry['main']['temp_min'])
            max_temp = kelvin_to_celsius(entry['main']['temp_max'])
            desc = entry['weather'][0]['description']
            icon = get_weather_icon(desc)

            forecast_cards.append({
                "date": date_str,
                "icon": icon,
                "description": desc.title(),
                "min_temp": min_temp,
                "max_temp": max_temp
            })

        # Display cards in 4 columns
        cols = st.columns(4)
        for i, card in enumerate(forecast_cards):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="forecast-card">
                    <h4>{card['date']}</h4>
                    <div style="font-size: 2em;">{card['icon']}</div>
                    <p><b>{card['description']}</b></p>
                    <p>🌡️ {card['max_temp']:.1f}°C / {card['min_temp']:.1f}°C</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error displaying forecast: {e}")


def plot_temperature_chart(data: dict):
    try:
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.subheader("📊 Temperature Trends")

        records = {
            "DateTime": [],
            "Temperature (°C)": [],
            "Feels Like (°C)": [],
            "Humidity (%)": []
        }

        for entry in data['list']:
            dt = datetime.fromtimestamp(entry['dt'])
            main = entry['main']
            records["DateTime"].append(dt)
            records["Temperature (°C)"].append(kelvin_to_celsius(main['temp']))
            records["Feels Like (°C)"].append(kelvin_to_celsius(main['feels_like']))
            records["Humidity (%)"].append(main['humidity'])

        df = pd.DataFrame(records).set_index("DateTime")

        tab1, tab2 = st.tabs(["🌡️ Temperature", "💧 Humidity"])
        with tab1:
            st.line_chart(df[["Temperature (°C)", "Feels Like (°C)"]])
        with tab2:
            st.line_chart(df[["Humidity (%)"]])

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error plotting temperature chart: {e}")

def create_weather_map(lat, lon, city_name, weather_data):
    try:
        # Create a folium map centered on the location with better tile options
        m = folium.Map(
            location=[lat, lon],
            zoom_start=11,
            tiles='OpenStreetMap',  # We'll add tiles manually for better control
            prefer_canvas=True
        )
        
        # Add multiple tile layer options
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='Street Map',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='CartoDB Positron',
            name='Light Map',
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Get weather info for popup
        temp = weather_data['main']['temp'] - 273.15
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        
        # Create enhanced popup content with better styling
        popup_content = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    width: 220px; padding: 10px; background: white; border-radius: 8px;">
            <h3 style="color: #2c3e50; margin: 0 0 10px 0; text-align: center; 
                       border-bottom: 2px solid #3498db; padding-bottom: 5px;">
                📍 {city_name}
            </h3>
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #e74c3c;">🌡️ Temperature:</span>
                    <span style="color: #2c3e50; font-weight: bold;">{temp:.1f}°C</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #3498db;">☁️ Condition:</span>
                    <span style="color: #2c3e50;">{description.title()}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #9b59b6;">💧 Humidity:</span>
                    <span style="color: #2c3e50;">{humidity}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; color: #1abc9c;">💨 Wind:</span>
                    <span style="color: #2c3e50;">{wind_speed} m/s</span>
                </div>
            </div>
        </div>
        """
        
        # Add weather marker with custom icon
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=folium.Tooltip(f"🌤️ {city_name} Weather", sticky=True),
            icon=folium.Icon(
                color='red', 
                icon='cloud',
                prefix='fa'
            )
        ).add_to(m)
        
        # Add a styled circle to highlight the area
        folium.Circle(
            location=[lat, lon],
            radius=8000,
            popup=f"🌍 {city_name} Weather Zone",
            color='#3498db',
            fill=True,
            fillColor='#3498db',
            fillOpacity=0.2,
            opacity=0.8,
            weight=3
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None
