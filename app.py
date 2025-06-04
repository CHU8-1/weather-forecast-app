import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 讀取 API key（來自 secrets）
api_key = st.secrets["weather"]["api_key"]
st.write("API Key loaded:", api_key)
# 設定頁面標題
st.set_page_config(page_title="天氣預報趨勢圖", layout="wide")

# Streamlit 介面
st.title("🌤️ 一週天氣預報趨勢圖")
st.markdown("輸入一或多個城市（用英文逗號隔開，例如：`Taipei,Tokyo,New York`）")

# 使用者輸入
city_input = st.text_input("請輸入城市名稱", value="Taipei")
cities = [city.strip() for city in city_input.split(',')]

# 取得天氣資料的函式
def get_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()
    df = pd.DataFrame(data['list'])
    df['datetime'] = pd.to_datetime(df['dt'], unit='s')
    df['temp'] = df['main'].apply(lambda x: x['temp'])
    df['humidity'] = df['main'].apply(lambda x: x['humidity'])
    return df[['datetime', 'temp', 'humidity']]

# 畫圖函式
def plot_weather(df, city):
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(df['datetime'], df['temp'], label='Temperature (°C)', color='red')
    ax1.set_ylabel('Temperature (°C)', color='red')
    ax2 = ax1.twinx()
    ax2.plot(df['datetime'], df['humidity'], label='Humidity (%)', color='blue')
    ax2.set_ylabel('Humidity (%)', color='blue')
    plt.title(f"{city} 一週天氣趨勢")
    plt.tight_layout()
    st.pyplot(fig)

# 顯示資料與圖表
for city in cities:
    st.subheader(f"📍 {city}")
    data = get_weather_data(city, api_key)
    if data is not None:
        st.dataframe(data)
        plot_weather(data, city)
    else:
        st.error(f"無法取得 {city} 的資料。請確認城市拼字正確。")

