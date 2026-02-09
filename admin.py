import streamlit as st
import pandas as pd
import utils

st.set_page_config(page_title="관리자 페이지", page_icon="🔒", layout="wide")

st.title("관리자 페이지 🔒")

# Simple Password Authentication
password = st.sidebar.text_input("관리자 비밀번호", type="password")

if password == "1234":  # Simple hardcoded password for now
    st.success("로그인 성공!")
    
    # Create Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["API 사용량 (Usage)", "FAQ 데이터 (Data)", "챗봇 행동 지침 (Behavior)", "🔗 연동 API (Connected APIs)"])
    
    with tab1:
        st.header("📊 API 사용량 및 비용 대시보드")
        
        # Load Usage Data
        df = utils.load_usage_data()
        
        if not df.empty:
            # Metrics Calculation
            total_requests = len(df)
            total_prompt_tokens = df['prompt_tokens'].sum()
            total_candidate_tokens = df['candidate_tokens'].sum()
            total_tokens = total_prompt_tokens + total_candidate_tokens
            
            # Cost Estimation (Gemini 2.5 Flash Rate)
            # Input: $0.30 / 1M tokens
            # Output: $2.50 / 1M tokens
            # Note: This is an estimation based on public pricing.
            cost_input = (total_prompt_tokens / 1_000_000) * 0.30
            cost_output = (total_candidate_tokens / 1_000_000) * 2.50
            total_cost = cost_input + cost_output
            
            # Display Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("총 요청 수", f"{total_requests} 회")
            col2.metric("총 토큰 사용량", f"{total_tokens:,.0f} Tokens")
            col3.metric("입력 토큰", f"{total_prompt_tokens:,.0f}")
            col4.metric("출력 토큰", f"{total_candidate_tokens:,.0f}")
            
            st.metric("💰 예상 청구 비용 (Estimated Cost)", f"${total_cost:.6f}")
            st.caption("* 예상 비용은 Gemini 2.5 Flash 기준 근사치입니다. (입력 $0.30/1M, 출력 $2.50/1M)")

            # Chart
            st.subheader("시간대별 토큰 사용량")
            chart_data = df.set_index('timestamp')[['prompt_tokens', 'candidate_tokens']]
            st.line_chart(chart_data)

            st.subheader("상세 로그")
            st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)
            
        else:
            st.info("아직 API 사용 기록이 없습니다.")

    with tab2:
        st.header("FAQ 데이터 관리")
        st.markdown("여기서 챗봇이 사용하는 FAQ 데이터를 직접 수정할 수 있습니다.")

        # Load data
        df = utils.load_faq_data()

        # Data Editor
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="faq_editor"
        )

        # Save Button
        if st.button("저장하기", key="save_faq"):
            utils.save_faq_data(edited_df)
            st.success("데이터가 성공적으로 저장되었습니다! 챗봇에 즉시 반영됩니다.")

    with tab3:
        st.header("🤖 챗봇 행동 지침 (Behavior Guidelines)")
        st.markdown("""
        챗봇의 어투, 성격, 혹은 답변 시 주의사항을 설정할 수 있습니다. 
        여기에 입력하는 내용은 챗봇의 시스템 프롬프트(System Instruction)에 추가됩니다.
        """)

        # Load rules
        current_rules = utils.load_bot_rules()
        
        # Text Area
        new_rules = st.text_area("행동 규칙 입력", value=current_rules, height=300)

        # Save Button
        if st.button("규칙 저장하기", key="save_rules"):
            if utils.save_bot_rules(new_rules):
                st.success("행동 규칙이 저장되었습니다! 챗봇에 즉시 반영됩니다.")
            else:
                st.error("저장 중 오류가 발생했습니다.")

    with tab4:
        st.header("🔗 연동 API 관리")
        st.markdown("현재 챗봇에 연동된 외부 API 정보를 확인하고 연결 상태를 점검할 수 있습니다.")
        
        st.subheader("1. 항공 스케줄 조회 API (Flight Schedule)")
        flight_url = utils.FLIGHT_API_BASE_URL
        st.code(flight_url, language="text")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("연결 테스트", key="test_flight_api"):
                with st.spinner("연결 확인 중..."):
                    success, code_or_err, elapsed = utils.check_api_status(flight_url)
                    
                    if success:
                        st.success(f"연결 성공! (Status: {code_or_err}, Time: {elapsed:.2f}s)")
                    else:
                        st.error(f"연결 실패 (Error: {code_or_err})")
        with col2:
            st.info("💡 이 API는 사용자가 항공권 일정을 문의할 때 호출됩니다.")

        st.divider()

        st.subheader("2. 운항정보 확인서 발송 API (Operation Confirmation)")
        op_url = utils.OPERATION_CONFIRMATION_API_URL
        st.code(op_url, language="text")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("연결 테스트", key="test_op_api"):
                with st.spinner("연결 확인 중..."):
                    # Note: Using POST endpoint with GET might return 405/404, but proves reachability.
                    success, code_or_err, elapsed = utils.check_api_status(op_url)
                    
                    if success:
                        st.success(f"연결 성공! (Status: {code_or_err}, Time: {elapsed:.2f}s)")
                    else:
                        st.error(f"연결 실패 (Error: {code_or_err})")
        with col2:
            st.info("💡 이 API는 사용자가 운항정보 확인서 발송을 요청할 때 호출됩니다.")

        st.divider()

        st.subheader("3. 예약 상세 조회 API (PNR Detail)")
        pnr_url = utils.PNR_DETAIL_API_URL
        st.code(pnr_url, language="text")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("연결 테스트", key="test_pnr_api"):
                with st.spinner("연결 확인 중..."):
                    # Use a dummy PNR or empty to check connectivity
                    # Note: API might return error for invalid PNR, but connection is successful if we get a response
                    success, code_or_err, elapsed = utils.check_api_status(pnr_url)
                    
                    if success:
                        st.success(f"연결 성공! (Status: {code_or_err}, Time: {elapsed:.2f}s)")
                    else:
                        st.error(f"연결 실패 (Error: {code_or_err})")
        with col2:
            st.info("💡 이 API는 사용자가 6자리 예약번호로 예약을 조회할 때 호출됩니다.")
        
else:
    if password:
        st.error("비밀번호가 틀렸습니다.")
    st.info("관리자 비밀번호를 입력해주세요.")
