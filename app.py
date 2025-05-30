import streamlit as st
import re
from api import get_weather_data, get_weekly_forecast, generate_weather_description, co
from ui import display_current_weather, display_weekly_forecast, plot_temperature_chart, apply_custom_css, create_weather_map
from utils import set_local_background, get_background_image_for_weather
from streamlit_folium import st_folium

def main():
    apply_custom_css()
    st.markdown(set_local_background("Pictures/WeatherBackground1.jpg"), unsafe_allow_html=True)
    st.title("⛅ Weather Forecast AI")

    tab1, tab2 = st.tabs(["📍 Weather Forecast", "💬 Chatbot Assistant"])

    # === Tab 1: Weather Forecast ===
    with tab1:
        st.title("☀️ Weather AI App")

        city = st.text_input("Enter city name", "")

        # Initialize session state for weather button
        if "weather_clicked" not in st.session_state:
            st.session_state["weather_clicked"] = False

        if st.button("Get Weather"):
            st.session_state["weather_clicked"] = True

        if st.session_state["weather_clicked"] and city:
            weather_data = get_weather_data(city)

            if weather_data and weather_data.get("cod") != "404":
                display_current_weather(weather_data)

                lat = weather_data["coord"]["lat"]
                lon = weather_data["coord"]["lon"]

                forecast_data = get_weekly_forecast(lat, lon)

                if forecast_data and forecast_data.get("cod") != "404":
                    display_weekly_forecast(forecast_data)
                    plot_temperature_chart(forecast_data)
                else:
                    st.warning("⚠️ Forecast data not available.")

                weather_map = create_weather_map(lat, lon, city, weather_data)

                if weather_map:
                    st.markdown('<div class="map-container">', unsafe_allow_html=True)
                    st.subheader("🗺️ Weather Map View")
                    st_folium(weather_map, width=700, height=450)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("⚠️ Failed to load the weather map.")
            else:
                st.error("City not found.")

    # === Tab 2: Chatbot Assistant ===
    with tab2:
        st.subheader("Weather Chatbot")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_msg = st.text_input("Ask the bot about the weather...")

        if st.button("Send"):
            if user_msg:
                st.session_state.chat_history.append(("You", user_msg))

                # Attempt to extract a city from user message
                matches = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", user_msg)
                city_guess = matches[-1] if matches else None

                if city_guess:
                    weather_data = get_weather_data(city_guess)
                    if weather_data.get("cod") == 200:
                        reply = generate_weather_description(weather_data)
                    else:
                        reply = f"😕 Sorry, I couldn't find the weather for **{city_guess}**."
                else:
                    prompt = (
                        "Important: You are a weather chatbot. "
                        "When a user asks about the weather or provides any weather-related inquiries, "
                        "respond with accurate and helpful weather information. "
                        "If the inquiry is not related to weather, reply with: "
                        "'Inquiry not understood. Please ask about the weather.'\n\n"
                        f"Answer this user query: {user_msg}"
                    )
                    response = co.generate(
                        model="command-r-plus",
                        prompt=prompt,
                        max_tokens=80,
                        temperature=0.7,
                    )
                    reply = response.generations[0].text.strip()

                st.session_state.chat_history.append(("Bot", reply))

        # Display chat history
        if not st.session_state.chat_history:
            st.markdown("💬 Ask me anything about the weather — like *'How's the weather in Tokyo?'*")
        else:
            for speaker, message in st.session_state.chat_history:
                emoji = "🙋‍♂️" if speaker == "You" else "🤖"
                st.markdown(f"{emoji} **{speaker}:** {message}")


if __name__ == "__main__":
    main()