
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================
# 1. 기본 설정
# =====================================

st.set_page_config(
    page_title="우산 챙겨! ☔",
    page_icon="☔",
    layout="wide"
)

TZ = ZoneInfo("Asia/Seoul")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#eaf6ff,#ffffff);
}
.title {
    text-align:center;
    font-size:42px;
    font-weight:900;
    color:#267db8;
}
.subtitle {
    text-align:center;
    color:#6689a5;
    margin-bottom:30px;
}
.weather-box {
    background:white;
    padding:22px;
    border-radius:18px;
    border:1px solid #dcecf8;
    margin:10px 0;
    box-shadow:0 4px 12px rgba(50,100,150,.06);
}
.recommend {
    background:#e8f4ff;
    padding:18px;
    border-radius:14px;
    border-left:5px solid #3999d5;
    margin:10px 0;
    color:#245b80;
}
.alert {
    background:#fff1e7;
    padding:18px;
    border-radius:14px;
    border-left:5px solid #f39b47;
    margin:10px 0;
    color:#80501f;
}
</style>
""", unsafe_allow_html=True)


# =====================================
# 2. 날씨 코드 해석
# =====================================

WEATHER_CODES = {
    0: ("맑음", "☀️"),
    1: ("대체로 맑음", "🌤️"),
    2: ("부분적으로 흐림", "⛅"),
    3: ("흐림", "☁️"),
    45: ("안개", "🌫️"),
    48: ("서리 안개", "🌫️"),
    51: ("약한 이슬비", "🌦️"),
    53: ("이슬비", "🌦️"),
    55: ("강한 이슬비", "🌧️"),
    56: ("어는 이슬비", "🌧️"),
    57: ("강한 어는 이슬비", "🌧️"),
    61: ("약한 비", "🌦️"),
    63: ("비", "🌧️"),
    65: ("강한 비", "🌧️"),
    66: ("어는 비", "🌧️"),
    67: ("강한 어는 비", "🌧️"),
    71: ("약한 눈", "🌨️"),
    73: ("눈", "❄️"),
    75: ("강한 눈", "❄️"),
    77: ("싸락눈", "🌨️"),
    80: ("약한 소나기", "🌦️"),
    81: ("소나기", "🌧️"),
    82: ("강한 소나기", "⛈️"),
    85: ("약한 눈 소나기", "🌨️"),
    86: ("강한 눈 소나기", "❄️"),
    95: ("뇌우", "⛈️"),
    96: ("우박 동반 뇌우", "⛈️"),
    99: ("강한 우박 동반 뇌우", "⛈️")
}


def weather_description(code):
    return WEATHER_CODES.get(
        int(code),
        ("날씨 정보 없음", "🌤️")
    )


# =====================================
# 3. 지역 검색 API
# =====================================

@st.cache_data(ttl=86400)
def search_city(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 10,
        "language": "ko",
        "format": "json",
        "countryCode": "KR"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    return data.get("results", [])


# =====================================
# 4. 날씨 조회 API
# =====================================

@st.cache_data(ttl=1800)
def get_weather(lat, lon):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "is_day,"
            "precipitation,"
            "rain,"
            "showers,"
            "snowfall,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "hourly": (
            "temperature_2m,"
            "apparent_temperature,"
            "precipitation_probability,"
            "precipitation,"
            "rain,"
            "showers,"
            "snowfall,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "apparent_temperature_max,"
            "apparent_temperature_min,"
            "precipitation_sum,"
            "precipitation_probability_max,"
            "sunrise,"
            "sunset,"
            "wind_speed_10m_max"
        ),

        "timezone": "Asia/Seoul",
        "forecast_days": 2
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# =====================================
# 5. 옷차림 추천
# =====================================

def clothes_recommend(min_temp, max_temp, feels):

    tips = []

    if max_temp <= 0:
        tips.append("🧥 매우 추워요. 두꺼운 겨울 외투를 추천해요.")

    elif max_temp <= 5:
        tips.append("🧥 추운 날씨예요. 패딩이나 두꺼운 코트를 챙기세요.")

    elif max_temp <= 10:
        tips.append("🧥 쌀쌀해요. 따뜻한 외투를 입는 것이 좋아요.")

    elif max_temp <= 16:
        tips.append("🧶 선선해요. 가디건이나 재킷을 추천해요.")

    elif max_temp <= 22:
        tips.append("👕 긴팔 옷이나 가벼운 겉옷이 좋아요.")

    elif max_temp <= 27:
        tips.append("🌿 따뜻해요. 얇고 편안한 옷차림을 추천해요.")

    else:
        tips.append("☀️ 더워요. 통풍이 잘되는 얇은 옷을 입으세요.")

    if min_temp <= 10 and max_temp >= 15:
        tips.append("🌡️ 아침과 낮의 기온 차가 커요. 벗기 쉬운 겉옷을 챙기세요.")

    if feels <= 5:
        tips.append("🥶 현재 체감온도가 낮아요. 목도리 등 보온용품을 고려하세요.")

    elif feels >= 30:
        tips.append("🥵 체감온도가 높아요. 시원한 곳에서 쉬고 물을 챙기세요.")

    return tips


# =====================================
# 6. 외출 준비물 추천
# =====================================

def prepare_items(pop, weather_code, max_temp, wind):

    items = []

    # 비
    if pop >= 40 or weather_code in [
        51, 53, 55, 56, 57,
        61, 63, 65, 66, 67,
        80, 81, 82
    ]:
        items.append("☔ 우산")

    # 눈
    if weather_code in [71, 73, 75, 77, 85, 86]:
        items.append("❄️ 따뜻한 외투")

    if max_temp <= 10:
        items.append("🧥 겉옷")

    if max_temp >= 28:
        items.append("💧 물")
        items.append("🧴 자외선 차단제")

    if wind >= 30:
        items.append("🌬️ 바람에 대비할 겉옷")

    if not items:
        items.append("🎒 개인 소지품")

    return items


# =====================================
# 7. 앱 제목
# =====================================

st.markdown(
    '<div class="title">☔ 우산 챙겨!</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '오늘 날씨부터 옷차림까지 똑똑하게!'
    '</div>',
    unsafe_allow_html=True
)

now = datetime.now(TZ)

st.caption(
    f"📅 {now.strftime('%Y년 %m월 %d일')} "
    f" | 🕒 {now.strftime('%H:%M')} 기준"
)


# =====================================
# 8. 지역 선택
# =====================================

st.sidebar.title("📍 지역 설정")

city = st.sidebar.text_input(
    "지역을 입력하세요",
    value="청주시",
    placeholder="예: 청주시, 서울특별시"
)

if st.sidebar.button("지역 검색", use_container_width=True):

    with st.spinner("지역을 찾고 있어요..."):

        try:
            results = search_city(city)

            if results:
                st.session_state["city_results"] = results
            else:
                st.session_state.pop("city_results", None)
                st.sidebar.error("검색 결과가 없어요.")

        except requests.RequestException:
            st.sidebar.error("지역 검색에 실패했어요.")

if "city_results" in st.session_state:

    results = st.session_state["city_results"]

    options = {
        f"{r['name']} / {r.get('admin1', '')}": r
        for r in results
    }

    selected = st.sidebar.selectbox(
        "검색된 지역 선택",
        list(options.keys())
    )

    if st.sidebar.button("이 지역 날씨 보기", use_container_width=True):
        st.session_state["selected_location"] = options[selected]

# 기본 위치: 청주시
if "selected_location" not in st.session_state:
    st.session_state["selected_location"] = {
        "name": "청주시",
        "latitude": 36.6424,
        "longitude": 127.4890,
        "admin1": "충청북도"
    }

location = st.session_state["selected_location"]

if st.sidebar.button("🔄 날씨 새로고침", use_container_width=True):
    get_weather.clear()
    st.rerun()


# =====================================
# 9. 날씨 가져오기
# =====================================

try:
    with st.spinner("날씨 정보를 가져오고 있어요..."):

        data = get_weather(
            location["latitude"],
            location["longitude"]
        )

except requests.RequestException as e:

    st.error("날씨 정보를 가져오지 못했어요.")
    st.caption(str(e))
    st.stop()


current = data["current"]
hourly = data["hourly"]
daily = data["daily"]

# 오늘 날짜 인덱스
today = now.strftime("%Y-%m-%d")

try:
    day_index = daily["time"].index(today)
except ValueError:
    st.error("오늘의 예보 자료를 찾을 수 없어요.")
    st.stop()

min_temp = daily["temperature_2m_min"][day_index]
max_temp = daily["temperature_2m_max"][day_index]

daily_code = daily["weather_code"][day_index]
description, emoji = weather_description(daily_code)

max_pop = daily["precipitation_probability_max"][day_index]
rain_sum = daily["precipitation_sum"][day_index]

current_temp = current["temperature_2m"]
feels = current["apparent_temperature"]
humidity = current["relative_humidity_2m"]
wind = current["wind_speed_10m"]

# 오늘 남은 시간의 강수확률
today_hour_indices = [
    i for i, t in enumerate(hourly["time"])
    if t.startswith(today)
    and t[11:16] >= now.strftime("%H:%M")
]

remaining_pops = [
    hourly["precipitation_probability"][i]
    for i in today_hour_indices
    if hourly["precipitation_probability"][i] is not None
]

remaining_max_pop = (
    max(remaining_pops) if remaining_pops else max_pop
)

# =====================================
# 10. 날씨 대시보드
# =====================================

st.markdown(f"## 📍 {location['name']} 오늘의 날씨")

st.markdown(
    f"""
    <div class="weather-box">
        <div style="text-align:center">
            <div style="font-size:70px">{emoji}</div>
            <div style="font-size:25px;font-weight:800;color:#367fb0">
                {description}
            </div>
            <div style="font-size:48px;font-weight:900;color:#267db8">
                {current_temp:.1f}℃
            </div>
            <div style="color:#708da4">
                체감온도 {feels:.1f}℃
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("최저기온", f"{min_temp}℃")
c2.metric("최고기온", f"{max_temp}℃")
c3.metric("강수확률 최대", f"{max_pop}%")
c4.metric("습도", f"{humidity}%")


# =====================================
# 11. 오늘의 날씨 알림
# =====================================

st.markdown("## 🔔 오늘의 날씨 알림")

if remaining_max_pop >= 60:

    st.markdown(
        '<div class="alert">'
        '🌧️ 오늘 비가 내릴 가능성이 높아요! '
        '외출할 때 우산을 꼭 준비하세요.'
        '</div>',
        unsafe_allow_html=True
    )

elif remaining_max_pop >= 40:

    st.warning(
        "🌦️ 비가 올 가능성이 있어요. "
        "접이식 우산을 챙기는 것을 추천해요."
    )

elif daily_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:

    st.warning("☔ 오늘 강수 현상이 예상돼요. 우산을 준비하세요.")

else:

    st.success("☀️ 오늘 남은 시간의 강수 가능성이 비교적 낮아요.")


# =====================================
# 12. 옷차림 추천
# =====================================

st.markdown("## 👕 오늘의 옷차림 추천")

tips = clothes_recommend(
    min_temp,
    max_temp,
    feels
)

for tip in tips:

    st.markdown(
        f'<div class="recommend">{tip}</div>',
        unsafe_allow_html=True
    )


# =====================================
# 13. 외출 준비물
# =====================================

st.markdown("## 🎒 외출 전 준비물")

items = prepare_items(
    remaining_max_pop,
    daily_code,
    max_temp,
    wind
)

for item in items:
    st.checkbox(item, key=f"item_{item}")


# =====================================
# 14. 시간별 예보
# =====================================

st.markdown("## 🕒 시간별 날씨 예보")

hour_indices = [
    i for i, t in enumerate(hourly["time"])
    if t.startswith(today)
]

hour_indices = [
    i for i in hour_indices
    if hourly["time"][i][11:16] >= now.strftime("%H:%M")
]

forecast_rows = []

for i in hour_indices:

    code = hourly["weather_code"][i]
    desc, icon = weather_description(code)

    forecast_rows.append({
        "시간": hourly["time"][i][11:16],
        "날씨": f"{icon} {desc}",
        "기온(℃)": hourly["temperature_2m"][i],
        "체감온도(℃)": hourly["apparent_temperature"][i],
        "강수확률(%)": hourly["precipitation_probability"][i],
        "강수량(mm)": hourly["precipitation"][i],
        "풍속(km/h)": hourly["wind_speed_10m"][i]
    })

forecast_df = pd.DataFrame(forecast_rows)

st.dataframe(
    forecast_df,
    use_container_width=True,
    hide_index=True
)


# =====================================
# 15. 기온 그래프
# =====================================

st.markdown("## 📈 오늘의 기온 변화")

if forecast_rows:

    chart = forecast_df.set_index("시간")[
        ["기온(℃)", "체감온도(℃)"]
    ]

    st.line_chart(chart)


# =====================================
# 16. 내일 날씨
# =====================================

st.markdown("## 🌅 내일 날씨 미리 보기")

tomorrow_index = min(day_index + 1, len(daily["time"]) - 1)

tomorrow_code = daily["weather_code"][tomorrow_index]
tomorrow_desc, tomorrow_icon = weather_description(tomorrow_code)

t1, t2, t3 = st.columns(3)

t1.metric(
    "내일 날씨",
    f"{tomorrow_icon} {tomorrow_desc}"
)

t2.metric(
    "내일 최저기온",
    f"{daily['temperature_2m_min'][tomorrow_index]}℃"
)

t3.metric(
    "내일 최고기온",
    f"{daily['temperature_2m_max'][tomorrow_index]}℃"
)

st.info(
    f"내일 강수확률 최대 "
    f"{daily['precipitation_probability_max'][tomorrow_index]}% "
    "예보입니다."
)


# =====================================
# 17. 데이터 출처
# =====================================

st.divider()

st.markdown("""
### 💡 이용 안내

- 날씨 정보는 Open-Meteo 예보 데이터를 사용합니다.
- 지역별 날씨는 해당 좌표의 예보를 기준으로 합니다.
- 옷차림은 일반적인 참고 추천이며 개인의 체감 차이가 있을 수 있습니다.
- 강수확률은 실제 비가 반드시 내린다는 의미가 아닙니다.
- 예보는 변경될 수 있으므로 외출 전 최신 정보를 확인하세요.

**Weather data by [Open-Meteo](https://open-meteo.com/)**
""")

st.caption(
    f"마지막 화면 갱신: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S')}"
)
