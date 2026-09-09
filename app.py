import streamlit as st
import time
from google import genai
from google.genai import types
from PIL import Image

# =========================================================
# 🔑 GEMINI API KEY
# =========================================================
api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=api_key,
    vertexai=False
)

# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="아이 약 3초 한눈 요약",
    page_icon="👶",
    layout="centered"
)

# =========================================================
# 이미지 압축
# =========================================================
def compress_image(image, max_size=(768, 768)):
    img = image.copy()
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    if img.mode != "RGB":
        img = img.convert("RGB")

    return img

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

/* =====================================================
   전체 배경 - 노란색 계열
   ===================================================== */
html, body {
    overflow-x: hidden !important;
}

.stApp {
    background: linear-gradient(
        180deg,
        #FFD54A 0%,
        #FFC531 55%,
        #FFB300 100%
    ) !important;
    min-height: 100vh;
}

/* =====================================================
   전체 메인 영역 - 배경 없이 노란 바탕 그대로 비침
   ===================================================== */
.block-container {
    max-width: 900px !important;
    background: transparent !important;
    border: none !important;
    padding: 2rem 1.6rem 1.4rem 1.6rem !important;
    margin-top: 1rem !important;
    margin-bottom: 1rem !important;
    box-shadow: none !important;
}

/* =====================================================
   기본 Streamlit 영역 투명화
   ===================================================== */
.element-container,
.stMarkdown {
    background-color: transparent !important;
    box-shadow: none !important;
}

/* ★ 단락(요소) 간 간격 전반적으로 좁힘 */
.element-container {
    margin-bottom: 0.2rem !important;
}

/* =====================================================
   💊 큰 알약 아이콘
   ===================================================== */
.pill-icon {
    text-align: center;
    font-size: 10rem;
    line-height: 1;
    margin-top: 100px;
    margin-bottom: 0px;
    filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
}

/* =====================================================
   제목 - "아프지마" (두꺼운 굴림 볼드체, 더 크게, 아래로)
   ===================================================== */
h1 {
    color: #1A1A1A !important;
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', 'Gulim', sans-serif !important;
    text-align: center;
    font-weight: 900 !important;
    font-size: 10.2rem !important;
    letter-spacing: -2px;
    margin-top: 20px !important;
    margin-bottom: 8px !important;
    line-height: 1.1 !important;
    -webkit-text-stroke: 1.5px #1A1A1A;
    text-shadow: none !important;
}

/* =====================================================
   설명 문구 - 작은 정보성 텍스트
   ===================================================== */
.stCaption,
[data-testid="stCaptionContainer"] {
    text-align: center !important;
    color: #3A2E00 !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    line-height: 1.6 !important;
    margin-bottom: 8px !important;
}

/* =====================================================
   📦 업로드+나이입력을 감싸는 흰색 박스 (검은 테두리)
   st.container(border=True) 로 생성된 래퍼
   ===================================================== */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border: 8px solid #000000 !important;
    border-radius: 22px !important;
    padding: 14px !important;
    margin-top: 14px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.15) !important;
}

/* =====================================================
   📸 사진 업로드 영역 - 흰 박스 안에 자연스럽게
   ===================================================== */
div[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin-top: 2px !important;
    margin-bottom: 6px !important;
    box-shadow: none !important;
}

div[data-testid="stFileUploader"] section {
    background: transparent !important;
    border: none !important;
    border-radius: 15px !important;
    box-shadow: none !important;
}

div[data-testid="stFileUploader"] section > div {
    background: transparent !important;
    border-color: transparent !important;
}

div[data-testid="stFileUploader"] label {
    color: #000000 !important;
    font-weight: 800 !important;
}

/* ★ 입체감/그림자 제거 - 평평한 버튼 */
div[data-testid="stFileUploader"] button {
    border-radius: 10px !important;
    border: 1.5px solid #000000 !important;
    color: #000000 !important;
    font-weight: 700 !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
    transform: none !important;
}

div[data-testid="stFileUploader"] button:hover {
    background: #F5F5F5 !important;
    box-shadow: none !important;
    transform: none !important;
}

div[data-testid="stFileUploader"] button:active {
    background: #EAEAEA !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ★ 업로드 영역 안의 모든 텍스트(영어/기호 포함)를 검은색으로 통일 */
div[data-testid="stFileUploader"] * {
    color: #000000 !important;
}

/* =====================================================
   🗓️ 나이 입력 영역 - 강제 적용
   ★ 실제 DOM 구조 확인 결과:
     stNumberInput(라벨+박스 전체) > label, > (wrapper) > stNumberInputContainer(실제 박스)
     사진 업로드처럼 "라벨은 밖, 박스만 테두리"가 되도록
     stNumberInputContainer에만 테두리를 적용함
   ===================================================== */
div[data-testid="stNumberInput"] {
    margin-top: 2px !important;
    margin-bottom: 8px !important;
}

/* NumberInput 라벨 (박스 밖) */
div[data-testid="stNumberInput"] label {
    color: #000000 !important;
    font-weight: 800 !important;
}

/* 실제 입력창+버튼을 감싸는 박스 - 음영 제거, 폭 절반으로 축소 */
div[data-testid="stNumberInputContainer"] {
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 6px 0 6px 0 !important;
    box-shadow: none !important;
    width: 50% !important;
}

/* ★ 숫자 입력창 안쪽 파란 테두리 제거 - 바깥 검은 테두리 하나만 보이게 */
div[data-testid="stNumberInput"] input {
    border: none !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
    color: #17536C !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}

/* 숫자 입력창 focus - 테두리 없이 은은한 그림자만 */
div[data-testid="stNumberInput"] input:focus {
    border: none !important;
    box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.15) !important;
}

/* 숫자 +/- 버튼 영역 - 음영 제거 */
div[data-testid="stNumberInput"] button {
    background: transparent !important;
    border-color: transparent !important;
    color: #000000 !important;
}

/* ★ 숫자 입력 영역 안의 모든 텍스트(숫자/기호 포함)를 검은색으로 통일 */
div[data-testid="stNumberInputContainer"] * {
    color: #000000 !important;
}

/* =====================================================
   분석 버튼
   ===================================================== */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #35BCEB 0%, #147FB2 100%) !important;
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 1.15rem !important;
    border-radius: 17px !important;
    border: none !important;
    padding: 15px 0px !important;
    box-shadow:
        0 6px 16px rgba(20, 127, 178, 0.30),
        inset 0 1px 0 rgba(255,255,255,0.35) !important;
    margin-top: 8px !important;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    background: linear-gradient(135deg, #42C5F0 0%, #106F9F 100%) !important;
    border-color: #0F668F !important;
    box-shadow: 0 9px 22px rgba(20, 127, 178, 0.35) !important;
}

div.stButton > button:active {
    transform: translateY(0px);
}

/* =====================================================
   업로드된 이미지
   ===================================================== */
[data-testid="stImage"] {
    background: #F5FCFF !important;
    border: none !important;
    border-radius: 20px !important;
    padding: 12px !important;
    margin-top: 15px !important;
    box-shadow: 0 5px 16px rgba(44, 145, 185, 0.10) !important;
}

/* =====================================================
   분석 결과 제목
   ===================================================== */
h2 {
    color: #000000 !important;
    font-weight: 800 !important;
    font-size: 1.35rem !important;
    background: #E9F8FF !important;
    border: none !important;
    border-radius: 17px !important;
    padding: 13px 17px !important;
    margin-top: 25px !important;
    margin-bottom: 12px !important;
}

/* =====================================================
   분석 결과 카드
   ===================================================== */
div[data-testid="stAlert"] {
    border-radius: 18px !important;
    border: none !important;
    background: #F8FDFF !important;
    box-shadow: 0 5px 16px rgba(44, 145, 185, 0.10) !important;
    color: #000000 !important;
}

div[data-testid="stAlert"] p {
    line-height: 1.75 !important;
    color: #294D60 !important;
}

[data-testid="stMarkdownContainer"] strong {
    color: #126A9C;
    font-weight: 800;
}

[data-testid="stMarkdownContainer"] h3 {
    color: #126A9C !important;
    font-weight: 800 !important;
    border-bottom: 1px solid #D4EEF8;
    padding-bottom: 7px;
    margin-top: 15px;
}

/* =====================================================
   구분선
   ===================================================== */
hr {
    border: none !important;
    height: 2px !important;
    background: #D2EFF9 !important;
    margin: 25px 0 !important;
}

/* =====================================================
   로딩 애니메이션
   ===================================================== */
.loading-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 14px 0 18px 0;
    font-size: 1rem;
    font-weight: 700;
    color: #3C7188;
    background: #F3FBFE;
    border: none;
    border-radius: 14px;
    padding: 10px 15px;
}

.loading-icon {
    display: inline-block;
    animation: loading-spin 1.2s linear infinite;
    transform-origin: center;
}

@keyframes loading-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* =====================================================
   오류 메시지
   ===================================================== */
[data-testid="stException"] {
    border-radius: 15px;
}

/* =====================================================
   하단 푸터
   ===================================================== */
.footer-text {
    text-align: center;
    color: #000000;
    font-size: 0.82rem;
    line-height: 1.7;
    margin-top: 18px;
    padding: 18px;
    background: transparent;
    border: none;
    border-radius: 17px;
}

/* =====================================================
   모바일
   ===================================================== */
@media (max-width: 600px) {
    .block-container {
        margin: 8px !important;
        padding: 1.2rem 0.8rem 1.2rem 0.8rem !important;
    }

    .pill-icon {
        font-size: 5rem !important;
    }

    h1 {
        font-size: 16vw !important;
        letter-spacing: -1px !important;
    }

    div.stButton > button {
        height: 55px;
        font-size: 1.05rem !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-width: 6px !important;
        padding: 10px !important;
    }

    div[data-testid="stFileUploader"] {
        padding: 6px !important;
    }

    div[data-testid="stNumberInputContainer"] {
        width: 65% !important;
    }

    h2 {
        font-size: 1.2rem !important;
    }
}

/* =====================================================
   전체적인 둥근 모서리
   ===================================================== */
button,
input,
textarea,
[data-baseweb="select"] {
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 로딩 문구 표시 함수
# =========================================================
def show_loading(text):
    st.markdown(
        f"""
        <div class="loading-status">
            <span>{text}</span>
            <span class="loading-icon">⏳</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# 메인
# =========================================================

# ★ 큰 알약 아이콘
st.markdown(
    "<div class='pill-icon'>💊</div>",
    unsafe_allow_html=True
)

st.title("약먹어")

# ★ 흰 박스(검은 테두리) 안에 업로드 + 나이 입력을 함께 배치
with st.container(border=True):

    uploaded_file = st.file_uploader(
        "📸 약 봉지 또는 처방전 사진을 올려주세요",
        type=["jpg", "jpeg", "png"]
    )

    age = st.number_input(
        "🗓️ 아이 만 나이 (세)",
        min_value=0,
        max_value=12,
        value=3,
        step=1
    )

st.write("")

# =========================================================
# 분석 버튼
# =========================================================
if uploaded_file and st.button(
    "✨ 3초 만에 분석하기",
    use_container_width=True
):

    raw_image = Image.open(uploaded_file)

    st.image(
        raw_image,
        caption="업로드된 약 사진",
        use_container_width=True
    )

    compressed_img = compress_image(raw_image)

    prompt = f"""
너는 소아 처방전과 약 봉투 사진을 읽고,
만 {age}세 아이의 부모가 이해하기 쉽게 핵심만 알려주는 AI입니다.

사진을 먼저 정확하게 읽고, 확인된 정보만 사용하세요.

[1. 사진 확인]
사진이 약 봉투, 처방전, 약병 또는 약 관련 안내문인지 먼저 확인하세요.

약 관련 사진이 아니라면 다른 설명 없이 아래 문장만 출력하세요.

⚠️ 올바른 약 봉지나 처방전 사진을 올려주세요.

[2. 약 정보 읽기]

약 관련 사진이라면 사진에 실제로 보이는 내용을 기준으로 다음 정보를 확인하세요.

* 약 이름
* 약의 성분명(사진에서 확인할 수 있을 때만)
* 약의 형태(시럽, 가루약, 알약, 연고 등)
* 처방된 복용량
* 복용 횟수
* 복용 시점
* 처방전이나 약 봉투에 적힌 주의사항

여러 약이 있다면 약마다 정보를 구분해서 확인하세요.

사진에서 글자가 흐리거나 약 이름을 확실하게 읽을 수 없다면
절대 추측하지 말고 "확인이 필요합니다"라고 표시하세요.

[3. 아이 나이 고려]

대상 아이는 만 {age}세입니다.

아이의 나이를 고려하여 부모가 알아야 할 주의사항을 알려주세요.

단, 사진에 없는 용량이나 복용 횟수를 임의로 계산하거나 변경하지 마세요.

나이만을 근거로 특정 부작용이 반드시 발생한다고 단정하지 마세요.
약품 정보에서 확인할 수 있는 일반적인 주의사항만 간단히 알려주세요.

[4. 해열제 확인]

처방된 약 중 해열진통제가 있는지 확인하세요.

특히 다음 성분을 확인하세요.

* 아세트아미노펜
* 이부프로펜
* 덱시부프로펜

해열제가 확인되면:

* 약 이름
* 성분
* 해열진통제 여부
* 다른 해열제와 함께 사용할 때 주의할 점
  을 간단히 알려주세요.

해열제가 없으면 다음 문장을 출력하세요.

※ 본 처방전/약에는 해열제가 포함되어 있지 않습니다.

중요:
교차 복용의 구체적인 시간이나 용량을 임의로 계산하지 마세요.
처방전이나 의사·약사의 지시가 우선입니다.

[5. 최종 답변 형식]

💊 약별 한눈 요약

각 약마다 아래 형식으로 짧게 작성하세요.

### 약 이름

* 무엇을 위한 약인지:
* 어떻게 먹는지:
* 꼭 알아둘 주의사항:
* 만 {age}세 아이에게 특히 알아둘 점:
* 약 이름 마다 설명이 끝난 마지막부분에
  해당 나이에 일어날수있는 부작용 알려줘. 예를들어 설사나, 어지러움,구토, 환각, 성격변화
  이런것들 있잖아. 내가 예를들어 설명한거지 저거를 그대로 쓰지는마.
  진짜 해당나이에 이약을 먹으면 일어날수있는 부작용을 너가 찾아서 알려달라는거야.
  내가 예시 한거를 그대로 쓰라는 소리가 아냐. 그러고 한글로만 알려줘.

사진에서 확인되지 않는 내용은
"확인이 필요합니다"라고 표시하세요.

약이 여러 개라면 첫 번째 약의 정보를 모두 설명한 후
두 번째 약으로 넘어가세요.

[🚨 오늘 꼭 기억할 주의사항]

가장 중요한 내용만 최대 2줄로 작성하세요.

[🌡️ 해열제 체크]

해열제가 있다면 핵심만 간단히 설명하세요.

해열제가 없다면:

※ 본 처방전/약에는 해열제가 포함되어 있지 않습니다.

[💡 약 먹이는 실전 팁]

약의 형태와 사진에서 확인되는 특성을 고려하여
부모가 바로 활용할 수 있는 팁을 1줄만 작성하세요.

[안전 규칙]

1. 사진에서 확인되지 않는 약 이름을 추측하지 마세요.
2. 확인되지 않는 성분을 추측하지 마세요.
3. 처방된 용량이나 횟수를 임의로 계산하거나 변경하지 마세요.
4. 불확실한 정보는 "확인이 필요합니다"라고 표시하세요.
5. 사진에 없는 의학적 정보를 사실처럼 만들어내지 마세요.
6. 의사 또는 약사의 처방을 대신하지 마세요.
7. 답변은 부모가 빠르게 읽을 수 있도록 짧고 명확하게 작성하세요.
    """

    status_text = st.empty()

    with status_text.container():
        show_loading("📷 사진 확인 중...")

    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash"
    ]

    result_text = None
    last_error = None

    for model_index, model_name in enumerate(models):

        try:

            status_text.empty()

            with status_text.container():
                show_loading("💊 약 이름 읽는 중...")

            stream = client.models.generate_content_stream(
                model=model_name,
                contents=[
                    prompt,
                    compressed_img
                ],
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level="low"
                    )
                )
            )

            result_parts = []
            first_chunk_received = False

            for chunk in stream:

                chunk_text = chunk.text

                if not chunk_text:
                    continue

                if not first_chunk_received:
                    status_text.empty()

                    with status_text.container():
                        show_loading("🔎 복용 정보 확인 중...")

                    first_chunk_received = True

                result_parts.append(chunk_text)

            result_text = "".join(result_parts).strip()

            status_text.empty()

            with status_text.container():
                show_loading("✅ 거의 완료됐어요")

            time.sleep(0.7)

            status_text.empty()

            break

        except Exception as e:

            error_text = str(e)
            last_error = error_text

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            ):

                if model_index < len(models) - 1:

                    status_text.empty()

                    with status_text.container():
                        show_loading("💊 약 이름 읽는 중...")

                    time.sleep(1)

                    continue

                else:

                    status_text.empty()

                    st.error(
                        "현재 Gemini 서버가 혼잡합니다. "
                        "잠시 후 다시 시도해주세요."
                    )

                    st.code(error_text, language="text")

                    break

            elif (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                if model_index < len(models) - 1:

                    status_text.empty()

                    with status_text.container():
                        show_loading("💊 약 이름 읽는 중...")

                    time.sleep(1)

                    continue

                else:

                    status_text.empty()

                    st.error(
                        "현재 Gemini API 사용량 한도를 초과했습니다. "
                        "잠시 후 다시 시도해주세요."
                    )

                    st.code(error_text, language="text")

                    break

            elif "401" in error_text:

                status_text.empty()

                st.error("🔑 Gemini API 인증에 실패했습니다.")

                st.code(error_text, language="text")

                break

            else:

                status_text.empty()

                st.error("Gemini API 호출 중 오류가 발생했습니다.")

                st.code(error_text, language="text")

                break

    if result_text:

        st.write("")

        st.subheader("📋 분석 결과")

        if "⚠️ 올바른 약 봉지" in result_text:
            st.warning(result_text)
        else:
            st.info(result_text)

# =========================================================
# 하단
# =========================================================
st.markdown("""
<div class='footer-text'>
<b>정보제공 : YDM (대표: 여다윤)</b>
<br>
본 서비스는 참고용이며
의사/약사의 지시가 우선합니다.
</div>
""", unsafe_allow_html=True)