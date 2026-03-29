import streamlit as st
import requests
import datetime

# Open-Meteo APIのエンドポイント
API_URL = "https://api.open-meteo.com/v1/forecast"


# 都市名と緯度経度の辞書
city_coords = {
    "札幌": (43.0642, 141.3469),
    "仙台": (38.2688, 140.8721),
    "新潟": (37.9161, 139.0364),
    "金沢": (36.5613, 136.6562),
    "東京": (35.6895, 139.6917),
    "名古屋": (35.1802, 136.9066),
    "大阪": (34.6937, 135.5023),
    "広島": (34.3963, 132.4596),
    "高知": (33.5597, 133.5311),
    "福岡": (33.5902, 130.4017),
    "那覇": (26.2124, 127.6809)
}

# セレクトボックスで都市選択（順番固定、初期値は東京）
city_list = list(city_coords.keys())
city = st.selectbox("都市を選択してください", city_list, index=city_list.index("東京"))
lat, lon = city_coords[city]

# 1週間分の日付リストを作成
today = datetime.date.today()
dates = [today + datetime.timedelta(days=i) for i in range(7)]

# Streamlitアプリのタイトル
st.title(f"{city}の1週間天気予報")

# APIパラメータ設定
params = {
    "latitude": lat,
    "longitude": lon,
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "weathercode",
        "precipitation_probability_mean"
    ],
    "timezone": "Asia/Tokyo"
}

# APIリクエスト
def get_weather():
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API取得エラー: {e}")
        return None

data = get_weather()

# 天気コードの簡易変換辞書と絵文字マッピング
weather_code_map = {
    0: ("快晴", "☀️"),
    1: ("主に晴れ", "🌤️"),
    2: ("部分的に曇り", "⛅"),
    3: ("曇り", "☁️"),
    45: ("霧", "🌫️"),
    48: ("霧氷", "🌫️"),
    51: ("霧雨(弱)", "🌦️"),
    53: ("霧雨(中)", "🌦️"),
    55: ("霧雨(強)", "🌦️"),
    61: ("雨(弱)", "🌧️"),
    63: ("雨(中)", "🌧️"),
    65: ("雨(強)", "🌧️"),
    71: ("雪(弱)", "🌨️"),
    73: ("雪(中)", "🌨️"),
    75: ("雪(強)", "❄️"),
    80: ("にわか雨", "🌦️"),
    81: ("にわか雨(強)", "🌦️"),
    82: ("にわか雨(激)", "🌦️"),
    95: ("雷雨", "⛈️"),
    96: ("雷雨(雹)", "⛈️")
}

if data:
    daily = data["daily"]
    st.subheader("日別天気予報")
    st.markdown('---')
    # 天気コードごとの背景色マッピング
    def get_bgcolor_by_code(code):
        # 晴れ系: 0,1,2
        if code in [0, 1, 2]:
            return "#FFA500"  # 橙色
        # 曇り系: 3,45,48
        elif code in [3, 45, 48]:
            return "#B0B0B0"  # 灰色
        # 雨系: 51,53,55,61,63,65,80,81,82,95,96
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96]:
            return "#3399FF"  # 青色
        # 雪系: 71,73,75
        elif code in [71, 73, 75]:
            return "#AEE9F7"  # 水色（雪用）
        else:
            return "#FFFFFF"  # デフォルト白

    for i in range(7):
        date_str = daily["time"][i]
        temp_max = daily["temperature_2m_max"][i]
        temp_min = daily["temperature_2m_min"][i]
        precipitation = daily["precipitation_sum"][i]
        code = daily["weathercode"][i]
        pop = daily.get("precipitation_probability_mean", [None]*7)[i]
        weather, emoji = weather_code_map.get(code, ("不明", ""))
        # 日付をYYYY年M月D日（曜日）形式に変換
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        youbi_list = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = youbi_list[date_obj.weekday()]
        formatted_date = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日（{weekday}） {emoji}"
        bgcolor = get_bgcolor_by_code(code)
        st.markdown(f"<div style='background-color:{bgcolor};padding:16px;border-radius:8px;'>", unsafe_allow_html=True)
        st.markdown(f"### {formatted_date}")
        st.write(f"天気: {weather}")
        st.write(f"最高気温: {temp_max}℃")
        st.write(f"最低気温: {temp_min}℃")
        if pop is not None:
            st.write(f"降水確率: {pop}%")
        st.write(f"降水量: {precipitation} mm")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('---')
else:
    st.warning("天気データが取得できませんでした。")
