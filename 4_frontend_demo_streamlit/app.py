import streamlit as st
import requests
import pandas as pd
import time

# 1. 페이지 설정
st.set_page_config(
    page_title="AI Creator Matching Engine (Prototype)",
    page_icon="💄",
    layout="wide"
)

# 2. API URL 설정 (Secrets 우선 사용, 없으면 로컬)
if "API_URL" in st.secrets:
    API_URL = st.secrets["API_URL"]
else:
    API_URL = "http://127.0.0.1:8000"

# 3. 헤더 섹션
st.title("💄 AI Creator Matching Engine (Prototype)")
st.markdown("""
**AI Creator Matching Engine (Prototype) 데모입니다.**
AI가 과거 스폰서십 성과 데이터를 분석하여, 입력된 캠페인 조건에 대한 **예상 ROI**를 예측합니다.
""")

# 4. 사이드바: 캠페인 조건 입력
st.sidebar.header("1. 캠페인 조건 설정")

# 입력 폼
with st.sidebar.form("campaign_form"):
    target_niche = st.selectbox("타겟 니치 (Niche)", ["Beauty", "Fashion", "Lifestyle", "Vlog"])
    target_platform = st.selectbox("플랫폼 (Platform)", ["Instagram", "YouTube", "TikTok"])
    target_followers = st.slider("목표 크리에이터 팔로워 수", 1000, 1000000, 50000)
    budget = st.number_input("캠페인 예산 ($)", min_value=500, value=5000, step=500)
    
    submitted = st.form_submit_button("🚀 AI 분석 실행")

# 5. 메인 화면: 결과 표시
if submitted:
    # API 요청 준비
    payload = {
        "niche": target_niche,
        "platform": target_platform,
        "follower_count": target_followers,
        "budget": budget
    }
    
    # 로딩 애니메이션 (UX)
    with st.spinner("AI가 2,000건의 매칭 데이터를 분석 중입니다..."):
        try:
            # 백엔드 API 호출
            response = requests.post(f"{API_URL}/predict", json=payload)
            time.sleep(1) # (데모용) 분석하는 척 1초 대기
            
            if response.status_code == 200:
                result = response.json()
                ai_data = result['ai_analysis']
                
                # --- 결과 시각화 섹션 ---
                st.success("분석 완료! AI 예측 결과입니다.")
                
                # KPI 지표 (Metrics)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(label="예상 ROI (투자 대비 수익)", value=f"{ai_data['predicted_roi']}x", delta="AI 예측")
                
                with col2:
                    st.metric(label="예상 매출액 (Revenue)", value=f"${ai_data['estimated_revenue']:,}")
                
                with col3:
                    st.metric(label="데이터 신뢰도", value=ai_data['confidence_score'])
                
                # 추가 설명
                st.info(f"""
                💡 **인사이트:**
                선택하신 **{target_platform}** 플랫폼의 **{target_niche}** 카테고리 크리에이터({target_followers:,}명 팔로워)와 매칭 시,
                **${budget:,}** 예산으로 약 **${ai_data['estimated_revenue']:,}**의 매출 효과가 기대됩니다.
                """)
                
                # (선택) 비교 그래프 예시
                st.subheader("📊 예상 성과 비교")
                chart_data = pd.DataFrame({
                    "구분": ["기존 평균 ROI", "AI 매칭 예상 ROI"],
                    "ROI": [4.5, ai_data['predicted_roi']] # 4.5는 가상의 기준값
                })
                st.bar_chart(chart_data.set_index("구분"))
                
            else:
                st.error(f"API 호출 실패: {response.text}")
                
        except Exception as e:
            st.error(f"서버 연결 오류. 백엔드(FastAPI)가 켜져 있나요? \n 에러 메시지: {e}")

else:
    st.info("👈 왼쪽 사이드바에서 캠페인 조건을 설정하고 'AI 분석 실행' 버튼을 눌러주세요.")
