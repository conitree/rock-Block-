
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================
# 1. 기본 설정
# =====================================

st.set_page_config(
    page_title="날씨 알리미",
    page_icon="🌤️",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #2878C8;
}
.sub-title {
    color: #777;
    font-size: 16px;
}
div[data-testid="stMetric"] {
    background-color: rgba(120,160,210,0.10);
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# =====================================
# 2. 지역 목록 및 좌표
# =====================================

REGIONS = {
    "서울특별시": {
        "종로구": (37.5729, 126.9794),
        "강남구": (37.5172, 127.0473),
        "마포구": (37.5663, 126.9019),
        "송파구": (37.5145, 127.1059),
    },
    "부산광역시": {
        "중구": (35.1062, 129.0323),
        "해운대구": (35.1631, 129.1635),
        "부산진구": (35.1629, 129.0530),
    },
    "대구광역시": {
        "중구": (35.8694, 128.6062),
        "수성구": (35.8582, 128.6306),
    },
    "인천광역시": {
        "중구": (37.4738, 126.6219),
        "연수구": (37.4102, 126.6783),
        "남동구": (37.4473, 126.7314),
    },
    "광주광역시": {
        "동구": (35.1460, 126.9231),
        "서구": (35.1520, 126.8895),
    },
    "대전광역시": {
        "서구": (36.3554, 127.3835),
        "유성구": (36.3622, 127.3561),
    },
    "울산광역시": {
        "남구": (35.5438, 129.3301),
        "중구": (35.5695, 129.3320),
    },
    "세종특별자치시": {
        "세종시": (36.4800, 127.2890),
    },
    "경기도": {
        "수원시": (37.2636, 127.0286),
        "성남시": (37.4200, 127.1265),
        "용인시": (37.2411, 127.1776),
        "고양시": (37.6584, 126.8320),
        "부천시": (37.5034, 126.7660),
        "안양시": (37.3943, 126.9568),
        "화성시": (37.1995, 126.8312),
        "평택시": (36.9921, 127.1129),
        "파주시": (37.7600, 126.7800),
        "남양주시": (37.6360, 127.2165),
        "의정부시": (37.7381, 127.0337),
        "광명시": (37.4786, 126.8644),
    },
    "강원특별자치도": {
        "춘천시": (37.8813, 127.7298),
        "원주시": (37.3422, 127.9202),
        "강릉시": (37.7519, 128.8761),
        "속초시": (38.2070, 128.5918),
        "동해시": (37.5247, 129.1143),
        "양양군": (38.0754, 128.6190),
    },
    "충청북도": {
        "청주시": (36.6424, 127.4890),
        "충주시": (36.9910, 127.9259),
        "제천시": (37.1326, 128.1910),
    },
    "충청남도": {
        "천안시": (36.8151, 127.1139),
        "아산시": (36.7898, 127.0018),
        "공주시": (36.4465, 127.1190),
        "서산시": (36.7848, 126.4503),
    },
    "전북특별자치도": {
        "전주시": (35.8242, 127.1480),
        "군산시": (35.9676, 126.7369),
        "익산시": (35.9483, 126.9577),
        "남원시": (35.4164, 127.3904),
    },
    "전라남도": {
        "목포시": (34.8118, 126.3922),
        "여수시": (34.7604, 127.6622),
        "순천시": (34.9506, 127.4872),
        "나주시": (35.0160, 126.7108),
    },
    "경상북도": {
        "포항시": (36.0190, 129.3435),
        "경주시": (35.8562, 129.2247),
        "구미시": (36.1195, 128.3446),
        "안동시": (36.5684, 128.7294),
    },
    "경상남도": {
        "창원시": (35.2281, 128.6811),
        "김해시": (35.2285, 128.8894),
        "진주시": (35.1798, 128.1076),
        "거제시": (34.8806, 128.6211),
        "통영시": (34.8544, 128.4330),
    },
    "제주특별자치도": {
        "제주시": (33.4996, 126.5312),
        "서귀포시": (33.2541, 126.5601),
    }
}


# =====================================
# 3. 날씨 코드
# =====================================

WEATHER_CODES = {
    0: "맑음",
    1: "대체로 맑음",
    2: "구름 조금",
    3: "흐림",
    45: "안개",
    48: "짙은 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    77: "싸락눈",
    80: "소나기",
    81: "소나기",
    82: "강한 소나기",
    85: "눈 소나기",
    86: "강한 눈 소나기",
    95: "천둥번개",
    96: "우박 동반 뇌우",
    99: "강한 뇌우"
}

SNOW_CODES = [71, 73, 75, 77, 85, 86]

WEATHER_ICONS = {
    "맑음": "☀️",
    "대체로 맑음": "🌤️",
    "구름 조금": "⛅",
    "흐림": "☁️",
    "안개": "🌫️",
    "짙은 안개": "🌫️",
    "약한 이슬비": "🌦️",
    "이슬비": "🌦️",
    "강한 이슬비": "🌧️",
    "약한 비": "🌦️",
    "비": "🌧️",
    "강한 비": "🌧️",
    "약한 눈": "🌨️",
    "눈": "❄️",
    "강한 눈": "❄️",
    "싸락눈": "🌨️",
    "소나기": "🌦️",
    "강한 소나기": "⛈️",
    "눈 소나기": "🌨️",
    "강한 눈 소나기": "❄️",
    "천둥번개": "⛈️",
    "우박 동반 뇌우": "⛈️",
    "강한 뇌우": "⛈️"
}


# =====================================
# 4. API 데이터 가져오기
# =====================================

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "snowfall,weather_code,wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,apparent_temperature,"
            "precipitation_probability,precipitation,"
            "snowfall,snowfall_probability,weather_code"
        ),
        "daily": (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_probability_max,"
            "precipitation_sum,snowfall_sum"
        ),
        "timezone": "Asia/Seoul",
        "forecast_days": 2
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=600)
def get_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "pm10,pm2_5",
        "timezone": "Asia/Seoul"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


# =====================================
# 5. 보조 함수
# =====================================

def number(value, default=0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def air_grade(value, kind):
    if value is None:
        return "정보 없음"

    if kind == "pm10":
        if value <= 30:
            return "좋음 😊"
        elif value <= 80:
            return "보통 🙂"
        elif value <= 150:
            return "나쁨 😷"
        else:
            return "매우 나쁨 🚨"

    else:
        if value <= 15:
            return "좋음 😊"
        elif value <= 35:
            return "보통 🙂"
        elif value <= 75:
            return "나쁨 😷"
        else:
            return "매우 나쁨 🚨"


def calculate_score(temp, rain, snow, wind, pm10, pm25):
    score = 100
    reasons = []

    if rain >= 80:
        score -= 25
        reasons.append("비가 올 가능성이 높아요.")
    elif rain >= 50:
        score -= 15
        reasons.append("비가 올 수 있어요.")

    if snow > 0:
        score -= 20
        reasons.append("눈 예보가 있어요.")

    if temp >= 33:
        score -= 20
        reasons.append("매우 더운 날씨예요.")
    elif temp >= 30:
        score -= 10
        reasons.append("더위에 주의하세요.")
    elif temp <= -10:
        score -= 20
        reasons.append("매우 추운 날씨예요.")
    elif temp <= 0:
        score -= 10
        reasons.append("추운 날씨예요.")

    if wind >= 40:
        score -= 15
        reasons.append("바람이 매우 강해요.")
    elif wind >= 25:
        score -= 8
        reasons.append("바람이 다소 강해요.")

    if pm10 is not None and pm10 > 150:
        score -= 15
        reasons.append("미세먼지가 매우 나빠요.")
    elif pm10 is not None and pm10 > 80:
        score -= 8
        reasons.append("미세먼지가 나빠요.")

    if pm25 is not None and pm25 > 75:
        score -= 15
        reasons.append("초미세먼지가 매우 나빠요.")
    elif pm25 is not None and pm25 > 35:
        score -= 8
        reasons.append("초미세먼지가 나빠요.")

    score = max(0, min(100, score))

    if score >= 80:
        message = "외출하기 좋은 날이에요! 😊"
    elif score >= 60:
        message = "외출할 만하지만 준비가 필요해요."
    elif score >= 40:
        message = "외출 전 날씨를 확인하세요."
    else:
        message = "실내 활동도 고려해 보세요."

    if not reasons:
        reasons.append("특별히 주의할 날씨 요소가 적어요.")

    return score, message, reasons


# =====================================
# 6. 앱 제목
# =====================================

st.markdown(
    '<div class="main-title">🌤️ 날씨 알리미</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '오늘 날씨부터 외출 준비물까지 한 번에 확인하세요!'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =====================================
# 7. 지역 선택
# =====================================

st.subheader("📍 지역 선택")

col1, col2 = st.columns(2)

with col1:
    selected_region = st.selectbox(
        "시·도",
        list(REGIONS.keys())
    )

with col2:
    selected_city = st.selectbox(
        "시·군·구",
        list(REGIONS[selected_region].keys())
    )

latitude, longitude = REGIONS[selected_region][selected_city]

st.caption(f"선택 지역: {selected_region} {selected_city}")

if st.button("🔄 날씨 새로고침"):
    get_weather.clear()
    get_air_quality.clear()


# =====================================
# 8. 날씨 데이터 불러오기
# =====================================

try:
    data = get_weather(latitude, longitude)

except requests.exceptions.RequestException:
    st.error("날씨 정보를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.")
    st.stop()

current = data["current"]
hourly = data["hourly"]
daily = data["daily"]

temp = number(current.get("temperature_2m"))
feels_like = number(current.get("apparent_temperature"))
humidity = number(current.get("relative_humidity_2m"))
wind = number(current.get("wind_speed_10m"))
rain_now = number(current.get("precipitation"))
weather_code = int(number(current.get("weather_code")))

weather_text = WEATHER_CODES.get(weather_code, "날씨 정보")
weather_icon = WEATHER_ICONS.get(weather_text, "🌤️")


# =====================================
# 9. 대기질 데이터
# =====================================

pm10 = None
pm25 = None

try:
    air_data = get_air_quality(latitude, longitude)
    air = air_data["current"]

    pm10 = air.get("pm10")
    pm25 = air.get("pm2_5")

except (requests.exceptions.RequestException, KeyError, TypeError):
    st.warning("대기질 정보를 불러오지 못했어요. 날씨 정보는 계속 확인할 수 있어요.")


# =====================================
# 10. 오늘 남은 시간 데이터
# =====================================

now = datetime.now(ZoneInfo("Asia/Seoul"))
today = now.strftime("%Y-%m-%d")

today_hours = [
    i for i, t in enumerate(hourly["time"])
    if t.startswith(today) and int(t[11:13]) >= now.hour
]

rain_values = [
    number(hourly["precipitation_probability"][i])
    for i in today_hours
    if hourly["precipitation_probability"][i] is not None
]

snow_values = [
    number(hourly["snowfall"][i])
    for i in today_hours
    if hourly["snowfall"][i] is not None
]

snow_prob_values = [
    number(hourly["snowfall_probability"][i])
    for i in today_hours
    if hourly["snowfall_probability"][i] is not None
]

rain_probability = max(rain_values) if rain_values else 0
snow_amount = max(snow_values) if snow_values else 0
snow_probability = max(snow_prob_values) if snow_prob_values else 0

# 시간별 눈 날씨 코드 확인
snow_expected = any(
    int(number(hourly["weather_code"][i])) in SNOW_CODES
    for i in today_hours
)


# =====================================
# 11. 현재 날씨
# =====================================

st.divider()
st.subheader(f"📅 {selected_city} 현재 날씨")

st.markdown(f"## {weather_icon} {weather_text}")

a, b, c = st.columns(3)

with a:
    st.metric("현재 기온", f"{temp:.1f}°C")

with b:
    st.metric("체감 온도", f"{feels_like:.1f}°C")

with c:
    st.metric("습도", f"{humidity:.0f}%")

st.caption(
    f"풍속 {wind:.1f} km/h · 현재 강수량 {rain_now:.1f} mm"
)


# =====================================
# 12. 미세먼지 및 초미세먼지
# =====================================

st.divider()
st.subheader("🌫️ 미세먼지 정보")

air1, air2 = st.columns(2)

with air1:
    st.markdown("### 미세먼지 (PM10)")

    if pm10 is not None:
        st.metric("농도", f"{pm10:.1f} μg/m³")
        st.write("상태:", air_grade(pm10, "pm10"))
    else:
        st.write("대기질 정보 없음")

with air2:
    st.markdown("### 초미세먼지 (PM2.5)")

    if pm25 is not None:
        st.metric("농도", f"{pm25:.1f} μg/m³")
        st.write("상태:", air_grade(pm25, "pm25"))
    else:
        st.write("대기질 정보 없음")


# =====================================
# 13. 오늘의 날씨 알림
# =====================================

st.divider()
st.subheader("🚨 오늘의 날씨 알림")

alerts = []

if rain_probability >= 50:
    alerts.append(
        ("☔ 비 알림", f"오늘 비가 올 가능성이 있어요. 강수확률 최대 {rain_probability:.0f}%예요.")
    )

if snow_expected or snow_amount > 0 or snow_probability >= 50:
    alerts.append(
        ("❄️ 눈 알림", "눈이 내릴 가능성이 있어요. 미끄러운 길에 주의하세요.")
    )

if temp >= 33 or feels_like >= 35:
    alerts.append(
        ("🥵 폭염 주의", "오늘은 너무 더워요! 물을 챙기고 더운 시간에는 쉬어 주세요.")
    )
elif temp >= 30 or feels_like >= 32:
    alerts.append(
        ("☀️ 더위 주의", "오늘은 더운 날씨예요. 시원한 옷차림을 추천해요.")
    )

if temp <= -10 or feels_like <= -12:
    alerts.append(
        ("🥶 한파 주의", "오늘은 매우 추워요! 따뜻하게 입으세요.")
    )
elif temp <= 0 or feels_like <= -2:
    alerts.append(
        ("🧣 추위 주의", "기온이 낮아요. 따뜻한 겉옷을 준비하세요.")
    )

if wind >= 40:
    alerts.append(
        ("💨 강풍 주의", "바람이 매우 강하게 불 수 있어요.")
    )
elif wind >= 25:
    alerts.append(
        ("🍃 바람 주의", "바람이 다소 강해요.")
    )

if pm10 is not None and pm10 > 80:
    alerts.append(
        ("😷 미세먼지 주의", "미세먼지 농도가 나빠요. 대기질을 확인하고 외출하세요.")
    )

if pm25 is not None and pm25 > 35:
    alerts.append(
        ("😷 초미세먼지 주의", "초미세먼지 농도가 나빠요. 야외 활동에 주의하세요.")
    )

if alerts:
    for title, message in alerts:
        st.warning(f"**{title}**\n\n{message}")
else:
    st.success("현재 확인된 특별한 날씨 주의 알림이 없어요!")


# =====================================
# 14. 외출 점수
# =====================================

st.divider()
st.subheader("⭐ 오늘의 외출 점수")

score, score_message, reasons = calculate_score(
    temp,
    rain_probability,
    snow_amount,
    wind,
    pm10,
    pm25
)

score_col1, score_col2 = st.columns([1, 2])

with score_col1:
    st.markdown(
        f"""
        <div style="font-size:48px;font-weight:800;color:#2878C8;">
            {score}<span style="font-size:20px;">/100</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with score_col2:
    st.markdown(f"### {score_message}")
    st.progress(score / 100)

st.write("**점수에 반영된 날씨 요소**")

for reason in reasons:
    st.write(f"• {reason}")

st.caption(
    "※ 외출 점수는 날씨 요소를 이용한 앱 자체 참고 점수이며 공식 기상 등급이 아닙니다."
)


# =====================================
# 15. 시간대별 예보
# =====================================

st.divider()
st.subheader("🕒 시간대별 날씨")

if today_hours:
    rows = []

    for i in today_hours:
        rows.append({
            "시간": hourly["time"][i][11:16],
            "기온(°C)": hourly["temperature_2m"][i],
            "강수확률(%)": hourly["precipitation_probability"][i],
            "눈(㎝)": hourly["snowfall"][i],
            "날씨": WEATHER_CODES.get(
                int(number(hourly["weather_code"][i])),
                "정보 없음"
            )
        })

    hourly_df = pd.DataFrame(rows)

    st.line_chart(
        hourly_df.set_index("시간")[["강수확률(%)"]]
    )

    st.dataframe(
        hourly_df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("오늘 남은 시간의 예보가 없어요.")


# =====================================
# 16. 외출 준비물
# =====================================

st.divider()
st.subheader("🎒 오늘의 외출 준비물")

items = []

if rain_probability >= 40:
    items.append("☂️ 우산")

if snow_expected or snow_amount > 0:
    items.append("🥾 미끄럼에 주의할 신발")

if temp <= 10:
    items.append("🧥 따뜻한 겉옷")
elif temp <= 18:
    items.append("🧥 가벼운 겉옷")

if temp >= 28 or feels_like >= 30:
    items.append("🧢 모자")
    items.append("💧 물")

if wind >= 25:
    items.append("🧣 바람을 막아줄 옷")

if pm10 is not None and pm10 > 80:
    items.append("😷 마스크")

if pm25 is not None and pm25 > 35:
    if "😷 마스크" not in items:
        items.append("😷 마스크")

if not items:
    items.append("🎒 평소 외출 준비물")

for index, item in enumerate(items):
    st.checkbox(item, key=f"prepare_{index}_{item}")


# =====================================
# 17. 오늘과 내일 비교
# =====================================

st.divider()
st.subheader("🗓️ 오늘과 내일 날씨 비교")

day1, day2 = st.columns(2)

with day1:
    code = int(number(daily["weather_code"][0]))
    text = WEATHER_CODES.get(code, "날씨 정보")
    icon = WEATHER_ICONS.get(text, "🌤️")

    st.markdown(f"### 오늘 {icon}")
    st.write(text)

    st.metric(
        "최고 기온",
        f"{daily['temperature_2m_max'][0]}°C"
    )

    st.metric(
        "최저 기온",
        f"{daily['temperature_2m_min'][0]}°C"
    )

    st.write(
        f"강수확률 최대 {daily['precipitation_probability_max'][0]}%"
    )

    st.write(
        f"예상 적설량 {daily['snowfall_sum'][0]} cm"
    )

with day2:
    code = int(number(daily["weather_code"][1]))
    text = WEATHER_CODES.get(code, "날씨 정보")
    icon = WEATHER_ICONS.get(text, "🌤️")

    st.markdown(f"### 내일 {icon}")
    st.write(text)

    st.metric(
        "최고 기온",
        f"{daily['temperature_2m_max'][1]}°C"
    )

    st.metric(
        "최저 기온",
        f"{daily['temperature_2m_min'][1]}°C"
    )

    st.write(
        f"강수확률 최대 {daily['precipitation_probability_max'][1]}%"
    )

    st.write(
        f"예상 적설량 {daily['snowfall_sum'][1]} cm"
    )


# =====================================
# 18. 하단 안내
# =====================================

st.divider()

st.caption(
    "🌤️ 날씨 알리미 | 날씨 데이터: Open-Meteo"
)

st.caption(
    "날씨 및 대기질 정보는 예측 자료로 실제 관측값과 차이가 날 수 있습니다."
)

st.caption(
    "지역 좌표는 대표 위치이며, 일부 지역만 제공됩니다."
)
