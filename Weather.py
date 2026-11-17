
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="날씨 알리미",
    page_icon="🌤️",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 38px;
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


# ==========================================
# 2. 지역 목록
# ==========================================

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


# ==========================================
# 3. 날씨 코드
# ==========================================

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

SNOW_CODES = [71, 73, 75, 77, 85, 86]


# ==========================================
# 4. 날씨 API
# ==========================================

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,apparent_temperature,"
            "precipitation_probability,precipitation,"
            "snowfall,weather_code"
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


# ==========================================
# 5. 대기질 API
# ==========================================

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


# ==========================================
# 6. 보조 함수
# ==========================================

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
        return "매우 나쁨 🚨"

    if value <= 15:
        return "좋음 😊"
    elif value <= 35:
        return "보통 🙂"
    elif value <= 75:
        return "나쁨 😷"
    return "매우 나쁨 🚨"


# ==========================================
# 7. 외출 점수 계산
# ==========================================

def calculate_score(temp, feels, rain, snow, wind, pm10, pm25):
    score = 100
    reasons = []

    if rain >= 80:
        score -= 25
        reasons.append("비가 올 가능성이 매우 높아요.")
    elif rain >= 50:
        score -= 15
        reasons.append("비가 올 가능성이 있어요.")

    if snow > 0:
        score -= 20
        reasons.append("눈이 예상돼요.")

    if temp >= 33 or feels >= 35:
        score -= 20
        reasons.append("더위에 주의해야 해요.")
    elif temp >= 30 or feels >= 32:
        score -= 10
        reasons.append("다소 더운 날씨예요.")

    if temp <= -10 or feels <= -12:
        score -= 20
        reasons.append("매우 추운 날씨예요.")
    elif temp <= 0 or feels <= -2:
        score -= 10
        reasons.append("추운 날씨예요.")

    if wind >= 40:
        score -= 15
        reasons.append("바람이 매우 강해요.")
    elif wind >= 25:
        score -= 8
        reasons.append("바람이 다소 강해요.")

    if pm10 is not None:
        if pm10 > 150:
            score -= 15
            reasons.append("미세먼지가 매우 나빠요.")
        elif pm10 > 80:
            score -= 8
            reasons.append("미세먼지가 나빠요.")

    if pm25 is not None:
        if pm25 > 75:
            score -= 15
            reasons.append("초미세먼지가 매우 나빠요.")
        elif pm25 > 35:
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


# ==========================================
# 8. 외출 가이드 및 준비물 추천
# ==========================================

def get_outdoor_advice(
    temp, feels, rain, snow, wind, pm10, pm25
):
    advice = []
    preparations = []

    # 미세먼지
    if (
        (pm10 is not None and pm10 > 150)
        or (pm25 is not None and pm25 > 75)
    ):
        advice.append(
            "😷 미세먼지가 매우 나빠요. "
            "가능하면 야외 활동을 줄이고 실내에 머무르는 것을 추천해요."
        )
        preparations.append("보건용 마스크")

    elif (
        (pm10 is not None and pm10 > 80)
        or (pm25 is not None and pm25 > 35)
    ):
        advice.append(
            "🌫️ 공기가 좋지 않아요. "
            "장시간 야외 활동은 피하고 외출할 때 마스크를 챙겨 보세요."
        )
        preparations.append("보건용 마스크")

    # 비
    if rain >= 50:
        advice.append(
            "☔ 비가 올 가능성이 있어요. "
            "우산을 챙기고 외출 시간을 확인하세요."
        )
        preparations.append("우산")

    # 눈
    if snow > 0:
        advice.append(
            "❄️ 눈이 예상돼요. "
            "길이 미끄러울 수 있으니 조심해서 이동하세요."
        )
        preparations.append("미끄럼에 주의할 신발")

    # 더위
    if temp >= 33 or feels >= 35:
        advice.append(
            "🥵 오늘은 너무 더워요! "
            "한낮 야외 활동은 피하고 시원한 실내에서 쉬는 것이 좋아요."
        )
        preparations.extend(["물", "모자"])

    elif temp >= 30 or feels >= 32:
        advice.append(
            "☀️ 더운 날씨예요. "
            "산책은 비교적 시원한 시간대에 하는 것을 추천해요."
        )
        preparations.extend(["물", "모자"])

    # 추위
    if temp <= -10 or feels <= -12:
        advice.append(
            "🥶 매우 추워요. "
            "오래 야외에 있기보다는 따뜻한 실내 활동을 추천해요."
        )
        preparations.append("따뜻한 겉옷")

    elif temp <= 0 or feels <= -2:
        advice.append(
            "🧣 추운 날씨예요. 따뜻하게 입고 외출하세요."
        )
        preparations.append("따뜻한 겉옷")

    # 강풍
    if wind >= 40:
        advice.append(
            "💨 바람이 매우 강해요. "
            "야외 활동을 줄이고 주변 시설물에 주의하세요."
        )

    elif wind >= 25:
        advice.append(
            "🍃 바람이 강한 편이에요. 바람막이를 챙기면 좋아요."
        )
        preparations.append("바람막이")

    # 외출하기 좋은 날인지 판단
    bad_weather = (
        rain >= 50
        or snow > 0
        or temp >= 33
        or feels >= 35
        or temp <= -10
        or feels <= -12
        or wind >= 40
        or (pm10 is not None and pm10 > 80)
        or (pm25 is not None and pm25 > 35)
    )

    if not bad_weather:
        advice.append(
            "🌳 산책하기 좋은 날씨네요! "
            "가벼운 산책이나 야외 활동을 즐겨 보세요."
        )

    if not advice:
        advice.append(
            "🌤️ 외출 전 날씨를 확인하고 즐거운 하루 보내세요!"
        )

    preparations = list(dict.fromkeys(preparations))

    return advice, preparations, bad_weather


# ==========================================
# 9. 앱 제목
# ==========================================

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


# ==========================================
# 10. 지역 선택
# ==========================================

st.subheader("📍 지역 선택")

col1, col2 = st.columns(2)

with col1:
    selected_region = st.selectbox(
        "시·도 선택",
        list(REGIONS.keys())
    )

with col2:
    selected_city = st.selectbox(
        "시·군·구 선택",
        list(REGIONS[selected_region].keys())
    )

latitude, longitude = REGIONS[selected_region][selected_city]

st.caption(f"선택 지역: {selected_region} {selected_city}")

if st.button("🔄 날씨 새로고침"):
    get_weather.clear()
    get_air_quality.clear()


# ==========================================
# 11. 날씨 데이터 불러오기
# ==========================================

try:
    data = get_weather(latitude, longitude)

except requests.exceptions.RequestException:
    st.error("날씨 정보를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.")
    st.stop()

current = data["current"]
hourly = data["hourly"]
daily = data["daily"]

temp = number(current.get("temperature_2m"))
feels = number(current.get("apparent_temperature"))
humidity = number(current.get("relative_humidity_2m"))
wind = number(current.get("wind_speed_10m"))
rain_now = number(current.get("precipitation"))
weather_code = int(number(current.get("weather_code")))

weather_text = WEATHER_CODES.get(weather_code, "날씨 정보")
weather_icon = WEATHER_ICONS.get(weather_text, "🌤️")


# ==========================================
# 12. 대기질 데이터
# ==========================================

pm10 = None
pm25 = None

try:
    air_data = get_air_quality(latitude, longitude)
    air = air_data["current"]

    pm10 = air.get("pm10")
    pm25 = air.get("pm2_5")

except (
    requests.exceptions.RequestException,
    KeyError,
    TypeError
):
    st.warning(
        "대기질 정보를 불러오지 못했어요. "
        "날씨 정보는 계속 확인할 수 있어요."
    )


# ==========================================
# 13. 오늘 남은 시간 계산
# ==========================================

now = datetime.now(ZoneInfo("Asia/Seoul"))
today = now.strftime("%Y-%m-%d")

today_hours = [
    i for i, t in enumerate(hourly["time"])
    if t.startswith(today)
    and int(t[11:13]) >= now.hour
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

rain_probability = max(rain_values) if rain_values else 0
snow_amount = sum(snow_values) if snow_values else 0

snow_expected = any(
    int(number(hourly["weather_code"][i])) in SNOW_CODES
    for i in today_hours
)


# ==========================================
# 14. 현재 날씨
# ==========================================

st.divider()
st.subheader(f"📅 {selected_city} 현재 날씨")

st.markdown(f"## {weather_icon} {weather_text}")

a, b, c = st.columns(3)

with a:
    st.metric("현재 기온", f"{temp:.1f}°C")

with b:
    st.metric("체감 온도", f"{feels:.1f}°C")

with c:
    st.metric("습도", f"{humidity:.0f}%")

st.caption(
    f"풍속 {wind:.1f} km/h · 현재 강수량 {rain_now:.1f} mm"
)


# ==========================================
# 15. 미세먼지와 초미세먼지
# ==========================================

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


# ==========================================
# 16. 오늘의 날씨 알림
# ==========================================

st.divider()
st.subheader("🚨 오늘의 날씨 알림")

alerts = []

if rain_probability >= 50:
    alerts.append(
        f"☔ 비가 올 가능성이 있어요. "
        f"강수확률 최대 {rain_probability:.0f}%예요."
    )

if snow_expected or snow_amount > 0:
    alerts.append(
        "❄️ 눈이 예상돼요. 미끄러운 길에 주의하세요."
    )

if temp >= 33 or feels >= 35:
    alerts.append(
        "🥵 오늘은 너무 더워요! 물을 챙기고 더운 시간에는 쉬어 주세요."
    )
elif temp >= 30 or feels >= 32:
    alerts.append(
        "☀️ 오늘은 더운 날씨예요. 시원한 옷차림을 추천해요."
    )

if temp <= -10 or feels <= -12:
    alerts.append(
        "🥶 오늘은 매우 추워요! 따뜻하게 입으세요."
    )
elif temp <= 0 or feels <= -2:
    alerts.append(
        "🧣 기온이 낮아요. 따뜻한 겉옷을 준비하세요."
    )

if wind >= 40:
    alerts.append(
        "💨 바람이 매우 강해요. 야외 활동에 주의하세요."
    )
elif wind >= 25:
    alerts.append(
        "🍃 바람이 다소 강해요."
    )

if pm10 is not None and pm10 > 80:
    alerts.append(
        "😷 미세먼지 농도가 나빠요. 대기질을 확인하세요."
    )

if pm25 is not None and pm25 > 35:
    alerts.append(
        "😷 초미세먼지 농도가 나빠요. 야외 활동에 주의하세요."
    )

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("현재 확인된 특별한 날씨 주의 알림이 없어요!")


# ==========================================
# 17. 오늘의 외출 가이드
# ==========================================

st.divider()
st.subheader("🏡 오늘의 외출 가이드")

advice_list, preparation_list, bad_weather = get_outdoor_advice(
    temp,
    feels,
    rain_probability,
    snow_amount,
    wind,
    pm10,
    pm25
)

for advice in advice_list:
    st.info(advice)

st.markdown("### 🎒 오늘 챙기면 좋은 것")

if preparation_list:
    for index, item in enumerate(preparation_list):
        st.checkbox(
            item,
            key=f"guide_prepare_{index}"
        )
else:
    st.success("특별히 추가로 챙길 준비물이 없어요!")

st.markdown("### 💡 오늘의 추천 활동")

if bad_weather:
    st.warning(
        "🏠 오늘은 날씨에 주의가 필요해요. "
        "실내 활동을 고려하고 외출한다면 충분히 준비하세요."
    )
else:
    st.success(
        "🌳 산책하기 좋은 날씨네요! "
        "가볍게 산책하거나 야외 활동을 즐겨 보세요."
    )


# ==========================================
# 18. 외출 점수
# ==========================================

st.divider()
st.subheader("⭐ 오늘의 외출 점수")

score, score_message, reasons = calculate_score(
    temp,
    feels,
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
    "※ 외출 점수는 앱 자체 참고 점수이며 공식 기상 등급이 아닙니다."
)


# ==========================================
# 19. 시간대별 날씨
# ==========================================

st.divider()
st.subheader("🕒 시간대별 날씨")

if today_hours:
    rows = []

    for i in today_hours:
        rows.append({
            "시간": hourly["time"][i][11:16],
            "기온(°C)": hourly["temperature_2m"][i],
            "강수확률(%)": hourly["precipitation_probability"][i],
            "강수량(mm)": hourly["precipitation"][i],
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


# ==========================================
# 20. 오늘과 내일 날씨 비교
# ==========================================

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
        f"강수확률 최대 "
        f"{daily['precipitation_probability_max'][0]}%"
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
        f"강수확률 최대 "
        f"{daily['precipitation_probability_max'][1]}%"
    )

    st.write(
        f"예상 적설량 {daily['snowfall_sum'][1]} cm"
    )


# ==========================================
# 21. 하단 안내
# ==========================================

st.divider()

st.caption(
    "🌤️ 날씨 알리미 | 날씨 및 대기질 데이터: Open-Meteo"
)

st.caption(
    "예보 및 대기질 자료는 실제 관측값과 차이가 날 수 있습니다."
)

st.caption(
    "지역 좌표는 대표 위치이며, 현재 일부 지역만 제공됩니다."
)
