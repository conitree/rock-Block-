
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# -----------------------------
# 기본 설정
# -----------------------------
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
        margin-bottom: 0;
    }
    .sub-title {
        color: #777;
        margin-top: 4px;
    }
    .score {
        font-size: 52px;
        font-weight: 800;
        color: #2878C8;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(120, 160, 210, 0.10);
        padding: 15px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 지역 목록
# 좌표는 각 지역의 대표 위치
# -----------------------------
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
    },
}

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
    80: "소나기",
    81: "소나기",
    82: "강한 소나기",
    95: "천둥번개",
    96: "우박 동반 뇌우",
    99: "강한 뇌우",
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
    "소나기": "🌦️",
    "강한 소나기": "⛈️",
    "천둥번개": "⛈️",
    "우박 동반 뇌우": "⛈️",
    "강한 뇌우": "⛈️",
}


# -----------------------------
# 날씨 데이터 가져오기
# -----------------------------
@st.cache_data(ttl=600)
def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,apparent_temperature,"
            "precipitation_probability,precipitation,weather_code"
        ),
        "daily": (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_probability_max,"
            "precipitation_sum"
        ),
        "timezone": "Asia/Seoul",
        "forecast_days": 2,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


# -----------------------------
# 외출 점수 계산
# -----------------------------
def calculate_score(temp, rain_probability, wind):
    score = 100
    reasons = []

    if rain_probability >= 80:
        score -= 35
        reasons.append("비가 올 가능성이 매우 높아요.")
    elif rain_probability >= 60:
        score -= 25
        reasons.append("비가 올 가능성이 있어요.")
    elif rain_probability >= 40:
        score -= 15
        reasons.append("우산을 챙기는 것이 좋아요.")

    if temp >= 33:
        score -= 20
        reasons.append("더위에 주의하세요.")
    elif temp >= 30:
        score -= 10
        reasons.append("햇볕과 더위에 주의하세요.")
    elif temp <= -10:
        score -= 20
        reasons.append("매우 추운 날씨예요.")
    elif temp <= 0:
        score -= 10
        reasons.append("따뜻한 옷을 준비하세요.")

    if wind >= 40:
        score -= 15
        reasons.append("바람이 강하게 불 수 있어요.")
    elif wind >= 25:
        score -= 8
        reasons.append("바람이 다소 강해요.")

    score = max(0, min(100, score))

    if score >= 80:
        message = "외출하기 좋은 날이에요!"
    elif score >= 60:
        message = "외출할 만하지만 준비가 필요해요."
    elif score >= 40:
        message = "외출 전 날씨를 한 번 더 확인하세요."
    else:
        message = "실내 활동도 고려해 보세요."

    if not reasons:
        reasons.append("특별히 주의할 날씨 요소가 적어요.")

    return score, message, reasons


# -----------------------------
# 화면
# -----------------------------
st.markdown('<p class="main-title">🌤️ 날씨 알리미</p>',
            unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">오늘 외출하기 전에 필요한 정보를 확인해 보세요.</p>',
    unsafe_allow_html=True
)

st.divider()

# 지역 선택
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

st.caption(
    f"선택한 지역: {selected_region} {selected_city}"
)

# 날씨 불러오기
if st.button("🌈 날씨 확인하기", type="primary", use_container_width=True):
    st.cache_data.clear()

try:
    data = get_weather(latitude, longitude)

    current = data["current"]
    hourly = data["hourly"]
    daily = data["daily"]

    temp = current["temperature_2m"]
    feels_like = current["apparent_temperature"]
    humidity = current["relative_humidity_2m"]
    wind = current["wind_speed_10m"]
    weather_code = current["weather_code"]

    weather_text = WEATHER_CODES.get(weather_code, "날씨 정보")
    weather_icon = WEATHER_ICONS.get(weather_text, "🌤️")

    # 오늘의 비 확률
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    today = now.strftime("%Y-%m-%d")

    today_hours = [
        i for i, t in enumerate(hourly["time"])
        if t.startswith(today) and int(t[11:13]) >= now.hour
    ]

    rain_values = [
        hourly["precipitation_probability"][i]
        for i in today_hours
        if hourly["precipitation_probability"][i] is not None
    ]

    current_rain_probability = max(rain_values) if rain_values else 0

    # 외출 점수
    score, score_message, reasons = calculate_score(
        temp,
        current_rain_probability,
        wind
    )

    st.divider()
    st.subheader(f"📅 {selected_city} 오늘의 날씨")

    # 현재 날씨
    a, b, c = st.columns(3)

    with a:
        st.metric("현재 기온", f"{temp:.1f}°C")

    with b:
        st.metric("체감 온도", f"{feels_like:.1f}°C")

    with c:
        st.metric("습도", f"{humidity}%")

    st.markdown(
        f"## {weather_icon} {weather_text}"
    )

    st.caption(
        f"풍속 {wind} km/h · 강수량 {current['precipitation']} mm"
    )

    # 외출 점수
    st.divider()
    st.subheader("⭐ 오늘의 외출 점수")

    score_col1, score_col2 = st.columns([1, 2])

    with score_col1:
        st.markdown(
            f'<div class="score">{score}<span style="font-size:20px;">/100</span></div>',
            unsafe_allow_html=True
        )

    with score_col2:
        st.markdown(f"### {score_message}")
        st.progress(score / 100)

    st.markdown("**점수에 반영된 날씨 정보**")
    for reason in reasons:
        st.write(f"• {reason}")

    st.caption(
        "※ 외출 점수는 기온·강수확률·바람을 이용한 앱 자체 참고 점수이며, "
        "공식 기상 등급은 아닙니다."
    )

    # 시간별 비 예보
    st.divider()
    st.subheader("🌧️ 시간대별 비 예보")

    if today_hours:
        rain_data = []

        for i in today_hours:
            time_label = hourly["time"][i][11:16]
            probability = hourly["precipitation_probability"][i]
            temperature = hourly["temperature_2m"][i]

            rain_data.append({
                "시간": time_label,
                "강수확률(%)": probability,
                "기온(°C)": temperature,
            })

        rain_df = pd.DataFrame(rain_data)

        st.line_chart(
            rain_df.set_index("시간")[["강수확률(%)"]],
            y="강수확률(%)"
        )

        st.dataframe(
            rain_df,
            use_container_width=True,
            hide_index=True
        )

        rainy_hours = [
            row for row in rain_data
            if row["강수확률(%)"] is not None
            and row["강수확률(%)"] >= 50
        ]

        if rainy_hours:
            first_rain = rainy_hours[0]["시간"]
            st.warning(
                f"☔ 오늘 {first_rain} 이후 비가 올 가능성이 있어요. "
                "외출 전 우산을 챙겨 보세요."
            )
        else:
            st.success("오늘은 강수확률이 50% 이상인 시간이 없어요.")

    else:
        st.info("오늘 남은 시간의 시간별 예보가 없어요.")

    # 준비물 체크리스트
    st.divider()
    st.subheader("🎒 오늘의 외출 준비물")

    items = []

    if current_rain_probability >= 40:
        items.append("☂️ 우산")
    if temp <= 10:
        items.append("🧥 따뜻한 겉옷")
    elif temp <= 18:
        items.append("🧥 가벼운 겉옷")
    if temp >= 28:
        items.append("🧢 모자")
        items.append("💧 물")
    if wind >= 25:
        items.append("🧣 바람을 막아줄 옷")

    if not items:
        items.append("🎒 평소 외출 준비물")

    for item in items:
        st.checkbox(item, key=f"check_{item}")

    # 오늘과 내일
    st.divider()
    st.subheader("🗓️ 오늘과 내일 비교")

    day1, day2 = st.columns(2)

    with day1:
        code = daily["weather_code"][0]
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

    with day2:
        code = daily["weather_code"][1]
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

    st.divider()
    st.caption(
        "날씨 데이터 출처: Open-Meteo · 예보는 실제 날씨와 다를 수 있습니다."
    )

except requests.exceptions.RequestException:
    st.error(
        "날씨 정보를 불러오지 못했어요. 잠시 후 다시 시도해 주세요."
    )
except (KeyError, IndexError, TypeError, ValueError):
    st.error(
        "날씨 데이터 형식에 문제가 있어요. 잠시 후 다시 시도해 주세요."
    )
