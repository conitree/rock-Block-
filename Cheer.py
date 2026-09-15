import streamlit as st
from openai import OpenAI

# OpenAI API 연결
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# 페이지 설정
st.set_page_config(
    page_title="AI 칭찬 생성기",
    page_icon="👏"
)

st.title("👏 AI 칭찬 생성기")
st.write("친구의 장점을 입력하면 AI가 따뜻한 칭찬을 만들어 줍니다.")

# 입력
name = st.text_input("칭찬할 사람의 이름")

feature = st.text_area(
    "칭찬하고 싶은 점",
    placeholder="예: 발표 준비를 열심히 했고 친구들을 잘 도와줬어요."
)

# 버튼
if st.button("✨ 칭찬 만들기"):
    if not name or not feature:
        st.warning("이름과 칭찬하고 싶은 점을 모두 입력해주세요.")
    else:
        prompt = f"""
학생에게 직접 말하는 것처럼 따뜻하고 자연스러운 칭찬을 작성해 주세요.

이름: {name}
칭찬하고 싶은 점: {feature}

조건:
- 2~3문장으로 작성하세요.
- 진심이 느껴지는 긍정적인 표현을 사용하세요.
- 학생이 읽었을 때 기분이 좋아질 수 있도록 작성하세요.
- 지나치게 과장하지 마세요.
"""

        try:
            response = client.responses.create(
                model="gpt-5.4-nano",
                input=prompt
            )

            praise = response.output_text

            st.success("칭찬이 완성됐어요! 🎉")
            st.write(praise)

        except Exception as e:
            st.error("칭찬을 만드는 중 오류가 발생했습니다.")
            st.write(str(e))
