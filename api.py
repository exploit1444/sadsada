import requests
import cohere
from utils import kelvin_to_celsius
import folium

WEATHER_API_KEY = "2bf4686b58e818560cb0aa13c5fd0722"
COHERE_API_KEY = "S9HZs7bl6TAoVZHrPmTfK6ywe7gUVE3hMW4M6NGN"
co = cohere.Client(COHERE_API_KEY)

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()
    print(data)  # Or use st.write(data) temporarily to debug
    return data

def get_weekly_forecast(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
    return requests.get(url).json()

def generate_weather_description(data):
    try:
        temp = kelvin_to_celsius(data['main']['temp'])
        desc = data['weather'][0]['description']
        prompt = f"The current weather is {desc} with a temperature of {temp:.1f}°C. Generate a short, friendly weather summary."

        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=60,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return str(e)

__all__ = ['get_weather_data', 'get_weekly_forecast', 'generate_weather_description', 'co']
