import streamlit as st
from api import get_weather_data, get_weekly_forecast, generate_weather_description
from ui import display_current_weather, display_weekly_forecast, plot_temperature_chart
from utils import set_local_background, get_background_image_for_weather

def main():
    set_local_background("WeatherBackground1.jpg")
    st.sidebar.title("⛅ Weather Forecast AI")

    city = st.sidebar.text_input("Enter City Name:")
    if st.sidebar.button("Get Weather"):
        st.title(f"Weather Updates for {city}:")
        with st.spinner('Fetching weather data...'):
            weather_data = get_weather_data(city)

            if weather_data.get("cod") == 200 and "main" in weather_data:
                desc = weather_data['weather'][0]['description']
                set_local_background(get_background_image_for_weather(desc))

                display_current_weather(weather_data)
                st.subheader("AI Weather Summary")
                st.write(generate_weather_description(weather_data))

                lat, lon = weather_data['coord']['lat'], weather_data['coord']['lon']
                forecast_data = get_weekly_forecast(lat, lon)

                if forecast_data.get("cod") != "404":
                    display_weekly_forecast(forecast_data)
                    plot_temperature_chart(forecast_data)
                else:
                    st.error("Error fetching forecast!")
            else:
                st.error("‼ Error: City not found ‼")
    else:
# Intro Animation
        st.markdown("""
        <style>
        .typing {
            width: 22ch;
            white-space: nowrap;
            overflow: hidden;
            font-size: 2.5em;
            font-weight: bold;
            color: white;
            text-align: center;
            margin: 40px auto;
            animation: typing 2s steps(22);
        }
        @keyframes typing {
            from { width: 0 }
            to { width: 22ch }
        }
        </style>
        <div class="typing">Weather Chatbot</div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
