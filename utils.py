import base64

def kelvin_to_celsius(temp_k):
    return temp_k - 273.15


def get_weather_icon(description):
    desc = description.lower()
    if "clear" in desc:
        return "☀️"
    elif "cloud" in desc:
        return "☁️"
    elif "rain" in desc:
        return "🌧"
    elif "snow" in desc:
        return "❄️"
    elif "storm" in desc or "thunder" in desc:
        return "⛈"
    elif "fog" in desc or "mist" in desc:
        return "🌫"
    else:
        return "🌤"

def set_local_background(image_path):
    with open(image_path, "rb") as img_file:
        b64_img = base64.b64encode(img_file.read()).decode()
    return f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
    """

def get_background_image_for_weather(description):
    desc = description.lower()
    if "clear" in desc:
        return "assets/sunny.jpg"
    elif "cloud" in desc:
        return "assets/cloudy.webp"
    elif "rain" in desc:
        return "assets/rainy.jpg"
    elif "storm" in desc or "thunder" in desc:
        return "assets/stormy.jpg"
    elif "snow" in desc:
        return "assets/snowy.webp"
    else:
        return "assets/WeatherBackground1.jpg"
