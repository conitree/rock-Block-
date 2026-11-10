
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="우산 챙겨!",
    page_icon="☂️",
    layout="wide"
)

st.title("☂️ 우산 챙겨!")
st.caption("오늘 날씨를 확인하고 외출을 준비해요.")

# -----------------------------
# 전국 지역 목록
# -----------------------------
REGIONS = {
    "서울특별시": [
        "종로구", "중구", "용산구", "성동구", "광진구",
        "동대문구", "중랑구", "성북구", "강북구", "도봉구",
        "노원구", "은평구", "서대문구", "마포구", "양천구",
        "강서구", "구로구", "금천구", "영등포구", "동작구",
        "관악구", "서초구", "강남구", "송파구", "강동구"
    ],
    "부산광역시": [
        "중구", "서구", "동구", "영도구", "부산진구",
        "동래구", "남구", "북구", "해운대구", "사하구",
        "금정구", "강서구", "연제구", "수영구", "사상구", "기장군"
    ],
    "대구광역시": [
        "중구", "동구", "서구", "남구", "북구",
        "수성구", "달서구", "달성군", "군위군"
    ],
    "인천광역시": [
        "중구", "동구", "미추홀구", "연수구", "남동구",
        "부평구", "계양구", "서구", "강화군", "옹진군"
    ],
    "광주광역시": ["동구", "서구", "남구", "북구", "광산구"],
    "대전광역시": ["동구", "중구", "서구", "유성구", "대덕구"],
    "울산광역시": ["중구", "남구", "동구", "북구", "울주군"],
    "세종특별자치시": ["세종시"],
    "경기도": [
        "수원시", "성남시", "의정부시", "안양시", "부천시",
        "광명시", "평택시", "동두천시", "안산시", "고양시",
        "과천시", "구리시", "남양주시", "오산시", "시흥시",
        "군포시", "의왕시", "하남시", "용인시", "파주시",
        "이천시", "안성시", "김포시", "화성시", "광주시",
        "양주시", "포천시", "여주시", "연천군", "가평군", "양평군"
    ],
    "강원특별자치도": [
        "춘천시", "원주시", "강릉시", "동해시", "태백시",
        "속초시", "삼척시", "홍천군", "횡성군", "영월군",
        "평창군", "정선군", "철원군", "화천군", "양구군",
        "인제군", "고성군", "양양군
    ],
    "충청북도": [
        "청주시", "충주시", "제천시", "보은군", "옥천군",
        "영동군", "증평군", "진천군", "괴산군", "음성군", "단양군"
    ],
    "충청남도": [
        "천안시", "공주시", "보령시", "아산시", "서산시",
        "논산시", "계룡시", "당진시", "금산군", "부여군",
        "서천군", "청양군", "홍성군", "예산군", "태안군"
    ],
    "전북특별자치도": [
        "전주시", "군산시", "익산시", "정읍시", "남원시",
        "김제시", "완주군", "진안군", "무주군", "장수군",
        "임실군", "순창군", "고창군", "부안군"
    ],
    "전라남도": [
        "목포시", "여수시", "순천시", "나주시", "광양시",
        "담양군", "곡성군", "구례군", "고흥군", "보성군",
        "화순군", "장흥군", "강진군", "해남군", "영암군",
        "무안군", "함평군", "영광군", "장성군", "완도군",
        "진도군", "신안군"
    ],
    "경상북도": [
        "포항시", "경주시", "김천시", "안동시", "구미시",
        "영주시", "영천시", "상주시", "문경시", "경산시",
        "의성군", "청송군", "영양군", "영덕군", "청도군",
        "고령군", "성주군", "칠곡군", "예천군", "봉화군",
        "울진군", "울릉군"
    ],
    "경상남도": [
        "창원시", "진주시", "통영시", "사천시", "김해시",
        "밀양시", "거제시", "양산시", "의령군", "함안군",
        "창녕군", "고성군", "남해군", "하동군", "산청군",
        "함양군", "거창군", "합천군"
    ],
    "제주특별자치도": ["제주시", "서귀포시"]
}

# -----------------------------
# 날씨 코드 설명
# -----------------------------
WEATHER_CODES = {
    0: "맑음 ☀️",
    1: "대체로 맑음 🌤️",
    2: "부분적으로 흐림 ⛅",
    3: "흐림 ☁️",
    45: "안개 🌫️",
    48: "안개 🌫️",
    51: "약한 이슬비 🌦️",
    53: "이슬비 🌦️",
    55: "강한 이슬비 🌧️",
    61: "약한 비 🌧️",
    63: "비 🌧️",
    65: "강한 비 ☔",
    71: "약한 눈 🌨️",
    73: "눈 ❄️",
    75: "강한 눈 ❄️",
    80: "소나기 🌦️",
    81: "소나기 🌧️",
    82: "강한 소나기 ⛈️",
    95: "뇌우 ⛈️",
    96: "우박을 동반한 뇌우 ⛈️",
    99: "강한 뇌우 ⛈️"
}

def weather_text(code):
    return WEATHER_CODES.get(int(code), "날씨 정보 확인 중")

# -----------------------------
# 지역 검색
# -----------------------------
@st.cache_data(ttl=86400)
def search_city(region, city):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    # 지역명을 함께 검색해 동명이인 지역 혼동 줄이기
    params = {
        "name": f"{city} {region}",
        "count": 20,
        "language": "ko",
        "format": "json",
        "countryCode": "KR"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        # 지역명이 포함된 검색이 안 되면 시·군·구 이름으로 재검색
        params["name"] = city
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        results = response.json().get("results", [])

    if not results:
        return None

    # 광역 지역명이 검색 결과의 행정구역 정보에 있는지 우선 확인
    region_clean = region.replace("특별자치도", "").replace(
        "특별시", ""
    ).replace("광역시", "").replace("도", "")

    for item in results:
        admin1 = item.get("admin1", "")
        admin2 = item.get("admin2", "")
        location_text = admin1 + admin2

        if region_clean in location_text or region in location_text:
            return item

    # 일치 항목이 없으면 첫 번째 국내 검색 결과 사용
    return results[0]


# -----------------------------
# 날씨 정보 가져오기
# -----------------------------
@st.cache_data(ttl=1800)
def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "rain,showers,snowfall,weather_code,wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,apparent_temperature,"
            "precipitation_probability,precipitation,"
            "weather_code"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,precipitation_sum"
        ),
        "timezone": "Asia/Seoul",
        "forecast_days": 2
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


# -----------------------------
# 지역 선택 화면
# -----------------------------
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
        REGIONS[selected_region]
    )

st.write(f"선택한 지역: **{selected_region} {selected_city}**")

# -----------------------------
# 날씨 표시
# -----------------------------
if st.button("🌤️ 날씨 확인하기", type="primary"):
    try:
        with st.spinner("날씨 정보를 가져오는 중이에요..."):
            place = search_city(selected_region, selected_city)

            if place is None:
                st.error("지역 좌표를 찾을 수 없습니다.")
                st.stop()

            latitude = place["latitude"]
            longitude = place["longitude"]

            weather = get_weather(latitude, longitude)

        current = weather["current"]
        daily = weather["daily"]
        hourly = weather["hourly"]

        st.divider()
        st.header(f"🌍 {selected_region} {selected_city} 날씨")

        # 현재 날씨
        temperature = current["temperature_2m"]
        feels_like = current["apparent_temperature"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        current_code = current["weather_code"]

        st.subheader("현재 날씨")

        st.title(f"{temperature}°C")
        st.write(weather_text(current_code))
        st.caption(f"체감 온도 {feels_like}°C")

        a, b, c = st.columns(3)

        a.metric("습도", f"{humidity}%")
        b.metric("바람", f"{wind} km/h")
        c.metric("강수량", f"{current['precipitation']} mm")

        # 오늘 예보
        st.divider()
        st.subheader("📅 오늘의 날씨")

        today_high = daily["temperature_2m_max"][0]
        today_low = daily["temperature_2m_min"][0]
        today_rain = daily["precipitation_probability_max"][0]
        today_code = daily["weather_code"][0]
        today_rain_amount = daily["precipitation_sum"][0]

        x, y, z = st.columns(3)

        x.metric("최고 기온", f"{today_high}°C")
        y.metric("최저 기온", f"{today_low}°C")
        z.metric(
            "최대 강수 확률",
            f"{today_rain if today_rain is not None else 0}%"
        )

        st.write(weather_text(today_code))
        st.write(f"예상 강수량: {today_rain_amount} mm")

        # 우산 추천
        st.divider()
        st.subheader("☂️ 우산 챙기기")

        rain_probability = today_rain or 0

        if rain_probability >= 60:
            st.error("비가 올 가능성이 높아요! 우산을 꼭 챙기세요.")
        elif rain_probability >= 30:
            st.warning("비가 올 수 있어요. 작은 우산을 챙기면 좋아요.")
        else:
            st.success("비가 올 가능성이 낮아요. 그래도 날씨를 확인하세요.")

        # 옷차림 추천
        st.divider()
        st.subheader("👕 오늘의 옷차림 추천")

        if temperature < 0:
            clothes = "두꺼운 패딩, 목도리, 장갑 등 따뜻한 옷을 준비하세요."
        elif temperature < 7:
            clothes = "겨울 외투와 따뜻한 옷을 추천해요."
        elif temperature < 12:
            clothes = "코트나 두꺼운 재킷을 추천해요."
        elif temperature < 17:
            clothes = "가벼운 재킷이나 카디건을 챙기세요."
        elif temperature < 23:
            clothes = "긴팔이나 얇은 겉옷이 좋아요."
        elif temperature < 28:
            clothes = "반팔이나 얇고 편안한 옷을 추천해요."
        else:
            clothes = "시원한 옷을 입고 햇빛을 가릴 수 있는 모자를 챙기세요."

        st.info(clothes)

        # 시간대별 예보
        st.divider()
        st.subheader("🕒 시간대별 날씨")

        hourly_df = pd.DataFrame({
            "시간": hourly["time"],
            "기온(°C)": hourly["temperature_2m"],
            "체감온도(°C)": hourly["apparent_temperature"],
            "강수확률(%)": hourly["precipitation_probability"],
            "강수량(mm)": hourly["precipitation"]
        })

        today_date = datetime.now().strftime("%Y-%m-%d")
        hourly_df = hourly_df[
            hourly_df["시간"].str.startswith(today_date)
        ].copy()

        hourly_df["시간"] = pd.to_datetime(
            hourly_df["시간"]
        ).dt.strftime("%H:%M")

        st.line_chart(
            hourly_df.set_index("시간")[["기온(°C)", "체감온도(°C)"]]
        )

        st.dataframe(
            hourly_df,
            use_container_width=True,
            hide_index=True
        )

        # 내일 날씨
        st.divider()
        st.subheader("🌈 내일의 날씨")

        tomorrow_high = daily["temperature_2m_max"][1]
        tomorrow_low = daily["temperature_2m_min"][1]
        tomorrow_rain = daily["precipitation_probability_max"][1]
        tomorrow_code = daily["weather_code"][1]

        p, q, r = st.columns(3)

        p.metric("최고 기온", f"{tomorrow_high}°C")
        q.metric("최저 기온", f"{tomorrow_low}°C")
        r.metric(
            "강수 확률",
            f"{tomorrow_rain if tomorrow_rain is not None else 0}%"
        )

        st.write(weather_text(tomorrow_code))

        st.success("오늘도 안전하고 즐거운 외출 되세요! 😊")

    except requests.exceptions.RequestException:
        st.error("날씨 서버에 연결하지 못했어요. 잠시 후 다시 시도해 주세요.")
    except (KeyError, IndexError, TypeError, ValueError) as error:
        st.error(f"날씨 데이터 처리 중 문제가 발생했어요: {error}")
    except Exception as error:
        st.error(f"오류가 발생했어요: {error}")

# -----------------------------
# 하단 안내
# -----------------------------
st.divider()
st.caption(
    "날씨 정보 제공: Open-Meteo | "
    "기상청 공식 예보와 차이가 있을 수 있습니다."
)
