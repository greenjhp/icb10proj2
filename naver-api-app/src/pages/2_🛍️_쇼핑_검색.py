import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import sys
import os

# 상위 경로를 임포트 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

st.title("🛍️ 쇼핑 검색 및 상품 분석")
st.markdown("네이버 쇼핑 상품 검색 결과를 통해 상품 가격 분포 및 판매 쇼핑몰 점유율을 분석합니다.")

# API 인증 검증
app.check_api_keys()

# UI 구성
with st.form("shopping_form"):
    st.subheader("🔍 쇼핑 상품 검색 설정")
    
    query = st.text_input(
        "검색 상품명 입력",
        value="무선 헤드폰",
        placeholder="예: 갤럭시 버즈, 노트북, 텀블러"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        display_num = st.slider(
            "표시할 결과 개수 (10 ~ 100)",
            min_value=10,
            max_value=100,
            value=30,
            step=10
        )
    with col2:
        sort_option = st.selectbox(
            "정렬 방식",
            options=[
                "유사도순 (sim)",
                "날짜순 (date)",
                "가격 낮은순 (asc)",
                "가격 높은순 (dsc)"
            ],
            index=0
        )
        sort_val = sort_option.split(" ")[1].replace("(", "").replace(")", "")

    submit_button = st.form_submit_button("상품 데이터 수집 및 분석")

if submit_button:
    if not query.strip():
        st.error("⚠️ 검색 상품명을 입력해주세요.")
        st.stop()
        
    # API 호출 설정
    api_url = "https://openapi.naver.com/v1/search/shopping.json"
    headers = app.get_headers()
    params = {
        "query": query,
        "display": display_num,
        "start": 1,
        "sort": sort_val
    }

    with st.spinner("상품 정보를 수집하는 중입니다..."):
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
                    
                    # 가격 컬럼(lprice) 전처리 (정수형 변환)
                    df["lprice"] = pd.to_numeric(df["lprice"], errors='coerce').fillna(0).astype(int)
                    
                    # 최저가가 0원인 제품을 제외한 데이터로 가격 분포 분석
                    valid_price_df = df[df["lprice"] > 0]
                    
                    st.success(f"총 {len(df)}개의 상품 데이터를 성공적으로 수집했습니다!")
                    
                    # 탭 분석 영역
                    tab1, tab2, tab3 = st.tabs(["📊 데이터 분석 리포트", "🖼️ 상품 목록 카드", "📋 전체 데이터 보기"])
                    
                    with tab1:
                        st.subheader("💡 상품 분석 인사이트")
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("최고가 상품", f"{int(df['lprice'].max()):,} 원")
                        with col_stat2:
                            # 0원이 아닌 최저가
                            min_price = valid_price_df['lprice'].min() if not valid_price_df.empty else 0
                            st.metric("최저가 상품", f"{int(min_price):,} 원")
                        with col_stat3:
                            mean_price = valid_price_df['lprice'].mean() if not valid_price_df.empty else 0
                            st.metric("평균 판매가", f"{int(mean_price):,} 원")
                        
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            st.subheader("💳 최저가 가격 분포")
                            if not valid_price_df.empty:
                                fig_hist = px.histogram(
                                    valid_price_df,
                                    x="lprice",
                                    nbins=15,
                                    labels={"lprice": "가격 (원)"},
                                    title="상품 최저가 구간별 분포",
                                    color_discrete_sequence=["#2ca02c"]
                                )
                                fig_hist.update_layout(yaxis_title="상품 개수")
                                st.plotly_chart(fig_hist, use_container_width=True)
                            else:
                                st.info("가격 데이터가 존재하지 않아 차트를 그릴 수 없습니다.")
                                
                        with col_chart2:
                            st.subheader("🏪 쇼핑몰 점유율 (Top 10)")
                            mall_counts = df["mallName"].value_counts().reset_index()
                            mall_counts.columns = ["쇼핑몰명", "상품수"]
                            mall_top = mall_counts.head(10)
                            
                            fig_pie = px.pie(
                                mall_top,
                                values="상품수",
                                names="쇼핑몰명",
                                title="상위 쇼핑몰별 상품 등록 비율",
                                hole=0.3
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                    with tab2:
                        st.subheader("📦 수집된 쇼핑 상품 목록")
                        
                        # 카드 형태로 상품 노출 (한 행에 3개씩 배치)
                        cols_per_row = 3
                        for idx, row in df.iterrows():
                            if idx % cols_per_row == 0:
                                cols = st.columns(cols_per_row)
                            
                            col_idx = idx % cols_per_row
                            with cols[col_idx]:
                                # 상품 썸네일 이미지 및 카드 정보 표기
                                st.image(row["image"], use_container_width=True)
                                
                                # 상품명 간소화
                                title = row["title"]
                                if len(title) > 40:
                                    title = title[:37] + "..."
                                st.markdown(f"**[{title}]({row['link']})**")
                                
                                st.markdown(f"💵 **최저가**: `{int(row['lprice']):,}원`" if row['lprice'] > 0 else "💵 **최저가**: `정보 없음`")
                                st.markdown(f"🏪 **쇼핑몰**: `{row['mallName']}`")
                                if row['brand']:
                                    st.markdown(f"🏷️ **브랜드**: `{row['brand']}`")
                                st.markdown("---")

                    with tab3:
                        st.subheader("📄 상세 상품 데이터 리스트")
                        # 필요한 열만 필터링하여 출력
                        display_df = df[["title", "lprice", "mallName", "brand", "maker", "category1", "category2", "link"]]
                        st.dataframe(display_df, use_container_width=True)
                        
                        # CSV 다운로드
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 쇼핑 데이터 다운로드 (CSV)",
                            data=csv,
                            file_name=f"naver_shopping_{query}.csv",
                            mime="text/csv"
                        )
            else:
                st.error(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
                error_info = response.json()
                st.json(error_info)
                
        except Exception as e:
            st.error(f"❌ 데이터 처리 중 오류가 발생했습니다: {str(e)}")
