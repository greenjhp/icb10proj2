import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv

# .env 파일 로드
load_dotenv(find_dotenv())

# 페이지 설정
st.set_page_config(
    page_title="네이버 API 통합 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if "client_id" not in st.session_state:
    st.session_state["client_id"] = os.getenv("NAVER_CLIENT_ID") or st.secrets.get("client_id", "")
if "client_secret" not in st.session_state:
    st.session_state["client_secret"] = os.getenv("NAVER_CLIENT_SECRET") or st.secrets.get("client_secret", "")


# 사이드바 설정
st.sidebar.title("🔑 네이버 API 인증 설정")
st.sidebar.markdown("네이버 개발자 센터에서 발급받은 API 키를 입력해주세요.")

client_id_input = st.sidebar.text_input(
    "Client ID",
    value=st.session_state["client_id"],
    type="password",
    placeholder="클라이언트 아이디 입력"
)
client_secret_input = st.sidebar.text_input(
    "Client Secret",
    value=st.session_state["client_secret"],
    type="password",
    placeholder="클라이언트 시크릿 입력"
)

# 입력값 세션 상태에 반영
st.session_state["client_id"] = client_id_input
st.session_state["client_secret"] = client_secret_input

# 사이드바 가이드 정보
st.sidebar.markdown("---")
st.sidebar.markdown(
    "### 💡 사용 방법\n"
    "1. 왼쪽 메뉴에 API 인증 키를 입력합니다.\n"
    "2. 왼쪽 페이지 목록에서 원하는 분석 탭을 선택합니다.\n"
    "3. 검색어와 기간을 설정한 후 분석을 진행합니다."
)

# 메인 페이지 콘텐츠
st.title("📊 네이버 API 통합 분석 대시보드")
st.markdown("---")

st.markdown(
    """
    ## 🚀 환영합니다!
    본 대시보드는 네이버 오픈 API를 활용하여 다양한 데이터를 수집하고 분석할 수 있는 웹 어플리케이션입니다.
    
    ### 🛠️ 주요 기능
    * **📊 검색어 트렌드 분석**: 네이버 통합검색 내 특정 키워드의 상대적인 검색 추이를 파악합니다.
    * **🛍️ 쇼핑 검색 분석**: 쇼핑 상품들의 최저가 분포와 쇼핑몰별 점유율을 분석합니다.
    * **📝 블로그 검색 분석**: 최신 블로그 발행 트렌드 및 주요 채널을 분석합니다.
    * **☕ 카페 검색 분석**: 특정 검색어 관련 카페글 게시 추이 및 주요 카페 커뮤니티 분포를 확인합니다.
    * **📰 뉴스 검색 분석**: 실시간 관련 뉴스를 수집하고 기사 발행 시간대별 추이를 시각화합니다.
    * **📈 쇼핑 트렌드 분석**: 데이터랩 쇼핑인사이트 API를 활용하여 분야별 키워드 트렌드를 정밀 분석합니다.
    """
)

apply_custom_style()

# 공통 스타일 주입 함수 (네이버 그린 테마 및 카드 디자인)
def apply_custom_style():
    st.markdown(
        """
        <style>
        /* 네이버 그린 버튼 스타일 */
        div.stButton > button:first-child {
            background-color: #03C75A !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.5rem 1rem !important;
            font-weight: bold !important;
            transition: all 0.2s ease-in-out !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #02b34a !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(3, 199, 90, 0.3) !important;
        }
        /* 메트릭 카드 프리미엄 스타일 */
        div[data-testid="metric-container"] {
            background-color: #1a1c23 !important;
            border: 1px solid #2d3139 !important;
            padding: 20px !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15) !important;
        }
        /* 메트릭 값 강조 */
        div[data-testid="stMetricValue"] {
            color: #03C75A !important;
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# 공통 인증 키 검증 함수
def check_api_keys():
    """API 키가 입력되었는지 확인하고 검증하는 함수"""
    apply_custom_style()  # 페이지 로드시 공통 스타일 자동 적용
    if not st.session_state["client_id"] or not st.session_state["client_secret"]:
        st.warning("⚠️ 왼쪽 사이드바에서 네이버 API Client ID와 Client Secret을 먼저 입력해주세요.")
        st.info("💡 네이버 개발자 센터(https://developers.naver.com/)에서 애플리케이션을 등록하시면 키를 발급받을 수 있습니다.")
        st.stop()


# 공통 헤더 반환 함수
def get_headers():
    """API 호출을 위한 인증 헤더 딕셔너리 반환"""
    return {
        "X-Naver-Client-Id": st.session_state["client_id"],
        "X-Naver-Client-Secret": st.session_state["client_secret"],
        "Content-Type": "application/json"
    }
