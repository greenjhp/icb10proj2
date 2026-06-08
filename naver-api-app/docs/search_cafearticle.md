# 네이버 검색 - 카페글 API 가이드

네이버 카페 게시글의 검색 결과를 검색어 기준으로 조회하는 API 규격 요약입니다.

## 1. API 기본 정보
- **요청 URL**: `https://openapi.naver.com/v1/search/cafearticle.json` (JSON 포맷만 지원)
- **HTTP 메서드**: `GET`

## 2. 요청 파라미터 (Query String)
| 파라미터명 | 타입 | 필수 여부 | 기본값 | 범위 | 설명 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `query` | string | 필수 | 없음 | - | 검색하려는 검색어 (UTF-8 인코딩 필수) |
| `display` | integer | 선택 | 10 | 1 ~ 100 | 한 번에 표시할 검색 결과 개수 |
| `start` | integer | 선택 | 1 | 1 ~ 1000 | 검색 시작 위치 (인덱스) |
| `sort` | string | 선택 | `sim` | `sim`, `date` | 정렬 방식 (`sim`: 유사도순, `date`: 날짜순) |

## 3. 응답 구조 (JSON)
- **lastBuildDate**: 검색 결과를 생성한 시간
- **total**: 검색된 총 결과 수
- **start**: 검색 시작 위치
- **display**: 한 번에 출력된 결과 개수
- **items**: 검색 결과의 개별 아이템 리스트
  - **title**: 카페글 제목 (검색어가 매칭된 부분은 태그 강조 가능)
  - **link**: 카페글 상세 주소
  - **description**: 카페글 내용 요약
  - **cafename**: 글이 작성된 카페명
  - **cafeurl**: 해당 카페의 대표 주소

## 4. 관련 공식 가이드 URL
- [카페글 검색 API 가이드](https://developers.naver.com/docs/serviceapi/search/cafearticle/cafearticle.md#%EC%B9%B4%ED%8E%98%EA%B8%80)
