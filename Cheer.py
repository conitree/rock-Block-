"app.py"

import streamlit as st
from openai import OpenAI

# Streamlit Secrets에서 API Key 가져오기
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

st.set_page_config(
    page_title="칭찬 생성기",
    page_icon="👏"
)

st.title("👏 AI 칭찬 생성기")
st.write("친구의 특징을 입력하면 따뜻한 칭찬을 만들어 줍니다.")

name = st.text_input("칭찬할 사람의 이름")
feature = st.text_area(
    "어떤 점을 칭찬하고 싶나요?",
    placeholder="예: 발표를 열심히 준비했고 친구들을 잘 도와줬어요."
)

if st.button("칭찬 만들기"):
    if not name or not feature:
        st.warning("이름과 칭찬할 내용을 모두 입력해주세요.")
    else:
        prompt = f"""
        다음 학생에게 어울리는 따뜻하고 자연스러운 칭찬을 만들어 주세요.

        이름: {name}
        특징: {feature}

        조건:
        - 학생에게 직접 말하는 것처럼 작성하세요.
        - 2~3문장으로 작성하세요.
        - 진심이 느껴지고 긍정적인 표현을 사용하세요.
        - 과장된 표현은 피하세요.
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

"requirements.txt"

streamlit
openai

Streamlit Cloud Secrets

Streamlit Cloud의 Settings → Secrets에 다음처럼 입력합니다.

OPENAI_API_KEY = "여기에_본인의_API_키"

API 키를 "app.py"에 직접 적지 않고 Secrets에서 불러오기 때문에 코드에 키가 노출되지 않습니다.
