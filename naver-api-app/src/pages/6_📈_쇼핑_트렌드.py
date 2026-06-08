import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px
import sys
import os

# 상위 경로를 임포트 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

st.title("📈 쇼핑 키워드 클릭 트렌드 분석")
st.markdown("네이버 쇼핑인사이트 API를 활용하여 특정 카테고리 내 쇼핑 검색어의 상대적 클릭 추이를 분석합니다.")

# API 인증 검증
app.check_api_keys()

# 네이버 쇼핑 대표 카테고리 목록
CATEGORY_MAP = {
    "패션의류 (50000000)": "50000000",
    "패션잡화 (50000001)": "50000001",
    "화장품/미용 (50000002)": "50000002",
    "디지털/가전 (50000003)": "50000003",
    "가구/인테리어 (50000004)": "50000004",
    "출산/육아 (50000005)": "50000005",
    "식품 (50000006)": "50000006",
    "스포츠/레저 (50000007)": "50000007",
    "생활/건강 (50000008)": "50000008",
    "여가/생활편의 (50000009)": "50000009",
    "면세점 (50000010)": "50000010",
    "도서 (50005542)": "50005542"
}

# UI 구성
with st.form("shopping_trend_form"):
    st.subheader("🔍 쇼핑 트렌드 조회 조건")
    
    # 카테고리 선택
    selected_category_name = st.selectbox(
        "쇼핑 분야 카테고리 선택",
        options=list(CATEGORY_MAP.keys()),
        index=3  # 기본값: 디지털/가전
    )
    category_id = CATEGORY_MAP[selected_category_name]
    
    # 키워드 입력
    keywords_input = st.text_input(
        "쇼핑 검색어 입력 (쉼표 ','로 구분하여 최대 5개 입력)",
        value="에어팟, 버즈, 헤드폰",
        placeholder="예: 텐트, 타프, 캠핑의자"
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # 기간 선택
        today = datetime.date.today()
        start_date = st.date_input("시작일", today - datetime.timedelta(days=180))
        end_date = st.date_input("종료일", today)
    with col2:
        # 시간 단위
        time_unit = st.selectbox(
            "구간 단위",
            options=["일간 (date)", "주간 (week)", "월간 (month)"],
            index=0
        )
        time_unit_val = time_unit.split(" ")[1].replace("(", "").replace(")", "")
    with col3:
        # 기기 필터
        device = st.selectbox(
            "기기 구분",
            options=["전체 기기", "PC", "모바일 (Mobile)"]
        )
        device_val = ""
        if "PC" in device:
            device_val = "pc"
        elif "모바일" in device:
            device_val = "mo"

    # 추가 고급 필터 (성별 및 연령대)
    with st.expander("⚙️ 고급 필터 (성별 및 연령)"):
        gender = st.selectbox(
            "성별 필터",
            options=["전체 성별", "남성", "여성"]
        )
        gender_val = ""
        if gender == "남성":
            gender_val = "m"
        elif gender == "여성":
            gender_val = "f"
            
        ages = st.multiselect(
            "연령대 필터 (다중 선택 가능, 미선택 시 전체)",
            options=["10", "20", "30", "40", "50", "60"]
        )

    submit_button = st.form_submit_button("쇼핑 트렌드 분석 시작")

if submit_button:
    # 키워드 전처리
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    if not keywords:
        st.error("⚠️ 쇼핑 검색어를 최소 1개 이상 입력해주세요.")
        st.stop()
    if len(keywords) > 5:
        st.warning("⚠️ 최대 5개 검색어까지만 조회가 가능합니다. 상위 5개 검색어만 분석합니다.")
        keywords = keywords[:5]
        
    if start_date > end_date:
        st.error("⚠️ 시작일이 종료일보다 늦을 수 없습니다.")
        st.stop()

    # API 요청 바디 구성 (keywords 사양에 맞춤)
    keyword_param_list = []
    for kw in keywords:
        keyword_param_list.append({
            "name": kw,
            "param": [kw]
        })
        
    payload = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": time_unit_val,
        "category": category_id,
        "keyword": keyword_param_list
    }
    
    if device_val:
        payload["device"] = device_val
    if gender_val:
        payload["gender"] = gender_val
    if ages:
        payload["ages"] = ages

    # API 호출
    api_url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    headers = app.get_headers()
    
    with st.spinner("쇼핑인사이트 트렌드 데이터를 조회 중입니다..."):
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result_data = response.json()
                
                # 데이터 변환 및 가공
                df_list = []
                for group in result_data.get("results", []):
                    title = group.get("title")
                    group_data = group.get("data", [])
                    
                    if group_data:
                        temp_df = pd.DataFrame(group_data)
                        temp_df = temp_df.rename(columns={"ratio": title})
                        temp_df = temp_df[["period", title]]
                        df_list.append(temp_df)
                
                if not df_list:
                    st.info("💡 조회된 쇼핑 클릭 트렌드 데이터가 없습니다. 카테고리나 검색어를 조정해 보세요.")
                else:
                    # 데이터프레임 병합
                    final_df = df_list[0]
                    for next_df in df_list[1:]:
                        final_df = pd.merge(final_df, next_df, on="period", how="outer")
                    
                    final_df = final_df.sort_values("period").reset_index(drop=True)
                    final_df = final_df.fillna(0)
                    
                    # 시각화 데이터 구조 재구성
                    plot_df = final_df.melt(id_vars=["period"], var_name="쇼핑검색어", value_name="상대클릭량")
                    
                    st.success("쇼핑 트렌드 데이터를 성공적으로 수집했습니다!")
                    
                    # 시각화
                    st.subheader("📈 기간별 쇼핑 클릭 트렌드")
                    st.caption("선택한 카테고리 내에서 키워드들의 가장 높은 클릭 시점을 100으로 기준한 상대적 수치입니다.")
                    
                    fig = px.line(
                        plot_df,
                        x="period",
                        y="상대클릭량",
                        color="쇼핑검색어",
                        labels={"period": "기간", "상대클릭량": "클릭 비율 (%)"},
                        title=f"{selected_category_name} 카테고리 키워드 쇼핑 트렌드 비교",
                        markers=True if time_unit_val == "month" else False
                    )
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 요약 정보 및 데이터프레임
                    st.subheader("📋 쇼핑 키워드 클릭 요약")
                    summary_data = []
                    for kw in keywords:
                        if kw in final_df.columns:
                            summary_data.append({
                                "쇼핑검색어": kw,
                                "평균 클릭 비율": round(final_df[kw].mean(), 2),
                                "최대 클릭 비율": final_df[kw].max(),
                                "최소 클릭 비율": final_df[kw].min()
                            })
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                    st.subheader("📄 상세 쇼핑 트렌드 데이터")
                    st.dataframe(final_df, use_container_width=True)
                    
                    # CSV 다운로드
                    csv = final_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 쇼핑 트렌드 데이터 다운로드 (CSV)",
                        data=csv,
                        file_name=f"naver_shopping_trend_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
            else:
                st.error(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
                error_info = response.json()
                st.json(error_info)
                
        except Exception as e:
            st.error(f"❌ 데이터 처리 중 오류가 발생했습니다: {str(e)}")
