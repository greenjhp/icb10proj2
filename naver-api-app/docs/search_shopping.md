# 네이버 검색 - 쇼핑 API 가이드

네이버 쇼핑 상품 검색 결과를 검색어 기준으로 조회하는 API 규격 요약입니다.

## 1. API 기본 정보
- **요청 URL**: `https://openapi.naver.com/v1/search/shopping.json` (JSON 포맷만 지원)
- **HTTP 메서드**: `GET`

## 2. 요청 파라미터 (Query String)
| 파라미터명 | 타입 | 필수 여부 | 기본값 | 범위 | 설명 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `query` | string | 필수 | 없음 | - | 검색하려는 검색어 (UTF-8 인코딩 필수) |
| `display` | integer | 선택 | 10 | 1 ~ 100 | 한 번에 표시할 검색 결과 개수 |
| `start` | integer | 선택 | 1 | 1 ~ 1000 | 검색 시작 위치 (인덱스) |
| `sort` | string | 선택 | `sim` | `sim`, `date`, `asc`, `dsc` | 정렬 방식 (`sim`: 유사도순, `date`: 날짜순, `asc`: 가격 오름차순, `dsc`: 가격 내림차순) |

## 3. 응답 구조 (JSON)
- **lastBuildDate**: 검색 결과를 생성한 시간
- **total**: 검색된 총 결과 수
- **start**: 검색 시작 위치
- **display**: 한 번에 출력된 결과 개수
- **items**: 검색 결과의 개별 쇼핑 상품 리스트
  - **title**: 상품명 (검색어가 매칭된 부분은 태그 강조 가능)
  - **link**: 상품 구매/판매 페이지 상세 주소
  - **image**: 상품 이미지 URL
  - **lprice**: 최저가 가격 정보 (최저가가 없거나 미표시 상태면 빈 문자열)
  - **hprice**: 최고가 가격 정보
  - **mallName**: 상품을 판매하는 쇼핑몰명
  - **productId**: 네이버 쇼핑 고유 상품 ID
  - **productType**: 상품 타입 정보 (예: `1`: 일반상품, `2`: 중고상품, `3`: 단종상품 등)
  - **brand**: 상품 브랜드명
  - **maker**: 상품 제조사명
  - **category1** ~ **category4**: 네이버 쇼핑 대분류/중분류/소분류/세분류 카테고리명

## 4. 관련 공식 가이드 URL
- [쇼핑 검색 API 가이드](https://developers.naver.com/docs/serviceapi/search/shopping/shopping.md#%EC%87%BC%ED%95%91)
