import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import sys
import os

# 상위 경로를 임포트 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

st.title("📝 블로그 검색 및 포스트 분석")
st.markdown("네이버 블로그 검색 결과를 수집하여 발행 트렌드 및 주요 인플루언서 채널을 분석합니다.")

# API 인증 검증
app.check_api_keys()

# UI 구성
with st.form("blog_form"):
    st.subheader("🔍 블로그 검색 설정")
    
    query = st.text_input(
        "검색어 입력",
        value="국내 여행 추천",
        placeholder="예: 맛집 리뷰, 신형 스마트폰, 캠핑 용품"
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

    submit_button = st.form_submit_button("블로그 데이터 분석")

if submit_button:
    if not query.strip():
        st.error("⚠️ 검색어를 입력해주세요.")
        st.stop()
        
    # API 호출 설정
    api_url = "https://openapi.naver.com/v1/search/blog.json"
    headers = app.get_headers()
    params = {
        "query": query,
        "display": display_num,
        "start": 1,
        "sort": sort_val
    }

    with st.spinner("블로그 포스트를 수집하는 중입니다..."):
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
                    
                    # 날짜 형식 변환 (YYYYMMDD -> YYYY-MM-DD)
                    df["parsed_date"] = pd.to_datetime(df["postdate"], format="%Y%m%d", errors='coerce')
                    df["formatted_date"] = df["parsed_date"].dt.strftime("%Y-%m-%d")
                    
                    st.success(f"총 {len(df)}개의 블로그 포스트를 성공적으로 수집했습니다!")
                    
                    tab1, tab2, tab3 = st.tabs(["📊 데이터 분석 리포트", "📋 수집된 포스트 목록", "📄 전체 데이터 보기"])
                    
                    with tab1:
                        st.subheader("💡 블로그 트렌드 분석")
                        
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            st.subheader("📅 일자별 블로그 발행 추이")
                            # 일자별 발행 건수 집계
                            date_counts = df["formatted_date"].value_counts().reset_index()
                            date_counts.columns = ["작성일", "발행수"]
                            date_counts = date_counts.sort_values("작성일")
                            
                            fig_line = px.bar(
                                date_counts,
                                x="작성일",
                                y="발행수",
                                labels={"작성일": "작성일자", "발행수": "게시글 수 (건)"},
                                title="수집 데이터 내 일자별 블로그 작성량",
                                color_discrete_sequence=["#1f77b4"]
                            )
                            st.plotly_chart(fig_line, use_container_width=True)
                            
                        with col_chart2:
                            st.subheader("👤 활발한 블로그 채널 (Top 10)")
                            blogger_counts = df["bloggername"].value_counts().reset_index()
                            blogger_counts.columns = ["블로그명", "작성글수"]
                            blogger_top = blogger_counts.head(10)
                            
                            fig_pie = px.pie(
                                blogger_top,
                                values="작성글수",
                                names="블로그명",
                                title="상위 블로그 채널 점유율",
                                hole=0.3
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                    with tab2:
                        st.subheader("📝 블로그 포스트 리스트")
                        for idx, row in df.iterrows():
                            # 블로그 포스트 카드 UI 구현
                            with st.container():
                                st.markdown(f"### [{row['title']}]({row['link']})")
                                st.caption(f"✍️ 작성자: {row['bloggername']} ({row['bloggerlink']}) | 📅 작성일: {row['formatted_date']}")
                                st.write(row["description"])
                                st.markdown("---")
                                
                    with tab3:
                        st.subheader("📄 상세 블로그 데이터")
                        display_df = df[["title", "bloggername", "formatted_date", "link", "description"]]
                        st.dataframe(display_df, use_container_width=True)
                        
                        # CSV 다운로드
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 블로그 데이터 다운로드 (CSV)",
                            data=csv,
                            file_name=f"naver_blog_{query}.csv",
                            mime="text/csv"
                        )
            else:
                st.error(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
                error_info = response.json()
                st.json(error_info)
                
        except Exception as e:
            st.error(f"❌ 데이터 처리 중 오류가 발생했습니다: {str(e)}")
