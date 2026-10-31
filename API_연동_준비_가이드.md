# YUNDVISION API 연동 준비 가이드

API는 자체 시스템 연동을 선택할 때 담당 개발자가 진행합니다. 콘솔만 쓰는 매장 설치의 필수 요건이 아닙니다. 실제 호출은 수행하지 않았습니다.

1. 공급사에 기업 API 개통·허용 모듈·요금·쿼터를 확인하고 전용 account / enterpriseCode / password를 별도 안전한 경로로 받습니다.
2. HTTPS·UTF-8 JSON을 사용합니다. 기준 주소는 https://yd.yunding360.com/openapi/ 입니다.
3. POST /oauth/token에 전용 자격정보를 JSON 본문으로 전달하는 명세입니다. 응답 accessToken·tokenType·refreshToken·수명 필드를 확인하고 서버에서 캐시합니다. HTML·브라우저 저장소·Git에 비밀값을 기록하지 않습니다.
4. api-version은 공통 v1이지만 POST /accStore/getAvgTimeAndFlowNum은 v2입니다. JSON 본문 요청에는 Content-Type: application/json을 사용합니다.
5. 문서의 Authorization은 tokenType+accessToken 결합, 예시는 공백 없는 형태입니다. 통상적인 Bearer 형식을 임의 적용하기 전에 성공 헤더를 공급사에서 받아 공백·접두어를 확정합니다.
6. GET /stores, GET /devices/page, GET /accStore/store/allList로 대상 매장·장치와 권한을 확인합니다. 기본 페이지는 0부터이며 모든 content/metadata 페이지를 처리합니다.
7. 방문객 v2는 yyyy-MM-dd·DAY/HOUR, 관심도와 히트맵은 밀리초 입력입니다. 방문객 총/평균시간과 attentionAvgDuration은 문서상 초입니다. 한국 시간대·끝 경계·비교 기간·처리 지연은 별도 합의합니다.
8. storeIds가 단일 UUID인지 배열인지 표기 차이, GET /area/heat/data/attention의 body 표기는 실제 성공 스키마를 요청합니다. 최대 기간·크기·호출한도도 확인합니다.
9. GET /videos/{sn}/{channelNo}는 IPC의 채널 0을 명시합니다. DX 채널 번호, RTMP/플레이어 호환·URL 만료·권한·저장 유형은 실제 장비로 검수합니다. 재생/녹화 URL은 비밀값이 포함될 수 있어 공유 로그에 남기지 않습니다.
10. 일반 API 401/403은 토큰/권한 확인 후 제한적으로 재인증·재요청하고, 인증 자체의 401/403은 반복하지 않습니다. 최종적으로 동일 조건의 WEB·내보내기 파일·API 결과를 대조합니다.

## 문서 필드와 WEB 지표 대조

| 필드 | 공식 의미 | 검수 주의 |
|---|---|---|
| totalPassTimes / indoorTimes / outdoorTimes | 통행 / 입장 / 퇴장 연인원 | 집계선·기간·중복 조건 대조 |
| totalCustomerPersonNum / customerPersonNum | 전체 고객 수 / 고객 수 | WEB unique와 자동으로 같다고 판단하지 않음 |
| totalWanderTime / avgWanderTime | 총 체류·이동시간 / 평균 체류시간, 초 | 문자열/숫자 및 표본 범위 대조 |
| attentionCustomerNum / attentionCustomerTimes | 관심 고객 수 / 관심 연인원 | 분구·중복 범위 대조 |
| attentionAvgDuration | 평균 관심시간, 초 | 밀리초 입력과 혼동 금지 |

## 근거와 미결 요청

- [접속 안내](https://openapi-docs.yunding360.com/)
- [인증](https://openapi-docs.yunding360.com/auth/)
- [방문객](https://openapi-docs.yunding360.com/accCustomerStoreFlow/)
- [관심도](https://openapi-docs.yunding360.com/attention/)
- [히트맵](https://openapi-docs.yunding360.com/area_heat/)
- [매장](https://openapi-docs.yunding360.com/store/)
- [장치](https://openapi-docs.yunding360.com/device/)
- [영상](https://openapi-docs.yunding360.com/video/)

[F01~F05 공급사 미결 체크리스트](DX-1100_공급사_설치_콘솔_체크리스트.md)를 사용합니다. 공식 문서 명세 확인과 실제 API 요청 성공은 별개입니다.
