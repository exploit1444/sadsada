import streamlit as st
import re
from api import get_weather_data, get_weekly_forecast, generate_weather_description, co
from ui import display_current_weather, display_weekly_forecast, plot_temperature_chart
from utils import set_local_background, get_background_image_for_weather

def main():
    st.markdown(set_local_background("Pictures/WeatherBackground1.jpg"), unsafe_allow_html=True)
    st.title("⛅ Weather Forecast AI")

    tab1, tab2 = st.tabs(["📍 Weather Forecast", "💬 Chatbot Assistant"])

    # === Weather Forecast Tab ===
    with tab1:
        st.subheader("Check Real-Time Weather")
        city = st.text_input("Enter City Name:").strip().title()

        if not city:
            st.info("👋 Enter a city name above to get the weather.")

        if st.button("Get Weather"):
            with st.spinner('Fetching weather data...'):
                weather_data = get_weather_data(city)

                if weather_data.get("cod") == 200 and "main" in weather_data:
                    desc = weather_data['weather'][0]['description']
                    st.markdown(set_local_background(get_background_image_for_weather(desc)), unsafe_allow_html=True)

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
                    st.error(f"‼ Error: {weather_data.get('message', 'City not found')} ‼")

    # === Chatbot Tab ===
    with tab2:
        st.subheader("Weather Chatbot")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_msg = st.text_input("Ask the bot about the weather...")

        if st.button("Send"):
            if user_msg:
                st.session_state.chat_history.append(("You", user_msg))

                # Try to extract a city name
                match = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", user_msg)
                city_guess = match[-1] if match else None

                if city_guess:
                    weather_data = get_weather_data(city_guess)
                    if weather_data.get("cod") == 200:
                        reply = generate_weather_description(weather_data)
                    else:
                        reply = f"Sorry, I couldn't find the weather for **{city_guess}**."
                else:
                    prompt = f"You are a weather chatbot. Answer this user query: {user_msg}"
                    response = co.generate(
                        model='command-r-plus',
                        prompt=prompt,
                        max_tokens=80,
                        temperature=0.7
                    )
                    reply = response.generations[0].text.strip()

                st.session_state.chat_history.append(("Bot", reply))

        # Display conversation
        if len(st.session_state.chat_history) == 0:
            st.markdown("💬 Ask me anything about the weather — like *'How's the weather in Tokyo?*'")
        else:
            for speaker, message in st.session_state.chat_history:
                emoji = "🙋‍♂️" if speaker == "You" else "🤖"
                st.markdown(f"{emoji} **{speaker}:** {message}")

if __name__ == "__main__":
    main()
