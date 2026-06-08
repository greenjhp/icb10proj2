# 네이버 데이터랩 - 통합 검색어 트렌드 API 가이드

네이버 통합검색 내에서 검색어의 검색 추이 데이터를 조회하는 API 규격 요약입니다.

## 1. API 기본 정보
- **요청 URL**: `https://openapi.naver.com/v1/datalab/search`
- **HTTP 메서드**: `POST`
- **콘텐트 타입**: `application/json`

## 2. 요청 파라미터 (JSON Body)
| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :--- | :--- |
| `startDate` | string | 필수 | 조회 시작 날짜 (형식: `YYYY-MM-DD`) |
| `endDate` | string | 필수 | 조회 종료 날짜 (형식: `YYYY-MM-DD`) |
| `timeUnit` | string | 필수 | 구간 단위 (`date`: 일간, `week`: 주간, `month`: 월간) |
| `keywordGroups` | array | 필수 | 주제어 집합 배열 (최대 5개까지 설정 가능) |
| `keywordGroups.groupName` | string | 필수 | 주제어 이름 |
| `keywordGroups.keywords` | array | 필수 | 주제어에 해당하는 검색어 배열 (최대 20개) |
| `device` | string | 선택 | 기기 유형 설정 (설정하지 않으면 전체 조회, `pc`: PC, `mo`: 모바일) |
| `gender` | string | 선택 | 성별 설정 (설정하지 않으면 전체 조회, `m`: 남성, `f`: 여성) |
| `ages` | array | 선택 | 연령대 설정 (설정하지 않으면 전체 조회, `1`~`11` 구간 설정 가능) |

## 3. 요청 예시 (JSON)
```json
{
  "startDate": "2023-01-01",
  "endDate": "2023-12-31",
  "timeUnit": "month",
  "keywordGroups": [
    {
      "groupName": "스마트폰",
      "keywords": ["아이폰", "갤럭시", "iphone", "galaxy"]
    }
  ]
}
```

## 4. 응답 구조 (JSON)
- **startDate**: 조회 시작 날짜
- **endDate**: 조회 종료 날짜
- **timeUnit**: 구간 단위
- **results**: 데이터 결과 리스트
  - **title**: 주제어 이름
  - **keywords**: 주제어 내 검색어 목록
  - **data**: 기간별 검색 추이 데이터 리스트
    - **period**: 해당 기간의 날짜
    - **ratio**: 조회 기간 내 최대 검색량을 100으로 설정했을 때의 상대적 값

## 5. 관련 공식 가이드 URL
- [통합 검색어 트렌드 API](https://developers.naver.com/docs/serviceapi/datalab/search/search.md#%ED%86%B5%ED%95%A9-%EA%B2%80%EC%83%89%EC%96%B4-%ED%8A%B8%EB%A0%8C%EB%93%9C)
