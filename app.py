import streamlit as st
from api import get_weather_data, get_weekly_forecast, generate_weather_description, co
from ui import display_current_weather, display_weekly_forecast, plot_temperature_chart
from utils import set_local_background, get_background_image_for_weather


def main():
    st.markdown(set_local_background("Pictures/WeatherBackground1.png"), unsafe_allow_html=True)
    st.sidebar.title("⛅ Weather Forecast AI")

    city = st.sidebar.text_input("Enter City Name:").strip().title()
    
    if st.sidebar.button("Get Weather"):
        st.title(f"Weather Updates for {city}:")
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


# Chatbot
st.sidebar.markdown("---")
st.sidebar.header("🤖 Weather Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_msg = st.sidebar.text_input("Ask the bot about the weather...")

if st.sidebar.button("Send"):
    if user_msg:
        st.session_state.chat_history.append(("You", user_msg))

        # Step 1: Try to extract a city name (simplified: last capitalized word)
        import re
        match = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", user_msg)
        city_guess = match[-1] if match else None

        if city_guess:
            weather_data = get_weather_data(city_guess)
            if weather_data.get("cod") == 200:
                reply = generate_weather_description(weather_data)
            else:
                reply = f"Sorry, I couldn't find the weather for **{city_guess}**."
        else:
            # fallback to language model response
            prompt = f"You are a weather chatbot. Answer this user query: {user_msg}"
            response = co.generate(
                model='command-r-plus',
                prompt=prompt,
                max_tokens=80,
                temperature=0.7
            )
            reply = response.generations[0].text.strip()

        st.session_state.chat_history.append(("Bot", reply))
        
# Display chat history
for speaker, message in st.session_state.chat_history:
    st.sidebar.markdown(f"**{speaker}:** {message}")
