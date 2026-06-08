import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import sys
import os

# 상위 경로를 임포트 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

st.title("📰 뉴스 검색 및 발행 트렌드 분석")
st.markdown("네이버 뉴스 검색 결과를 수집하여 이슈에 대한 미디어의 관심 추이 및 발행 현황을 시각화 분석합니다.")

# API 인증 검증
app.check_api_keys()

# UI 구성
with st.form("news_form"):
    st.subheader("🔍 뉴스 검색 설정")
    
    query = st.text_input(
        "검색어 입력",
        value="인공지능 AI",
        placeholder="예: 금리 인상, 기후 변화, 신작 영화"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        display_num = st.slider(
            "표시할 결과 개수 (10 ~ 100)",
            min_value=10,
            max_value=100,
            value=50,
            step=10
        )
    with col2:
        sort_option = st.selectbox(
            "정렬 방식",
            options=["유사도순 (sim)", "날짜순 (date)"],
            index=0
        )
        sort_val = sort_option.split(" ")[1].replace("(", "").replace(")", "")

    submit_button = st.form_submit_button("뉴스 데이터 분석")

if submit_button:
    if not query.strip():
        st.error("⚠️ 검색어를 입력해주세요.")
        st.stop()
        
    # API 호출 설정
    api_url = "https://openapi.naver.com/v1/search/news.json"
    headers = app.get_headers()
    params = {
        "query": query,
        "display": display_num,
        "start": 1,
        "sort": sort_val
    }

    with st.spinner("뉴스를 수집하는 중입니다..."):
        try:
            response = requests.get(api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                result_data = response.json()
                items = result_data.get("items", [])
                
                if not items:
                    st.info("💡 검색 결과가 존재하지 않습니다. 다른 검색어로 시도해 보세요.")
                else:
                    df = pd.DataFrame(items)
                    
                    # HTML 태그 제거 헬퍼 함수
                    import re
                    def remove_html_tags(text):
                        if not isinstance(text, str):
                            return text
                        return re.sub(r'<[^>]*>', '', text)
                    
                    df["title"] = df["title"].apply(remove_html_tags)
                    df["description"] = df["description"].apply(remove_html_tags)
                    
                    # pubDate 파싱 (RFC 822 형식: "Mon, 08 Jun 2026 19:10:00 +0900")
                    # 여러 형식에 호환되도록 처리
                    df["parsed_date"] = pd.to_datetime(df["pubDate"], errors='coerce')
                    df["formatted_date"] = df["parsed_date"].dt.strftime("%Y-%m-%d")
                    df["hour"] = df["parsed_date"].dt.hour
                    
                    st.success(f"총 {len(df)}개의 뉴스 기사를 성공적으로 수집했습니다!")
                    
                    tab1, tab2, tab3 = st.tabs(["📊 미디어 트렌드 리포트", "📋 수집된 뉴스 목록", "📄 전체 데이터 보기"])
                    
                    with tab1:
                        st.subheader("💡 뉴스 미디어 발행 분석")
                        
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            st.subheader("📅 일자별 기사 발행량 추이")
                            # 일자별 발행 건수 집계
                            date_counts = df["formatted_date"].value_counts().reset_index()
                            date_counts.columns = ["발행일", "기사수"]
                            date_counts = date_counts.dropna().sort_values("발행일")
                            
                            if not date_counts.empty:
                                fig_bar = px.bar(
                                    date_counts,
                                    x="발행일",
                                    y="기사수",
                                    labels={"발행일": "날짜", "기사수": "보도 기사 수 (건)"},
                                    title="일자별 뉴스 보도 빈도",
                                    color_discrete_sequence=["#ff7f0e"]
                                )
                                st.plotly_chart(fig_bar, use_container_width=True)
                            else:
                                st.info("발행일자 데이터를 파싱할 수 없어 차트를 표시할 수 없습니다.")
                                
                        with col_chart2:
                            st.subheader("⏰ 시간대별 기사 발행 추이 (24시간)")
                            hour_counts = df["hour"].value_counts().reset_index()
                            hour_counts.columns = ["시간대", "기사수"]
                            # 모든 시간대(0~23)를 포괄하기 위해 정렬 및 빈 영역 보완
                            hour_counts = hour_counts.dropna().sort_values("시간대")
                            
                            if not hour_counts.empty:
                                fig_line = px.line(
                                    hour_counts,
                                    x="시간대",
                                    y="기사수",
                                    labels={"시간대": "시 (Hour)", "기사수": "보도 기사 수 (건)"},
                                    title="24시간대별 기사 발행 추이",
                                    markers=True,
                                    color_discrete_sequence=["#d62728"]
                                )
                                fig_line.update_xaxes(tickmode="linear", tick0=0, dtick=2)
                                st.plotly_chart(fig_line, use_container_width=True)
                            else:
                                st.info("시간대 데이터를 파싱할 수 없어 차트를 표시할 수 없습니다.")
                            
                    with tab2:
                        st.subheader("📰 뉴스 기사 목록")
                        for idx, row in df.iterrows():
                            with st.container():
                                st.markdown(f"### {row['title']}")
                                st.caption(f"📅 보도 시각: {row['pubDate']}")
                                st.write(row["description"])
                                
                                # 링크 표시 (네이버 뉴스와 언론사 원문 링크 모두 제공)
                                link_cols = st.columns(2)
                                with link_cols[0]:
                                    if row['originallink']:
                                        st.markdown(f"🔗 [언론사 원문 기사 보기]({row['originallink']})")
                                with link_cols[1]:
                                    if row['link']:
                                        st.markdown(f"📰 [네이버 뉴스에서 보기]({row['link']})")
                                st.markdown("---")
                                
                    with tab3:
                        st.subheader("📄 상세 뉴스 데이터")
                        display_df = df[["title", "pubDate", "originallink", "link", "description"]]
                        st.dataframe(display_df, use_container_width=True)
                        
                        # CSV 다운로드
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 뉴스 데이터 다운로드 (CSV)",
                            data=csv,
                            file_name=f"naver_news_{query}.csv",
                            mime="text/csv"
                        )
            else:
                st.error(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
                error_info = response.json()
                st.json(error_info)
                
        except Exception as e:
            st.error(f"❌ 데이터 처리 중 오류가 발생했습니다: {str(e)}")
