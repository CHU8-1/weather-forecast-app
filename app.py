import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# 🚨 這行一定要放最上面
st.set_page_config(page_title="天氣預報趨勢圖", layout="wide")

# 讀取 API key
api_key = st.secrets["weather"]["api_key"]

st.title("🌤️ 一週天氣預報趨勢圖")
st.markdown("輸入一或多個城市（用英文逗號隔開，例如：`Taipei,Tokyo,New York`）")
city_input = st.text_input("請輸入城市名稱", value="Taipei")
cities = [city.strip() for city in city_input.split(',')]

# 取得城市時區
def get_timezone(city):
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    geo_res = requests.get(geocode_url)
    if geo_res.status_code != 200 or not geo_res.json():
        return None
    geo_data = geo_res.json()[0]
    lat, lon = geo_data['lat'], geo_data['lon']
    tf = TimezoneFinder()
    return tf.timezone_at(lng=lon, lat=lat)

# 取得天氣資料並轉換時區
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        return None, None
    data = res.json()
    df = pd.DataFrame(data['list'])
    df['temp'] = df['main'].apply(lambda x: x['temp'])
    df['humidity'] = df['main'].apply(lambda x: x['humidity'])
    df['datetime'] = pd.to_datetime(df['dt'], unit='s').dt.tz_localize('None')

    timezone = get_timezone(city)
    if timezone:
        df['datetime'] = df['datetime'].dt.tz_convert(timezone)
        return df[['datetime', 'temp', 'humidity']], timezone
    else:
        return df[['datetime', 'temp', 'humidity']], None

# 畫圖
def plot_weather(df, city):
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df['datetime'], df['temp'], label='Temperature (°C)', color='red')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax2 = ax1.twinx()
    ax2.plot(df['datetime'], df['humidity'], label='Humidity (%)', color='blue')
    ax2.set_ylabel('Humidity (%)', color='blue')
    plt.title(f"{city}'s weekly weather trends")
    st.pyplot(fig)

# 顯示
for city in cities:
    st.subheader(f"📍 {city}")
    df, timezone = get_weather_data(city, api_key)
    if df is not None:
        if timezone:
            st.caption(f"🕒 顯示時間為 **{timezone} 當地時間**")
        st.dataframe(df)
        plot_weather(df, city)
    else:
        st.error(f"無法取得 {city} 的資料。請確認城市拼字正確。")


