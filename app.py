import streamlit as st
import google.generativeai as genai
import requests
import utils
from google.api_core.exceptions import ResourceExhausted

# --- Page Configuration ---
st.set_page_config(
    page_title="진에어 AI 고객센터",
    page_icon="✈️",
    layout="wide"
)

# --- Helper Functions ---
@st.cache_data(show_spinner=False)
def load_faq():
    """FAQ 데이터를 캐싱하여 로드합니다."""
    return utils.get_faq_as_text()

def get_flight_schedule(departure: str, arrival: str, date: str):
    """
    실시간 항공 스케줄을 조회하는 함수입니다.
    
    Args:
        departure: 출발 공항 코드 (예: GMP)
        arrival: 도착 공항 코드 (예: CJU)
        date: 날짜 (형식: YYYYMMDD, 예: 20250618)
    """
    base_url = utils.FLIGHT_API_BASE_URL
    url = f"{base_url}/API/Flight"
    params = {
        'departure': departure,
        'arrival': arrival,
        'date': date,
        'lang': 'ko'
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def send_operation_confirmation(flight_date: str, flight_number: str, email: str):
    """
    운항정보확인서를 이메일로 발송하는 함수입니다.
    
    Args:
        flight_date: 날짜 (형식: YYYYMMDD, 예: 20240703)
        flight_number: 편명 (예: LJ507)
        email: 수신 이메일 주소
    """
    return utils.send_operation_confirmation_api(flight_date, flight_number, email)

def get_pnr_detail(pnr: str):
    """
    예약 번호(6자리)를 사용하여 예약 상세 내역을 조회하는 함수입니다.
    
    Args:
        pnr: 예약 번호 (예: X3AJUP)
    """
    return utils.get_pnr_detail_api(pnr)


# --- Sidebar: Configuration ---
with st.sidebar:
    st.title("설정 (Settings)")
    


    api_key = st.text_input("Google API Key", type="password")
    if not api_key:
        st.warning("API Key를 입력해주세요.")
    
    st.markdown("---")
    st.markdown("👈 관리자 페이지에서 FAQ를 수정할 수 있습니다.")

# --- Main Interface ---
st.title("진에어 AI 고객센터 ✈️")

# Quick Links
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.link_button("📢 공지사항", "https://www.jinair.com/company/announce/announceList", use_container_width=True)
with col2:
    st.link_button("❓ 자주 묻는 질문", "https://www.jinair.com/qna/faq", use_container_width=True)
with col3:
    st.link_button("🎁 진행중인 프로모션", "https://www.jinair.com/promotion/inprogressEvent", use_container_width=True)
with col4:
    if st.button("📄 운항정보 확인서", use_container_width=True):
        st.session_state.show_op_form = not st.session_state.get("show_op_form", False)

if st.session_state.get("show_op_form", False):
    with st.container(border=True):
        st.subheader("운항정보 확인서 발송")
        with st.form("op_form"):
            f_date = st.text_input("탑승일 (YYYYMMDD)", placeholder="20240703")
            f_num = st.text_input("편명 (예: LJ507)", placeholder="LJ507")
            f_email = st.text_input("이메일 주소")
            
            submitted = st.form_submit_button("발송하기")
            if submitted:
                if f_date and f_num and f_email:
                    with st.spinner("발송 중..."):
                        result = utils.send_operation_confirmation_api(f_date, f_num, f_email)
                        # Check if "error" key exists AND is not None/Empty string
                        if result and result.get("error"):
                            st.error(f"발송 실패: {result['error']}")
                        else:
                            st.success("운항정보 확인서가 이메일로 발송되었습니다!")
                            st.session_state.messages.append({"role": "assistant", "content": f"운항정보 확인서를 {f_email}로 발송했습니다. (편명: {f_num}, 날짜: {f_date})"})
                            st.session_state.show_op_form = False
                            st.rerun()
                else:
                    st.warning("모든 정보를 입력해주세요.")




# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Logic ---
if api_key:
    # 1. Configure GenAI
    genai.configure(api_key=api_key)
    
    # 2. Update System Instruction with FAQ from CSV (Cached) and Bot Rules
    faq_content = load_faq()
    rules_content = utils.load_bot_rules()
    
    system_instruction = f"""Role: JinAir Agent. Lang: Korean.
    Instruction: 기본적으로 한국어로 답변하세요. 단, 사용자가 다른 언어로 질문하면 그 언어에 맞춰 답변하세요.
Rules: {rules_content}
FAQ:
{faq_content}
Instr:
1. Source: FAQ only. Else "죄송합니다. 제공된 정보에는 해당 내용이 없습니다." (translated).
2. Flight Query: Use `get_flight_schedule`. Format: "N flights. Fastest: [F] [T]. List: ..." (translated)
3. Operation Confirmation: Ask for Date (YYYYMMDD), Flight Num, and Email. Use `send_operation_confirmation`.
4. PNR Lookup: Ask for 6-char PNR. Use `get_pnr_detail`. Summarize: Flight, Date, Passengers.
5. Be concise. Link URLs.
"""

    # 3. Create Model
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        system_instruction=system_instruction,
        tools=[get_flight_schedule, send_operation_confirmation, get_pnr_detail]
    )

    # 4. Handle User Input
    if prompt := st.chat_input("궁금한 점을 물어보세요!"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                try:
                    # Reconstruct history for API (Limited to save tokens)
                    history_for_api = []
                    # Current message is already in session_state, exclude it for history
                    past_messages = st.session_state.messages[:-1]
                    # Limit to last 6 messages (3 turns) - Extreme Optimization
                    if len(past_messages) > 6:
                        past_messages = past_messages[-6:]
                    
                    for msg in past_messages:
                        role = "user" if msg["role"] == "user" else "model"
                        history_for_api.append({"role": role, "parts": [msg["content"]]})
                    
                    chat = model.start_chat(history=history_for_api, enable_automatic_function_calling=True)
                    response = chat.send_message(prompt)
                    
                    # Log Usage
                    if response.usage_metadata:
                        utils.log_usage(
                            model_name='gemini-2.5-flash',
                            prompt_tokens=response.usage_metadata.prompt_token_count,
                            candidate_tokens=response.usage_metadata.candidates_token_count
                        )
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                except ResourceExhausted:
                    error_msg = "⚠️ API 사용량이 초과되었습니다 (Quota Exceeded). 잠시 후 다시 시도해주세요."
                    st.error(error_msg)
                
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("👈 왼쪽 사이드바에 API Key를 입력하고 대화를 시작하세요.")
