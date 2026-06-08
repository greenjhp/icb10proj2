import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import sys
import os

# 상위 경로를 임포트 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

st.title("☕ 카페글 검색 및 커뮤니티 분석")
st.markdown("네이버 카페 게시글 검색 결과를 수집하여 어떤 온라인 커뮤니티에서 활발히 언급되는지 분석합니다.")

# API 인증 검증
app.check_api_keys()

# UI 구성
with st.form("cafe_form"):
    st.subheader("🔍 카페글 검색 설정")
    
    query = st.text_input(
        "검색어 입력",
        value="중고차 추천",
        placeholder="예: 맛집 후기, 육아 정보, 인테리어 팁"
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

    submit_button = st.form_submit_button("카페글 데이터 분석")

if submit_button:
    if not query.strip():
        st.error("⚠️ 검색어를 입력해주세요.")
        st.stop()
        
    # API 호출 설정
    api_url = "https://openapi.naver.com/v1/search/cafearticle.json"
    headers = app.get_headers()
    params = {
        "query": query,
        "display": display_num,
        "start": 1,
        "sort": sort_val
    }

    with st.spinner("카페 게시글을 수집하는 중입니다..."):
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
                    
                    st.success(f"총 {len(df)}개의 카페 게시글을 성공적으로 수집했습니다!")
                    
                    tab1, tab2, tab3 = st.tabs(["📊 커뮤니티 분석 리포트", "📋 수집된 카페글 목록", "📄 전체 데이터 보기"])
                    
                    with tab1:
                        st.subheader("💡 온라인 커뮤니티 언급 트렌드")
                        
                        # 카페 채널 분포 분석
                        cafe_counts = df["cafename"].value_counts().reset_index()
                        cafe_counts.columns = ["카페명", "게시글수"]
                        cafe_top = cafe_counts.head(10)
                        
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            st.subheader("☕ 언급량이 많은 카페 (Top 10)")
                            fig_bar = px.bar(
                                cafe_top,
                                x="게시글수",
                                y="카페명",
                                orientation="h",
                                labels={"게시글수": "게시글 수 (건)", "카페명": "네이버 카페 이름"},
                                title="주요 커뮤니티별 게시물 빈도",
                                color="게시글수",
                                color_continuous_scale="Viridis"
                            )
                            # Y축 이름 정렬 (순서 뒤집기)
                            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig_bar, use_container_width=True)
                            
                        with col_chart2:
                            st.subheader("📊 상위 카페 언급 점유율")
                            fig_pie = px.pie(
                                cafe_top,
                                values="게시글수",
                                names="카페명",
                                title="상위 10개 카페 채널 간 지분 비교",
                                hole=0.4
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                    with tab2:
                        st.subheader("☕ 수집된 카페 게시글 목록")
                        for idx, row in df.iterrows():
                            with st.container():
                                st.markdown(f"### [{row['title']}]({row['link']})")
                                st.caption(f"🏠 카페명: **{row['cafename']}** ({row['cafeurl']})")
                                st.write(row["description"])
                                st.markdown("---")
                                
                    with tab3:
                        st.subheader("📄 상세 카페글 데이터")
                        display_df = df[["title", "cafename", "link", "description"]]
                        st.dataframe(display_df, use_container_width=True)
                        
                        # CSV 다운로드
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 카페 데이터 다운로드 (CSV)",
                            data=csv,
                            file_name=f"naver_cafe_{query}.csv",
                            mime="text/csv"
                        )
            else:
                st.error(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
                error_info = response.json()
                st.json(error_info)
                
        except Exception as e:
            st.error(f"❌ 데이터 처리 중 오류가 발생했습니다: {str(e)}")
