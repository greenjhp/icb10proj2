# 네이버 오픈API 공통 가이드

네이버 오픈API를 사용하기 위한 공통 호출 규격 및 인증 방식 안내입니다.

## 1. 개요
네이버 오픈API는 HTTP 기반의 REST API로 제공되며, 인증을 위해 애플리케이션 등록 후 발급받은 클라이언트 아이디와 클라이언트 시크릿을 HTTP 헤더에 포함하여 전송해야 합니다.

## 2. API 호출 인증 헤더
API를 호출할 때 HTTP 요청 헤더에 아래 두 가지 정보를 설정하여 전송합니다.

| 헤더 이름 | 설명 |
| :--- | :--- |
| `X-Naver-Client-Id` | 애플리케이션 등록 후 발급받은 **Client ID** 값 |
| `X-Naver-Client-Secret` | 애플리케이션 등록 후 발급받은 **Client Secret** 값 |

## 3. 대표적인 오류 코드 (Common Error Codes)
네이버 오픈API 호출 시 발생할 수 있는 주요 에러 코드와 설명입니다.

| HTTP 상태 코드 | 에러 코드 | 에러 메시지 및 발생 원인 |
| :--- | :--- | :--- |
| **400** | `SE01` | **Bad Request**: 잘못된 쿼리 요청이거나 필수 파라미터 누락 |
| **401** | `SE02` | **Unauthorized**: 인증 헤더 값이 없거나 잘못됨 |
| **403** | `SE03` | **Forbidden**: API 권한이 설정되지 않았거나 호출 제한 초과 |
| **404** | `SE04` | **Not Found**: 잘못된 URL 호출 |
| **500** | `SE99` | **Internal Server Error**: 네이버 서버 내부 오류 |

## 4. 관련 공식 가이드 URL
- [네이버 오픈API 공통 가이드](https://developers.naver.com/docs/common/openapiguide/)
