import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px
import sys
import os

# 상위 경로를 임포트 경로에 추가하여 app.py 모듈 호출 가능케 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

st.title("📊 통합 검색어 트렌드 분석")
st.markdown("네이버 통합검색 내 특정 키워드들의 상대적인 검색량 추이를 비교 분석합니다.")

# API 인증 검증
app.check_api_keys()

# UI 폼 구성
with st.form("trend_form"):
    st.subheader("🔍 검색 조건 설정")
    
    # 키워드 입력
    keywords_input = st.text_input(
        "검색어 입력 (쉼표 ','로 구분하여 최대 5개 입력)",
        value="아이폰, 갤럭시, 픽셀폰",
        placeholder="예: 파이썬, 자바, C++"
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # 기간 선택
        today = datetime.date.today()
        start_date = st.date_input("시작일", today - datetime.timedelta(days=365))
        end_date = st.date_input("종료일", today)
    with col2:
        # 시간 단위
        time_unit = st.selectbox(
            "구간 단위",
            options=["일간 (date)", "주간 (week)", "월간 (month)"],
            index=2
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

    # 추가 고급 필터 (접이식)
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
            options=[
                "1 (0~12세)", "2 (13~18세)", "3 (19~24세)", "4 (25~29세)",
                "5 (30~34세)", "6 (35~39세)", "7 (40~44세)", "8 (45~49세)",
                "9 (50~54세)", "10 (55~59세)", "11 (60세 이상)"
            ]
        )
        ages_val = [a.split(" ")[0] for a in ages]

    # 제출 버튼
    submit_button = st.form_submit_button("트렌드 분석 시작")

if submit_button:
    # 검색어 전처리
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    if not keywords:
        st.error("⚠️ 검색어를 최소 1개 이상 입력해주세요.")
        st.stop()
    if len(keywords) > 5:
        st.warning("⚠️ 최대 5개 검색어까지만 조회가 가능합니다. 상위 5개 검색어만 분석합니다.")
        keywords = keywords[:5]
        
    # 날짜 검증
    if start_date > end_date:
        st.error("⚠️ 시작일이 종료일보다 늦을 수 없습니다.")
        st.stop()

    # API 요청 바디 구성
    # keywordGroups 형식으로 리스트 생성
    keyword_groups = []
    for kw in keywords:
        keyword_groups.append({
            "groupName": kw,
            "keywords": [kw]
        })
        
    payload = {
        "startDate": start_date.strftime("%Y-%m-%d"),
        "endDate": end_date.strftime("%Y-%m-%d"),
        "timeUnit": time_unit_val,
        "keywordGroups": keyword_groups
    }
    
    if device_val:
        payload["device"] = device_val
    if gender_val:
        payload["gender"] = gender_val
    if ages_val:
        payload["ages"] = ages_val

    # API 호출
    api_url = "https://openapi.naver.com/v1/datalab/search"
    headers = app.get_headers()
    
    with st.spinner("네이버 데이터랩 트렌드 데이터를 조회 중입니다..."):
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result_data = response.json()
                
                # 데이터 변환 및 가공
                # 결과를 플로팅하기 위해 데이터프레임 구조화
                # 각 기간별로 모든 키워드의 ratio를 하나의 테이블로 병합
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
                    st.info("💡 조회된 데이터가 없습니다. 검색 기간이나 검색어를 조정해 보세요.")
                else:
                    # 데이터프레임 병합
                    final_df = df_list[0]
                    for next_df in df_list[1:]:
                        final_df = pd.merge(final_df, next_df, on="period", how="outer")
                    
                    final_df = final_df.sort_values("period").reset_index(drop=True)
                    # NaN 값은 0으로 처리
                    final_df = final_df.fillna(0)
                    
                    # 시각화 데이터 재구조화 (wide to long)
                    plot_df = final_df.melt(id_vars=["period"], var_name="검색어", value_name="상대검색량")
                    
                    st.success("데이터를 성공적으로 수집했습니다!")
                    
                    # 각 키워드별 평균/최대값 계산
                    summary_data = []
                    for kw in keywords:
                        if kw in final_df.columns:
                            summary_data.append({
                                "검색어": kw,
                                "평균 검색량": round(final_df[kw].mean(), 2),
                                "최대 검색량": final_df[kw].max(),
                                "최소 검색량": final_df[kw].min()
                            })
                    summary_df = pd.DataFrame(summary_data)
                    
                    # 📌 상단 요약 st.metric 카드 추가 (UX/UI 리서처 제안)
                    st.subheader("📌 핵심 요약 지표")
                    cols = st.columns(len(summary_df))
                    for i, row in summary_df.iterrows():
                        kw_name = row["검색어"]
                        max_val = row["최대 검색량"]
                        mean_val = row["평균 검색량"]
                        
                        # 최대 검색량이 발생한 날짜 찾기
                        max_row = final_df[final_df[kw_name] == max_val]
                        max_period = max_row["period"].values[0] if not max_row.empty else "N/A"
                        
                        with cols[i]:
                            st.metric(
                                label=f"{kw_name} 트렌드",
                                value=f"{mean_val}% / {max_val}%",
                                delta=f"최대 발생일: {max_period}",
                                delta_color="normal"
                            )
                    
                    # 시각화 영역
                    st.subheader("📈 기간별 검색 트렌드 추이")
                    st.caption("가장 검색량이 많았던 시점의 값을 100으로 기준하여 상대적인 변화를 보여줍니다.")
                    
                    # 네이버 그린 포인트를 포함한 커스텀 컬러 테마 적용
                    custom_colors = ["#03C75A", "#3b82f6", "#ef4444", "#f59e0b", "#8b5cf6"]
                    
                    fig = px.line(
                        plot_df,
                        x="period",
                        y="상대검색량",
                        color="검색어",
                        color_discrete_sequence=custom_colors,
                        labels={"period": "기간", "상대검색량": "상대적 검색량 (%)"},
                        title=f"검색어 트렌드 비교 ({start_date} ~ {end_date})",
                        markers=True if time_unit_val == "month" else False
                    )
                    fig.update_layout(
                        hovermode="x unified",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 데이터 요약 정보 및 테이블
                    st.subheader("📋 수집 데이터 분석 요약")
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                    st.subheader("📄 상세 데이터 내역")
                    st.dataframe(final_df, use_container_width=True)
                    
                    # CSV 다운로드 버튼
                    csv = final_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 CSV 데이터 다운로드",
                        data=csv,
                        file_name=f"naver_search_trend_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )

                    
            else:
                st.error(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
                error_info = response.json()
                st.json(error_info)
                
        except Exception as e:
            st.error(f"❌ 데이터 처리 중 오류가 발생했습니다: {str(e)}")
