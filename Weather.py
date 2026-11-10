
import streamlit as st
import requests
import pandas as pd
import math
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from geopy.geocoders import Nominatim

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="우산 챙겨! | 날씨 알림",
    page_icon="☔",
    layout="wide",
    initial_sidebar_state="expanded"
)

KST = ZoneInfo("Asia/Seoul")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #edf7ff 0%, #f8fbff 45%, #ffffff 100%);
    }
    .main-title {
        font-size: 38px;
        font-weight: 900;
        color: #2479b9;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #66849e;
        margin-bottom: 25px;
    }
    .weather-card {
        background: white;
        border-radius: 18px;
        padding: 22px;
        border: 1px solid #e0edf7;
        box-shadow: 0 4px 15px rgba(50,100,150,0.06);
        margin-bottom: 12px;
    }
    .weather-card h3 {
        color: #4386b7;
        margin-top: 0;
    }
    .big-temp {
        font-size: 48px;
        font-weight: 800;
        color: #2679b5;
    }
    .recommend-card {
        background: #eaf5ff;
        border-left: 5px solid #4b9bd5;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
        color: #245474;
    }
    .warning-card {
        background: #fff4e7;
        border-left: 5px solid #f3a34b;
        border-radius: 12px;
        padding: 18px;
        margin: 10px 0;
        color: #85531c;
    }
    .small-info {
        color: #71879a;
        font-size: 13px;
    }
    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 14px;
        border: 1px solid #e0edf7;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. 기상청 API 인증키
# ==========================================

def get_api_key():
    try:
        return st.secrets["KMA_SERVICE_KEY"]
    except Exception:
        return os.getenv("KMA_SERVICE_KEY", "")


# ==========================================
# 3. 위도 / 경도 -> 기상청 격자 변환
# ==========================================

def convert_to_grid(lat, lon):
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136

    DEGRAD = math.pi / 180.0

    re = RE / GRID

    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / \
         math.tan(math.pi * 0.25 + slat1 * 0.5)

    sn = math.log(
        math.cos(slat1) / math.cos(slat2)
    ) / math.log(sn)

    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn

    ro = re * sf / math.pow(
        math.tan(math.pi * 0.25 + olat * 0.5), sn
    )

    ra = re * sf / math.pow(
        math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5), sn
    )

    theta = lon * DEGRAD - olon

    if theta > math.pi:
        theta -= 2.0 * math.pi

    if theta < -math.pi:
        theta += 2.0 * math.pi

    theta *= sn

    x = ra * math.sin(theta) + XO + 0.5
    y = ro - ra * math.cos(theta) + YO + 0.5

    return int(x), int(y)


# ==========================================
# 4. 지역 검색
# ==========================================

@st.cache_data(ttl=86400)
def search_location(address):
    geolocator = Nominatim(
        user_agent="umbrella_weather_app_v1"
    )

    result = geolocator.geocode(
        address,
        timeout=10,
        country_codes="kr"
    )

    if result is None:
        return None

    return {
        "lat": result.latitude,
        "lon": result.longitude,
        "name": result.address
    }


# ==========================================
# 5. 기상청 발표시간 계산
# ==========================================

def get_base_times():
    now = datetime.now(KST) - timedelta(minutes=10)

    times = [2, 5, 8, 11, 14, 17, 20, 23]

    candidates = []

    for day_offset in range(2):
        day = now.date() - timedelta(days=day_offset)

        for hour in times:
            base = datetime(
                day.year, day.month, day.day,
                hour, 0, tzinfo=KST
            )

            if base <= now:
                candidates.append(base)

    return sorted(candidates, reverse=True)


# ==========================================
# 6. 기상청 단기예보 API 요청
# ==========================================

@st.cache_data(ttl=1800)
def get_weather(nx, ny, service_key):
    url = (
        "https://apis.data.go.kr/1360000/"
        "VilageFcstInfoService_2.0/getVilageFcst"
    )

    candidates = get_base_times()
    last_error = "예보 데이터를 찾을 수 없습니다."

    for base in candidates[:5]:

        params = {
            "serviceKey": service_key,
            "pageNo": 1,
            "numOfRows": 1000,
            "dataType": "JSON",
            "base_date": base.strftime("%Y%m%d"),
            "base_time": base.strftime("%H%M"),
            "nx": nx,
            "ny": ny
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=20
            )

            response.raise_for_status()
            data = response.json()

            header = data["response"]["header"]

            if str(header.get("resultCode")) != "00":
                last_error = header.get(
                    "resultMsg", "API 오류"
                )
                continue

            items = data["response"]["body"]["items"]["item"]

            if not items:
                continue

            df = pd.DataFrame(items)

            return df, base.strftime("%Y-%m-%d %H:%M")

        except Exception as e:
            last_error = str(e)

    raise RuntimeError(last_error)


# ==========================================
# 7. 날씨 데이터 분석
# ==========================================

def analyze_weather(df):

    today = datetime.now(KST).strftime("%Y%m%d")

    today_df = df[
        df["fcstDate"].astype(str) == today
    ].copy()

    if today_df.empty:
        return None, None, None

    # 시간별 데이터 정리
    pivot = today_df.pivot_table(
        index=["fcstDate", "fcstTime"],
        columns="category",
        values="fcstValue",
        aggfunc="first"
    ).reset_index()

    # 기온
    temperatures = pd.to_numeric(
        pivot.get("TMP", pd.Series(dtype=float)),
        errors="coerce"
    ).dropna()

    min_temp = None
    max_temp = None

    # TMN / TMX가 있으면 우선 사용
    tmn = today_df[today_df["category"] == "TMN"]
    tmx = today_df[today_df["category"] == "TMX"]

    if not tmn.empty:
        min_temp = float(tmn.iloc[0]["fcstValue"])

    if not tmx.empty:
        max_temp = float(tmx.iloc[0]["fcstValue"])

    # 없으면 시간별 기온으로 계산
    if min_temp is None and not temperatures.empty:
        min_temp = float(temperatures.min())

    if max_temp is None and not temperatures.empty:
        max_temp = float(temperatures.max())

    # 강수확률
    pop = pd.to_numeric(
        pivot.get("POP", pd.Series(dtype=float)),
        errors="coerce"
    ).dropna()

    max_pop = float(pop.max()) if not pop.empty else 0

    # 강수형태
    pty_values = pd.to_numeric(
        pivot.get("PTY", pd.Series(dtype=float)),
        errors="coerce"
    ).fillna(0)

    rain_types = {
        0: "강수 없음",
        1: "비",
        2: "비/눈",
        3: "눈",
        4: "소나기",
        5: "빗방울",
        6: "빗방울/눈날림",
        7: "눈날림"
    }

    pty = int(pty_values.max()) if not pty_values.empty else 0

    # 하늘 상태
    sky_values = pd.to_numeric(
        pivot.get("SKY", pd.Series(dtype=float)),
        errors="coerce"
    ).dropna()

    sky = int(sky_values.iloc[0]) if not sky_values.empty else 1

    sky_types = {
        1: "맑음 ☀️",
        3: "구름 많음 ⛅",
        4: "흐림 ☁️"
    }

    if pty != 0:
        weather_text = rain_types.get(pty, "강수")
    else:
        weather_text = sky_types.get(sky, "날씨 정보")

    # 시간별 데이터 표시용
    result = pivot.copy()

    result["시간"] = result["fcstTime"].astype(str).str[:2] + ":00"

    for col in ["TMP", "POP", "WSD"]:
        if col in result.columns:
            result[col] = pd.to_numeric(
                result[col], errors="coerce"
            )

    return {
        "min_temp": min_temp,
        "max_temp": max_temp,
        "max_pop": max_pop,
        "weather_text": weather_text,
        "pty": pty,
        "sky": sky
    }, result, today_df


# ==========================================
# 8. 옷차림 추천
# ==========================================

def recommend_clothes(min_temp, max_temp):

    if min_temp is None or max_temp is None:
        return [
            "🌤️ 기온 정보가 부족해요.",
            "외출 전에 최신 기온을 확인해 주세요."
        ]

    tips = []

    if max_temp <= 0:
        tips.append("🧥 매우 추워요. 두꺼운 겨울 외투와 보온용품을 챙기세요.")

    elif max_temp <= 5:
        tips.append("🧥 추운 날씨예요. 패딩이나 두꺼운 코트를 추천해요.")

    elif max_temp <= 10:
        tips.append("🧥 쌀쌀해요. 따뜻한 외투를 챙겨 입으세요.")

    elif max_temp <= 16:
        tips.append("🧶 선선해요. 가디건이나 얇은 재킷을 추천해요.")

    elif max_temp <= 22:
        tips.append("👕 적당한 날씨예요. 긴팔이나 가벼운 겉옷이 좋아요.")

    elif max_temp <= 27:
        tips.append("🌿 따뜻해요. 얇고 편안한 옷차림을 추천해요.")

    else:
        tips.append("☀️ 더운 날씨예요. 통풍이 잘되는 가벼운 옷을 입으세요.")

    if min_temp <= 10 and max_temp >= 15:
        tips.append("🌡️ 아침과 낮의 기온 차가 커요. 벗고 입기 쉬운 겉옷을 챙기세요.")

    elif max_temp - min_temp >= 10:
        tips.append("🌡️ 일교차가 큰 편이에요. 외출 시간에 따라 옷을 조절하세요.")

    return tips


# ==========================================
# 9. 외출 준비물 추천
# ==========================================

def recommend_items(max_pop, pty, min_temp, max_temp):

    items = []

    if pty in [1, 2, 4, 5, 6]:
        items.append("☔ 우산")
    elif max_pop >= 40:
        items.append("☔ 접이식 우산")

    if min_temp is not None and min_temp <= 10:
        items.append("🧥 겉옷")

    if max_temp is not None and max_temp >= 28:
        items.append("🧴 자외선 차단제")
        items.append("💧 물")

    if max_temp is not None and max_temp >= 25:
        items.append("🧢 모자")

    if not items:
        items.append("🎒 개인 소지품")

    return items


# ==========================================
# 10. 앱 화면
# ==========================================

st.markdown(
    '<div class="main-title">☔ 우산 챙겨!</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '오늘 날씨를 확인하고, 똑똑하게 외출 준비하기'
    '</div>',
    unsafe_allow_html=True
)

now = datetime.now(KST)

st.caption(
    f"📅 {now.strftime('%Y년 %m월 %d일 %A')} | "
    f"🕒 {now.strftime('%H:%M')} 기준"
)

# 사이드바
with st.sidebar:

    st.header("📍 지역 설정")

    address = st.text_input(
        "지역 또는 주소 입력",
        value="서울특별시청",
        placeholder="예: 서울특별시 강남구"
    )

    if st.button("지역 검색", use_container_width=True):

        with st.spinner("지역을 검색하고 있어요..."):

            try:
                location = search_location(address)

                if location:
                    st.session_state["location"] = location
                    st.success("지역을 찾았어요!")
                else:
                    st.error("지역을 찾을 수 없어요.")

            except Exception:
                st.error("지역 검색에 실패했어요. 다시 시도해 주세요.")

    st.divider()

    st.markdown("### 🌤️ 이용 안내")
    st.write("• 기상청 단기예보 사용")
    st.write("• 지역별 날씨 조회")
    st.write("• 기온별 옷차림 추천")
    st.write("• 비 예보에 따른 우산 알림")

    st.divider()

    if st.button("🔄 날씨 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# 초기 위치
if "location" not in st.session_state:
    st.session_state["location"] = {
        "lat": 37.5665,
        "lon": 126.9780,
        "name": "서울특별시청"
    }

location = st.session_state["location"]

# API 인증
service_key = get_api_key()

if not service_key:
    st.error(
        "기상청 API 인증키가 설정되지 않았어요. "
        "Streamlit Secrets에 KMA_SERVICE_KEY를 등록해 주세요."
    )
    st.stop()

# 좌표 변환
nx, ny = convert_to_grid(
    location["lat"],
    location["lon"]
)

st.markdown(
    f"### 📍 {location['name'].split(',')[0]}"
)

# API 호출
try:

    with st.spinner("기상청에서 날씨 정보를 가져오고 있어요..."):

        weather_df, base_time = get_weather(
            nx, ny, service_key
        )

        analysis, hourly, raw_today = analyze_weather(
            weather_df
        )

    if analysis is None:
        st.warning(
            "오늘의 예보 자료가 아직 없거나 오늘 예보가 종료되었어요."
        )
        st.stop()

except Exception as e:

    st.error("날씨 정보를 가져오지 못했어요.")
    st.code(str(e))
    st.info(
        "API 인증키, 인터넷 연결, 지역 좌표 및 기상청 서비스 상태를 확인해 주세요."
    )
    st.stop()


# ==========================================
# 11. 오늘의 날씨
# ==========================================

st.markdown("## 🌤️ 오늘의 날씨")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "오늘의 날씨",
        analysis["weather_text"]
    )

with col2:
    if analysis["min_temp"] is not None:
        st.metric(
            "예상 최저기온",
            f"{analysis['min_temp']:.1f} ℃"
        )
    else:
        st.metric("예상 최저기온", "정보 없음")

with col3:
    if analysis["max_temp"] is not None:
        st.metric(
            "예상 최고기온",
            f"{analysis['max_temp']:.1f} ℃"
        )
    else:
        st.metric("예상 최고기온", "정보 없음")


st.markdown(
    f"""
    <div class="weather-card">
        <h3>☔ 강수 예보</h3>
        <div style="font-size:28px;font-weight:800;color:#4386b7;">
            강수확률 최대 {analysis['max_pop']:.0f}%
        </div>
        <p>오늘 예보 시간대 중 가장 높은 강수확률이에요.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 12. 날씨별 알림
# ==========================================

st.markdown("## 🔔 오늘의 날씨 알림")

if analysis["pty"] in [1, 2, 4, 5, 6]:
    st.warning(
        "☔ 비 또는 강수 현상이 예보되어 있어요. "
        "외출할 때 우산을 챙기세요!"
    )

elif analysis["pty"] in [3, 7]:
    st.warning(
        "❄️ 눈 또는 눈날림이 예보되어 있어요. "
        "따뜻하게 입고 외출하세요."
    )

elif analysis["max_pop"] >= 60:
    st.warning(
        "🌧️ 비가 내릴 가능성이 높아요. "
        "우산을 미리 준비하는 것이 좋아요."
    )

elif analysis["max_pop"] >= 40:
    st.info(
        "🌦️ 비가 올 가능성이 있어요. "
        "접이식 우산을 챙기는 것을 추천해요."
    )

else:
    st.success(
        "🌤️ 현재 확인된 오늘 예보에서는 "
        "뚜렷한 강수 신호가 많지 않아요."
    )


# ==========================================
# 13. 옷차림 추천
# ==========================================

st.markdown("## 👕 오늘의 옷차림 추천")

clothes = recommend_clothes(
    analysis["min_temp"],
    analysis["max_temp"]
)

for tip in clothes:

    st.markdown(
        f'<div class="recommend-card">{tip}</div>',
        unsafe_allow_html=True
    )


# ==========================================
# 14. 외출 준비물
# ==========================================

st.markdown("## 🎒 외출 전 준비물")

items = recommend_items(
    analysis["max_pop"],
    analysis["pty"],
    analysis["min_temp"],
    analysis["max_temp"]
)

for item in items:
    st.checkbox(item, key=f"check_{item}")


# ==========================================
# 15. 시간별 예보
# ==========================================

st.markdown("## 🕒 시간별 날씨 예보")

display = pd.DataFrame()

display["시간"] = hourly["시간"]

if "TMP" in hourly.columns:
    display["기온(℃)"] = hourly["TMP"]

if "POP" in hourly.columns:
    display["강수확률(%)"] = hourly["POP"]

if "WSD" in hourly.columns:
    display["풍속(m/s)"] = hourly["WSD"]

if "SKY" in hourly.columns:
    sky_map = {
        1: "맑음 ☀️",
        3: "구름 많음 ⛅",
        4: "흐림 ☁️"
    }

    display["하늘 상태"] = (
        pd.to_numeric(hourly["SKY"], errors="coerce")
        .map(sky_map)
    )

if "PTY" in hourly.columns:
    pty_map = {
        0: "없음",
        1: "비",
        2: "비/눈",
        3: "눈",
        4: "소나기",
        5: "빗방울",
        6: "빗방울/눈날림",
        7: "눈날림"
    }

    display["강수 형태"] = (
        pd.to_numeric(hourly["PTY"], errors="coerce")
        .map(pty_map)
    )

st.dataframe(
    display,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 16. 기온 그래프
# ==========================================

if "TMP" in hourly.columns:

    st.markdown("## 📈 오늘의 기온 변화")

    chart = hourly[
        ["시간", "TMP"]
    ].dropna().copy()

    chart = chart.set_index("시간")

    chart.columns = ["기온(℃)"]

    st.line_chart(chart, use_container_width=True)


# ==========================================
# 17. 안내 및 출처
# ==========================================

st.divider()

st.markdown("""
### 💡 우산 챙겨! 이용 안내

- 날씨 정보는 기상청 단기예보를 기반으로 합니다.
- 옷차림 추천은 예보 기온을 이용한 일반적인 참고 정보입니다.
- 실제 체감온도는 바람, 습도, 개인차에 따라 달라질 수 있습니다.
- 강수확률은 비가 올 가능성을 의미하며 실제 강수 여부를 보장하지 않습니다.
- 예보 발표 이후 날씨가 달라질 수 있으므로 외출 전 최신 정보를 확인하세요.

**날씨 데이터 출처: 기상청**
""")

st.caption(
    f"예보 발표 기준 시각: {base_time} | "
    "우산 챙겨! Weather App"
)
