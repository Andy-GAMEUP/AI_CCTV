"""Console observations and supplier checklist, verified through Chrome UI."""
from pathlib import Path
from html import escape
import base64,re

ROOT=Path(__file__).parent
CHECKS=[
("A01","설치","P0","납품 사양","DX-1100 세부 형번·펌웨어, CCTV 모델·수량, 포트별 용도·전원·동봉품을 제공해 주세요.","사양표·본체 사진·구성품표"),
("A02","설치","P0","분석 수행 위치·호환성","영상·녹화·방문객·핫존·동선을 카메라/셋탑/클라우드 중 어디에서 수행하는지, 타사 ONVIF 포함 모델별 지원 여부와 라이선스를 확정해 주세요.","모델·펌웨어·기능 호환표"),
("A03","설치","P0","배선·PoE","CCTV 3대·공유기·스위치·DX-1100·노트북의 포트별 배선, PoE 규격·전력·분리기 필요 여부를 제공해 주세요.","배선도 1장·전원표·거리 조건"),
("A04","설치","P0","카메라 배치·보정","납품 카메라의 높이·각도·범위·조도·역광 조건과 출입구/매장/계산대 배치, 중첩 시야 보정을 안내해 주세요.","배치도·권장 수치·보정 화면"),
("A05","설치","P0","공식 도구·실행 환경","구성 도구·플러그인의 공식 설치 파일/URL·버전·지원 OS/브라우저·오프라인 설치·오류 조치를 제공해 주세요.","프로그램·버전표·한국어 설치 순서"),
("A06","설치","P0","최초 계정·네트워크","DX·카메라 활성화·초기 계정·변경/분실 복구, DHCP/고정 IP·DNS/NTP, 필수 외부 통신 대상·포트·방향을 안내해 주세요.","설정표·통신 요구사항·계정 인계법"),
("A07","설치","P0","ONVIF·스트림","카메라별 ONVIF 활성화·전용 계정·실제 포트, 코덱·화질·프레임률·비트레이트와 스트림1/2 정상 기준을 제공해 주세요.","설정표·카메라 등록 성공 화면"),
("A08","설치","P0","HDD·외장하드","1TB 내장 HDD의 규격·크기·허용 용량·장착·초기화를 안내하고 USB 외장하드가 녹화용/백업용/미지원인지 명시해 주세요.","저장장치 지원표·장착/초기화 화면"),
("A09","설치","P0","로컬 녹화·재생","채널별 녹화 시간표·덮어쓰기·검색·재생·영상 추출, 3대·1TB의 보관 기간과 산출 조건을 안내해 주세요.","녹화·재생 매뉴얼·용량 계산"),
("B01","플랫폼","P0","권한·라이선스","관리자/운영자의 매장·장치·분석·다운로드 접근 범위와 모듈·기능별 활성화/요금 조건을 확인해 주세요.","권한표·납품 기능 범위표"),
("B02","플랫폼","P0","매장 생성·한국 주소","Stores architecture → Add a store의 필수값, 한국 주소/지도 선택, 매장번호·면적·Business status·Launch time 의미를 안내해 주세요.","한국 매장 생성 시연·필드 정의"),
("B03","플랫폼","P0","영업시간·시간대","요일별·휴일·자정 넘김 영업시간, 장치·콘솔 시간대, 하루 마감 기준과 과거 통계 영향·일괄 설정법을 설명해 주세요.","시간 설정 화면·집계 예시"),
("B04","플랫폼","P0","구역·도면 매핑","Create in-store zone 후속 화면, 도면 업로드·축척·층/구역 생성, 카메라 연결·보정·수정/삭제 영향을 안내해 주세요.","샘플 매장·구역/도면 설정 매뉴얼"),
("B05","플랫폼","P0","DX 등록 유형","Video/Traffic(in)/Traffic(pass)/Storage/Attention/Traffic(in&pass) 중 DX-1100과 각 카메라에 쓸 유형 및 별도 등록 필요 여부를 확정해 주세요.","실제 모델→등록 유형 매핑표"),
("B06","플랫폼","P0","시리얼·key·바인딩","Serial number·key 확인/발급 위치·필수 여부, 기존 계정 등록 해제·재등록·교체·오류 조치를 안내해 주세요.","라벨 예시·등록/해제 절차"),
("B07","플랫폼","P0","온라인·채널 상태","Status·Firmware version·Last online time 정상 기준과 셋탑 아래 카메라 3대의 Channel Management 연결 구조·최초 반영 시간을 안내해 주세요.","장치·3채널 정상 화면"),
("B08","플랫폼","P0","접근권한 상속·가시성","Inherit store access rights·Visible·Associated in-store zone의 의미·권한 영향과 구역 선택 선행 조건을 안내해 주세요.","권한·구역 연결 예시"),
("C01","분석","P0","지표 사전","Passby/In-store/Exit traffic, Total customers, Customer count(unique), Customer group의 정의·단위·집계 범위를 구분해 주세요.","지표 사전·같은 샘플의 계산 예시"),
("C02","분석","P0","중복·비고객 제외","도움말의 중복·직원/배달원·단기 체류·대상 연령 제외 설정 위치·기본값·식별 방식·일/매장/카메라 간 중복 범위를 안내해 주세요.","설정 화면·임계값·검증 예시"),
("C03","분석","P0","입점률·체류 산식","입점률 Customer count/Passby traffic 산식의 선행 장치·지표 조건·분모 0 처리와 평균 체류 시작/종료·제외·상한 규칙을 확정해 주세요.","산식·경계 사례·표본"),
("C04","분석","P0","동선 10초 표본","Moving line analysis의 ≥10s dwell time in zone 조건 적용 탭·범위·변경 가능 여부와 짧은 동선 누락 영향을 설명해 주세요.","4개 탭 정의·표본 규칙·도식"),
("C05","분석","P1","히트맵·관심도","attention count·Avg. attention duration·Wandering/Interested/Purchase-inclined의 정의·임계값과 3D/Table/Chart 범례를 설명해 주세요.","지표·분류 기준·샘플 화면"),
("C06","분석","P1","기간·비교·분포","Today/Yesterday/주/월/Customize, MoM·PoP·YOY·Distribution의 기간 정렬·시간 집계·휴일 처리 의미를 설명해 주세요.","필터별 사용법·계산 예시"),
("C07","분석","P0","빈 데이터·지연","--·0·0s·No data·No qualified stores found 차이, 집계/표시 지연, 최소 표본과 권한·설정·수집 장애 진단법을 안내해 주세요.","상태 정의·정상 반영 시간·점검표"),
("C08","분석","P1","속성·피팅·매출","Customer profile·Costume analysis·피팅·매출의 장치/추가 데이터 연동·라이선스·이번 납품 지원/미지원 범위를 확정해 주세요.","기능 범위·연계 규격·보고서"),
("D01","사용","P0","온라인 영상·녹화","매장/채널 선택, 실시간·시간 지정/비동기 재생·배속·녹화 다운로드와 로컬 HDD/클라우드 저장 구분을 안내해 주세요.","3채널 시연·브라우저 조건"),
("D02","사용","P1","영상 부가 기능","Capture all·View snaps·PTZ·Layout·Full screen·Passenger flows의 의미와 지원 모델·추가 권한/요금을 안내해 주세요.","기능별 지원표·화면"),
("D03","사용","P0","데이터 내보내기","기간·시간/장소 차원·지표 선택→Preview→Export, 파일 형식·인코딩·열 정의·최대 행/기간·실패 처리를 제공해 주세요.","실제 샘플 파일·화면 합계 대조"),
("D04","사용","P1","알림·오프라인","Device warning/Alarm push·장치 통계/오프라인 로그·Data Alert의 조건·수신 대상·중복/복구 알림·비용을 안내해 주세요.","테스트 알림·장애/복구 예시"),
("D05","사용","P1","로그·유지보수","로그인/페이지/시스템/영상 작업 로그의 보관·조회·출력, 업데이트·백업/복구·장치 교체·지원 절차를 제공해 주세요.","운영 매뉴얼·로그·지원 연락처"),
("D06","사용","P0","데이터·원격 접근","영상/분석/속성 데이터의 저장 위치·보관·삭제·계정 해제, 전송 대상과 공급사 원격 접근 범위를 설명해 주세요.","데이터 흐름도·권한/보관표"),
("E01","검수","P0","테스트 환경","조회 가능한 장치 0대·매장 없음 상태의 원인을 확인하고 실제 장치 또는 샘플 매장·데이터를 제공해 주세요.","DX+카메라 3대 매핑된 검수 환경"),
("E02","검수","P0","설치→콘솔 시연","초기 상태→배선→IP→HDD→카메라3대→매장/장치/구역→영상/재생→분석→내보내기 전체를 시연해 주세요.","한국어 매뉴얼·전체 영상·정상 화면"),
("E03","검수","P0","방문객 정확도","수동 관찰과 콘솔을 대조할 표본 수·조건·정답 정의·허용 오차·중복/직원 제외 시험을 제시해 주세요.","합의 검수 기준·관찰표·결과"),
("E04","검수","P0","동선·체류 시험","3구역 이동, 10초 미만/이상 체류, 반복 출입·중첩 시야의 결과와 수집 지연을 검증해 주세요.","도면·시험 시나리오·결과"),
("E05","검수","P0","재생·파일 대조","3대 실제 녹화 재생과 동일 필터/기간의 화면 지표·내보낸 파일 합계를 대조해 주세요.","영상·샘플 데이터·대조표"),
("E06","검수","P0","복구·인수인계","정전/인터넷 단절/재부팅 후 녹화·분석 재개, 누락/재전송을 시험하고 미결·담당자·완료일을 인계해 주세요.","복구 시험·최종 IP/모델표·미결 목록"),
]

from official_guidance import revise_checks, evidence_html, evidence_md, extend_official, write_notes
CHECKS = revise_checks(CHECKS)

def table(head, rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def picture(name,caption):
    data=base64.b64encode((ROOT/'console_assets'/name).read_bytes()).decode()
    return f'<details class="source-image"><summary>실제 콘솔 화면 · {caption}</summary><figure><img loading="lazy" src="data:image/png;base64,{data}" alt="{caption}"><figcaption>2026-10-31 Chrome 로그인 세션에서 확인. 데이터가 없는 UI 증거이며 실제 기능 동작 완료 증거가 아닙니다.</figcaption></figure></details>'

def section(n,id,title,sub,body):
    return f'<section class="section" id="{id}"><div class="section-head"><span class="number">{n}</span><div><h2>{title}</h2><p>{sub}</p></div></div>{body}</section>'

def supplement():
    intro='''<div class="notice"><strong>점검 기준 · 2026-10-31</strong><a href="https://yd.yunding360.com/V1/work" target="_blank" rel="noopener">YUNDVISION 콘솔 열기 ↗</a><br>사용자가 로그인한 Chrome 세션에서 조회했습니다. 메뉴/양식 확인과 데이터 동작 검증을 구분합니다. 장치·매장 생성, 운영 설정 저장, 권한 변경, 영상/데이터 내보내기는 실행하지 않았습니다.</div><div class="notice warn"><strong>현재 온라인 분석 운영 준비 완료로 판정할 수 없습니다</strong>현재 계정에서 앞선 실화면 점검 시 조회한 Device Config는 0 device in total, 매장 목록은 No data, 영상은 Store/Video 0/0입니다. 분석에는 No qualified stores found 또는 데이터 없음이 표시됩니다. 미등록·권한·필터·라이선스 중 원인은 미확정입니다. --·0s를 실제 방문객 0명·체류시간 0초로 확정하지 마세요.</div>'''
    menu=table(['메뉴 원문 / 한국어','실제 확인 범위','점검 수준'],[
    ('Workbench / 작업대','Business management: 종합 데이터·영상·순찰·방문객 분석. System configuration: 장치·로그·시스템.','화면 확인'),
    ('Comprehensive data dashboard / 종합 데이터','날짜·Venue·Comparison period, Single Metric Table / Comprehensive Data Table.','화면 확인 · 수치 미검증'),
    ('Video surveillance / 영상 감시','매장 트리·Online 필터·검색, 타임라인·배속·캡처·PTZ·화면 배치·녹화 다운로드.','화면 확인 · 영상/재생 미검증'),
    ('Accurate traffic / 방문객 분석','Real-time traffic, Traffic analysis, Passenger flow operation, Property analysis, Customer Mapping, Business Analysis, Export data.','메뉴·주요 조회 화면 확인'),
    ('Device management / 장치 관리','Device Config·Channel Management·Device warning·Device statistics·DeviceTag.','목록·등록 양식 확인'),
    ('System Management / 시스템 관리','Stores architecture, 직위·부서·직원, 태그, 비밀번호 보안, 휴일/이벤트, 외부 알림, Login Config.','매장 목록·생성 양식 확인 / 기타 메뉴 확인'),
    ('Log management / 로그 관리','System login log·Page visit log·System operation log·Video operation log. 로그인 로그의 날짜·직원·Export.','로그인 조회 화면 확인 · 로그 내용 미검증'),
    ('Store inspection management / 순찰','실시간·보고서·통계·Task list·프로세스·설정·스냅샷·Video Gallery·Draft box.','메뉴 확인 · 부가 기능'),
    ])
    s10=section('10','console','온라인 콘솔의 구조와 현재 상태','메뉴 존재와 정상 작동을 구분합니다.',intro+menu+picture('01-workbench.png','워크벤치와 빈 데이터'))
    setup='''<h3>최초 등록 · 매장 → 장치 → 구역 → 연결·분석 확인</h3><p class="small">실제 입력 양식을 확인했지만 저장 이후 단계는 미검증입니다. 납품 정보와 권한을 확인한 후 담당자가 등록하세요. 공식 설명으로 보완된 절차는 14단계, API 준비는 15단계에 정리했습니다.</p>
    <ol class="steps"><li><strong>매장과 영업시간을 만듭니다.</strong><span class="path">Workbench → System configuration → System management → Stores architecture → Add a store</span><p>전체 메뉴 화면에서는 상단 System Management로 이동합니다. 생성 양식 단계: Create a store → Associated device → Create in-store zone.</p><p>필수 표시: Belonging region, Store name, Store number, Address, Detailed address, Business status, Launch time, Store area(m²). 영업시간은 Repeat every day / Repeat every week로 나뉩니다. 확인 시 양식 기본 시간 10:00~22:00는 실제 영업시간으로 수정해야 합니다. 한국 주소 지도와 시간대는 공급사 확인 대상입니다.</p><p>Save&amp;Next / Skip the next steps and save directly 버튼을 확인했습니다. 저장 후 장치·구역 연결 화면은 공급사 매뉴얼과 대조하세요.</p></li>
    <li><strong>모델별 등록 유형과 key를 확인합니다.</strong><span class="path">Device management → Device Config → Add device</span><p>필수 표시: Serial number, Device name, Device type, Associated store. 추가 항목: key, Associated in-store zone, Inherit store access rights(확인 시 체크됨). key는 필수 표시가 없지만 모델별 필요 여부·발급 위치는 미확인입니다. 매장 선택 전 구역은 비활성 상태였습니다.</p><p>유형: Video device / Traffic(in) device / Traffic(pass) device / Storage device / Attention device / Traffic(in&amp;pass) device. <strong>DX-1100 유형 및 카메라 별도 등록 여부는 공급사에서 확정받으세요.</strong> 명칭만 보고 Storage device를 임의 선택하지 않습니다. 기존 바인딩을 확인하고, 매장 접근자가 장치 권한도 상속할지 선택한 후 Confirm으로 저장하는 절차입니다.</p></li>
    <li><strong>온라인 상태와 카메라 3개 채널을 확인합니다.</strong><span class="path">Device management → Device Config / Channel Management</span><p>목록 항목: Device model·Device type·Status·Device binding time·Firmware version·Last online time 등. 매장·유형·상태·Visible 필터가 장치를 숨기지 않는지 확인합니다. 등록 후 셋탑과 3대 카메라의 실제 채널 연결 구조·온라인 상태·영상을 검증해야 합니다.</p></li>
    <li><strong>분석 구역과 카메라를 매핑합니다.</strong><p>Create in-store zone 단계와 Associated in-store zone 항목은 확인했습니다. 실제 도면 업로드·축척·층/구역·카메라 매핑 화면은 현재 빈 매장이라 검증 전입니다. 샘플 매장과 단계별 자료를 받으세요.</p></li></ol>'''
    s11=section('11','console-setup','매장·장치를 콘솔에 등록하는 방법','확인된 양식과 미검증 후속 단계를 표시했습니다.',setup+picture('02-add-device.png','장치 추가 양식'))
    use='''<h3>매일 사용하는 조회 순서</h3><ol class="steps"><li><strong>영상과 장치 상태부터 확인합니다.</strong><span class="path">Video surveillance → 매장/채널 선택 → 실시간 영상</span><p>Store / Region / Favorite / Tag, Online 필터와 검색을 확인했습니다. 등록 후 3채널 영상과 지정 시각의 녹화를 확인합니다. Stop all·Capture all·Asynchronous playback·Double speed·PTZ·Layout·Full screen·Dowload recordings UI가 있습니다. 공식 문서의 배속·캡처·배치·다운로드 조작법은 14단계에 반영했습니다. 실제 장비 재생·다운로드·모델별 PTZ/플러그인은 미검증입니다.</p></li>
    <li><strong>기간·매장을 선택해 방문객을 조회합니다.</strong><span class="path">Accurate traffic → Real-time traffic / Traffic analysis → Overview of in-store traffic</span><p>Real-time traffic의 Today / Yesterday / This week / This month / Customize, Venue, Comparison period(MoM), Data mode(Distribution), Search를 확인했습니다. 같은 기간·매장·필터로 비교하세요. 비교 용어와 Distribution의 정확한 정의는 공급사 확인 대상입니다.</p></li>
    <li><strong>동선·히트맵을 별도로 조회합니다.</strong><span class="path">Accurate traffic → Customer Mapping → Moving line analysis / Density heat map / Store area map</span><p>날짜·매장 선택 후 Search를 누릅니다. 동선은 전체/구역별 방향·경로·구역 공유 흐름을 구분합니다. 히트맵에는 Zone traffic statistics / Avg. attention duration과 3D / Table / Chart UI가 있습니다. 실제 도면·범례·수치는 샘플 데이터로 검증해야 합니다.</p></li>
    <li><strong>지표를 선택하고 미리보기 후 내보냅니다.</strong><span class="path">Accurate traffic → Export data → Export configuration → 조건·지표 선택 → Preview → Export</span><p>조건: Time selection, Time dimension, Venue dimension, Venue selection, Indicator selection. 지표 그룹: Traffic / Sales / Fitting / Customer group / Other. 파일 형식·인코딩·행 제한·수치 일치는 미검증입니다. 동일 조건의 화면 합계와 파일 합계를 대조하세요.</p></li>
    <li><strong>데이터 없음은 원인별로 점검합니다.</strong><p>매장/장치 존재 → 조회 필터·권한 → 온라인·채널 → 분석 지원/활성화 → 구역 연결 → 영업시간/시간대 → 집계 지연 순으로 확인합니다. Device warning에는 Warning statistics·Alarm push, Device statistics에는 Device information·오프라인 비율/상세·매장별 장치 통계·Offline log of device가 있습니다. 메뉴를 확인했으며 실제 장애 로그는 검증 전입니다.</p></li></ol>'''
    metrics=table(['지표 / 기능','확인 내용과 해석 주의'],[
    ('Passby traffic / In-store traffic (person-times)','통행·입점 지표이며 단위는 연인원으로 표시. 집계선·방향·재입장 기준은 공급사 확인 필요.'),
    ('Customer count (unique)','도움말: 중복 고객·비고객(배달/배송/직원 등)·단기 체류·대상 연령 외 고객 제외. 일부는 설정 필요라고 명시. 식별 방식·기간·기본값·설정 위치는 미확인.'),
    ('Store entry rate','도움말 산식: (Customer count / Passby traffic) × 100%. 입출입 흐름 연결 조건을 설명하는 영문 문구도 있으나 정확한 장치·지표 선행 조건과 분모 0 처리는 공급사 확인 필요.'),
    ('Avg. dwell time','평균 체류 표시. 0s는 현재 빈 데이터 상태여서 측정 결과로 확정하지 않음. 시작/종료·제외·상한 확인 필요.'),
    ('Moving line analysis','Flow direction(whole-store) / Flow direction(zone) / Flow path(whole-store) / Shared flow(zone) 4개 탭. 기본 탭에 Sampling rule: ≥10s dwell time in zone 표시. 다른 탭 적용 범위·임계값 변경 가능 여부는 미확인.'),
    ('Store area map / Density heat map','attention count, Avg. attention duration, Wandering / Interested / Purchase-inclined 표시 확인. 분류 임계값·범례·도면은 미검증.'),
    ('PoP / YOY / MoM / Distribution','용어 표시 확인. 비교 기간·분모·누락일 처리와 분포/집계 의미는 공급사 정의서 필요.'),
    ])
    more='''<h3>추가 메뉴 · 장치·권한·라이선스 지원 여부 별도 확인</h3><p class="small">Traffic analysis: Hours and days, Floor customer flow, Traffic ranking, Customer group, Traffic details, Traffic comparison, Cumulative traffic, In-store fitting data. Passenger flow operation: Holiday traffic·Holiday comparison·holidayFlowAnalysi·Weekend holiday flow analysis. Property analysis: Customer profile·Costume analysis. Customer Mapping: Customer wander·Customer trajectory. Business Analysis: Business mapview·Business overview·Business ranking·Yearly accumulation. Export data: Data Alert. 메뉴 존재만 확인했으며 모든 기능의 수치·작동을 검증한 것은 아닙니다. 공식 문서로 확인한 사용법은 14단계를 참고하세요. 매출·피팅 등의 추가 데이터 연계 조건을 확인하세요.</p>'''
    s12=section('12','console-use','영상·방문객·동선·보고서 사용 순서','실제 영문 메뉴를 병기해 화면에서 찾기 쉽도록 했습니다.',use+metrics+picture('03-moving-line.png','동선 탭과 10초 표본 규칙')+picture('04-export.png','내보내기 조건과 지표 선택')+more)
    checklist=table(['ID / 시점','공급사 확인 주제','제출 증거'],[(c[0]+' / '+c[2],escape(c[3]),escape(c[5])) for c in CHECKS])
    lead=f'''<div class="notice"><strong>공급사 회신용 · 총 {len(CHECKS)}개 항목</strong><a href="DX-1100_공급사_설치_콘솔_체크리스트.html">입력·회신용 HTML 체크리스트 ↗</a> · <a href="DX-1100_공급사_설치_콘솔_체크리스트.md">텍스트 원본 ↗</a><br>P0는 설치/운영/검수 전 필수 확인, P1은 운영 기능·추가 납품 범위 확인입니다. 일반 설치·운영 31개, 선택 API 연동 5개, 자체 한글 콘솔 개발 12개입니다. 해소/통합 내역은 16단계에서 확인하며 각 항목의 회신 상태·근거·담당자·기한을 기록합니다. 체크리스트는 작성만 했으며 공급사에 발송하지 않았습니다.</div><p>설치 전에는 모델·호환·배선·HDD·도구·계정·등록 유형을 확정하고, 운영 전에는 영상·재생·분석 기준·구역·시간대·파일 출력까지 확인합니다. 검수 기준과 허용 오차는 공급사가 시험 조건과 수치로 제시하고 합의해야 합니다.</p>'''
    sources='''<p class="reference">화면 근거: <a href="https://yd.yunding360.com/V1/work">Workbench</a> · <a href="https://yd.yunding360.com/V1/stores/list">매장</a> · <a href="https://yd.yunding360.com/V1/equipment/list">장치</a> · <a href="https://yd.yunding360.com/V1/videoAdmin/realTime">영상</a> · <a href="https://yd.yunding360.com/V1/realTimeCustomer">실시간 방문객</a> · <a href="https://yd.yunding360.com/V1/storeFlowPt">입점 개요</a> · <a href="https://yd.yunding360.com/V1/inStoreShoppingAnalysis/movingLineAnalysis">동선</a> · <a href="https://yd.yunding360.com/V1/storeInHot">히트맵</a> · <a href="https://yd.yunding360.com/V1/exportAccurateJz/config">내보내기</a>。로그인·권한·라이선스에 따라 메뉴가 달라질 수 있습니다.</p>'''
    return s10+s11+s12+section('13','supplier-check','공급사 회신·검수 체크리스트','문서로 해소된 요청은 삭제하고 남은 질문만 기록합니다.',lead+checklist+sources)

def build_checklist(css):
    rows=[]
    for id,g,p,title,q,proof in CHECKS:
        rows.append(f'''<tr id="{id}" data-id="{id}"><td><label><input type="checkbox" data-field="done" aria-label="{id} 검수 완료"> {id}</label><br><span class="tag">{p} · {g}</span></td><td><strong>{title}</strong>{evidence_html(id)}<p>{q}</p><small>요청 증거: {proof}</small></td><td><label>회신 상태<select data-field="state" aria-label="{id} 회신 상태"><option>미회신</option><option>제공 완료</option><option>부분 제공</option><option>미지원</option><option>해당 없음</option><option>추가 확인</option></select></label><label>근거 / 미지원 사유<textarea rows="3" data-field="evidence" aria-label="{id} 근거 자료" placeholder="파일명·버전·쪽/화면 또는 사유"></textarea></label><label>담당자 · 완료 예정일<input data-field="owner" aria-label="{id} 담당자와 예정일" placeholder="담당자 / YYYY-MM-DD"></label></td></tr>''')
    extra='''.print-value{display:none}main.reply{margin:0 auto;max-width:1280px;padding:40px 30px}.reply h1{font-size:34px;line-height:1.4}.reply table{table-layout:fixed}.reply th:first-child{width:115px}.reply th:last-child{width:34%}.reply td p{margin:7px 0;font-size:14px}.reply td small,.reply td label{font-size:12px}.reply select,.reply textarea,.reply td input:not([type=checkbox]){display:block;width:100%;border:1px solid #c7d8d5;border-radius:5px;padding:7px;margin:3px 0 10px;background:white;color:#172d35;font:inherit;font-size:13px}.reply textarea{resize:vertical}.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}.reply tr:has(input[type=checkbox]:checked){background:#edf7f3}.reply input[type=checkbox]{accent-color:#087e80;width:17px;height:17px}.reply .meta{margin:20px 0}@media(max-width:760px){main.reply{padding:20px 12px}.reply table{min-width:850px}.reply h1{font-size:27px}}@media print{@page{size:A4 landscape;margin:12mm}.reply input:not([type=checkbox]),.reply select,.reply textarea{display:none!important}.print-value{display:block;white-space:pre-wrap;overflow-wrap:anywhere;font-size:9pt;color:#172d35;padding:5px 0 10px}main.reply{padding:0;max-width:none}.toolbar{display:none}.reply table{font-size:9pt;min-width:0}.reply td{padding:8px}.reply textarea{min-height:60px}.reply td p{font-size:9pt}.reply input,.reply select,.reply textarea{font-size:9pt!important;color:#000!important}.reply tr{break-inside:avoid}}'''
    script=r'''(()=>{const key='dx-supplier-reply-v1',fields=[...document.querySelectorAll('[data-field]')],status=document.getElementById('reply-status');let saved={};try{saved=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch{}function id(e){return(e.closest('[data-id]')?.dataset.id||'meta')+'-'+e.dataset.field;}function update(){for(const e of fields.filter(x=>x.type!=='checkbox')){let mirror=e.nextElementSibling;if(!mirror||!mirror.classList.contains('print-value')){mirror=document.createElement('span');mirror.className='print-value';e.after(mirror);}mirror.textContent=e.value||'미기입';}document.getElementById('count').textContent=document.querySelectorAll('[data-field="done"]:checked').length+' / '+document.querySelectorAll('tr[data-id]').length+' 항목 검수 완료';}function save(){try{localStorage.setItem(key,JSON.stringify(Object.fromEntries(fields.map(e=>[id(e),e.type==='checkbox'?e.checked:e.value]))));status.textContent='현재 브라우저에 저장됨 · 전달 시 CSV 또는 인쇄/PDF를 사용하세요.';}catch{status.textContent='자동 저장 불가 · CSV 또는 인쇄/PDF로 보관하세요.';}update();}for(const e of fields){if(e.type==='checkbox')e.checked=!!saved[id(e)];else if(typeof saved[id(e)]==='string')e.value=saved[id(e)];e.addEventListener('input',save);e.addEventListener('change',save);}document.getElementById('csv').onclick=()=>{const q=s=>'"'+String(s??'').replace(/"/g,'""')+'"',safe=s=>/^[=+@\-\t\r]/.test(String(s))?"'"+s:s;const result=[['DX-1100 공급사 회신 체크리스트'],...fields.filter(e=>!e.closest('tr')).map(e=>[e.getAttribute('aria-label'),e.value]),[],['ID','검수 완료','우선순위/구분','요청 항목','회신 상태','근거/사유','담당자/예정일']];for(const row of document.querySelectorAll('tr[data-id]'))result.push([row.dataset.id,row.querySelector('[data-field="done"]').checked?'예':'아니오',row.querySelector('.tag').textContent,row.children[1].innerText,...['state','evidence','owner'].map(x=>row.querySelector('[data-field="'+x+'"]').value)]);const blob=new Blob(['\ufeff'+result.map(r=>r.map(x=>q(safe(x))).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='DX-1100_공급사_회신.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};update();})();'''
    head='''<div class="eyebrow">SUPPLIER REVIEW · DX-1100 / YUNDVISION</div><h1>설치·온라인 콘솔 사용 가이드<br>공급사 미결 회신 체크리스트</h1><p class="small">v1.3 · 일반 설치·운영 31개 + 선택 API 5개 + 자체 한글 콘솔 개발 12개. 기존 항목 삭제/통합 근거는 <a href="공식문서_반영내역.md">공식 문서 반영 내역</a>을 참고하세요.</p><p>DX-1100 + 돔형 CCTV 최소 3대 + 공유기·PoE 스위치 + 1TB 권장 저장장치를 기준으로 요청드립니다. 제공된 공식 WEB/API 문서로 확인된 설명은 재요청에서 제외했습니다. 남은 질문만 현재 납품 형번·펌웨어에 맞춰 회신해 주세요.</p><div class="notice warn"><strong>현재 확인 상태 · 2026-10-31</strong>로그인 콘솔에서 조회 가능한 장치 0대, 매장 목록 없음, 영상 0/0, 분석 데이터 없음입니다. 원인은 미확정입니다. 메뉴·양식을 확인했으며 실제 등록·저장·영상·분석·내보내기 동작은 검증 전입니다.</div><p><strong>P0</strong>: 설치/운영/검수 전 필수. <strong>P1</strong>: 운영 기능·추가 범위 확인. F01~F05는 API 선택 연동 시, G01~G12는 자체 한글 콘솔 개발 시 적용합니다. 미지원·해당 없음도 사유와 대안을 회신해 주세요. <strong>왼쪽 검수 완료 체크는 발주자가 증거와 실제 결과를 확인한 후 표시</strong>합니다. 공급사의 ‘제공 완료’가 자동 검수 합격을 의미하지 않습니다.</p>'''
    head+='''<div class="notice" id="custom-console"><strong>추가 요청 · 자체 한글 WEB 콘솔 개발·연동 (G01~G12)</strong>공급사 API를 이용해 국내 운영자용 한글 콘솔을 별도로 개발하려고 합니다. <a href="#G01">자체 콘솔 개발 12개 항목으로 이동 ↓</a> · <a href="#F01">기존 API 연동 5개 항목으로 이동 ↓</a><br>F01~F05의 개통·인증·지표·한도·영상 검수는 유지하고, G01~G12에서 개발/고객 제공 허용·기능 대응·권한 격리·추가 API/SDK·데이터 이용·공동 검수·유지보수를 확인합니다. 각 기능은 지원/추가 계약/기존 콘솔 전용/미지원으로 구분하고 근거·비용·담당자·기한을 회신해 주세요. 모든 기능을 자체 콘솔에서 대체할 수 있다고 전제하지 않습니다. G 항목의 P0는 해당 개발 범위 확정·착수 전 확인을 뜻합니다.</div>'''
    meta='<div class="form-grid meta">'+''.join(f'<label>{label}<input data-field="{key}" aria-label="{label}" placeholder="{ph}"></label>' for key,label,ph in [('supplier','공급사 / 담당자','업체 / 담당자'),('site','현장 / 실제 형번','매장 / DX-1100 세부 형번'),('due','회신 요청일','YYYY-MM-DD'),('version','실제 회신일 / 자료 버전','YYYY-MM-DD / 버전')])+'</div>'
    how='''<div class="notice"><strong>작성·전달 방법</strong>입력은 이 브라우저에만 저장됩니다. <b>HTML 파일 자체에는 입력 결과가 기록되지 않습니다.</b> 작성 후 ‘회신 CSV 다운로드’ 또는 ‘인쇄 / PDF 저장’ 결과를 회신해 주세요. 긴 설명은 별도 첨부하고 근거 칸에는 파일명·쪽을 적습니다. 비밀번호·장치 key는 별도 안전한 경로로 인계합니다.</div>'''
    end='''<div class="notice"><strong>공통 제출 형식</strong>① 최신 한국어 PDF/HTML ② 포트별 배선도·모델/네트워크/호환표 ③ 공식 프로그램·플러그인과 버전 ④ 초기 설치부터 분석·파일 출력까지 시연 영상 ⑤ 검수 결과·미결·담당자·기한. 각 설정에는 입력값 출처·저장 방법·정상 표시·오류 조치를 포함해 주세요.</div><p class="small"><a href="AI_CCTV_설치_매뉴얼.html">설치·콘솔 통합 매뉴얼</a> · <a href="https://yd.yunding360.com/V1/work">온라인 콘솔</a>. 공급사 발송 전 검토용입니다. 로그인 정보·조직명·시리얼번호·key는 포함하지 않았습니다.</p>'''
    html='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DX-1100 공급사 회신 체크리스트</title><style>'+css+extra+'</style></head><body><main class="reply">'+head+meta+how+'<div class="toolbar"><button onclick="window.print()">인쇄 / PDF 저장</button><button id="csv">회신 CSV 다운로드</button><strong id="count"></strong></div><p class="small" id="reply-status" role="status">입력 내용은 현재 브라우저에 저장됩니다.</p><div class="table-wrap"><table><thead><tr><th>검수 / ID</th><th>공급사 요청 질문 / 제출 증거</th><th>공급사 회신</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'+end+'</main><script>'+script+'</script></body></html>'
    (ROOT/'DX-1100_공급사_설치_콘솔_체크리스트.html').write_text(html)
    md='# DX-1100 설치·온라인 콘솔 공급사 회신 체크리스트\n\n공급사 담당자님께, 공식 WEB/API 문서로 해소된 설명은 제외했습니다. 남은 31개 일반 요청, 5개 선택 API 요청, 12개 자체 한글 콘솔 개발 요청을 납품 모델·펌웨어 기준으로 회신해 주세요. 삭제/통합 근거는 [공식 문서 반영 내역](공식문서_반영내역.md)에 정리했습니다.\n\n구성: DX-1100 + 돔형 CCTV 최소 3대 + 공유기·PoE 스위치 + 1TB 권장 저장장치.\n\n점검일: 2026-10-31. 조회 가능한 장치 0대·매장 없음·영상 0/0·분석 데이터 없음. 원인 미확정이며 실제 등록·저장·재생·분석·내보내기는 미검증입니다.\n\nP0: 설치/운영/검수 전 필수. P1: 운영 기능·추가 범위 확인. F01~F05는 API 선택 연동 시, G01~G12는 자체 한글 콘솔 개발 시 적용합니다. 완료 체크는 발주자가 증거를 검수한 후 표시합니다.\n\n공급사/담당자: ____ / 현장·형번: ____ / 회신 요청일: ____ / 회신일·자료 버전: ____\n'
    for id,g,p,title,q,proof in CHECKS:
        if id=='G01':
            md+='\n## 자체 한글 WEB 콘솔 개발·연동 추가 요청 (G01~G12)\n\n공급사 API를 이용한 국내 운영자용 한글 콘솔 개발을 검토하고 있습니다. 기존 F01~F05와 함께 회신해 주세요. 각 기능은 지원/추가 계약/기존 콘솔 전용/미지원으로 구분하고 근거·비용·담당자·기한을 제시해 주세요. G 항목의 P0는 해당 개발 범위 확정·착수 전 확인입니다.\n'
        md+=f'\n- [ ] **{id} · {p} · {g} / {title}**\n\n  요청: {q}{evidence_md(id)}\n\n  제출 증거: {proof}\n\n  회신 상태: 미회신 / 제공 완료 / 부분 제공 / 미지원 / 해당 없음 / 추가 확인\n\n  근거 파일·버전·쪽 / 사유: ____\n\n  담당자·완료 예정일: ____\n'
    md+='\n공통 제출: 최신 한국어 PDF/HTML, 배선도·호환/네트워크 표, 공식 프로그램·버전표, 전체 시연 영상, 검수 결과·미결 목록. 비밀번호·장치 key는 별도 안전한 경로로 인계합니다.\n\n화면 근거: https://yd.yunding360.com/V1/work 및 실제 열람한 하위 메뉴. 메뉴 존재가 기능·라이선스·장치 호환·정상 동작의 보장은 아닙니다. 발송 전 검토용입니다.\n'
    (ROOT/'DX-1100_공급사_설치_콘솔_체크리스트.md').write_text(md)

def extend(html):
    css=re.search(r'<style>(.*?)</style>',html,re.S).group(1)
    write_notes(CHECKS)
    build_checklist(css)
    html=html.replace('<footer class="footer">',supplement()+'<footer class="footer">',1)
    nav=''.join(f'<a href="#{id}"><span class="navnum">{n}</span>{label}</a>' for n,id,label in [('10','console','온라인 콘솔 개요'),('11','console-setup','매장·장치 등록'),('12','console-use','조회·동선·내보내기'),('13','supplier-check','공급사 회신 체크')])
    html=html.replace('</nav>',nav+'</nav>',1).replace('INSTALLATION MANUAL · V1.0','INSTALLATION & CONSOLE · V1.1')
    html=html.replace('DX-1100 설치하기','DX-1100 설치·사용하기')
    html=html.replace('<title>AI CCTV · 현장 설치 가이드</title>','<title>AI CCTV · DX-1100 설치·온라인 콘솔 사용 매뉴얼</title>')
    html=html.replace('· 원본 2종 재구성<br>','· 원본 2종 + 로그인 콘솔 점검 반영<br>')
    html=html.replace('클라우드 등록, 방문객 집계 기준·중복 처리, 구역 보정·정확도 검증은 이 원본만으로 확정할 수 없습니다.','PDF만으로는 클라우드·집계·구역 설정을 확정할 수 없습니다. 이번 콘솔 점검 내용과 한계는 10~13단계에 추가했습니다.')
    html=html.replace('설치·운영 가이드 보강 요청 자료 열기 ↗','초기 설치 가이드 보강 요청 자료 ↗')
    html=html.replace('플랫폼 URL·장치 바인딩·분석 대시보드 확인 절차는 공급업체에서 받아야 합니다.', '현재 콘솔 URL·등록 양식·조회 메뉴를 직접 확인한 내용은 10~13단계를 참고하세요. 실제 장치 바인딩과 분석 결과는 공급업체 테스트 환경에서 검수해야 합니다.')
    html=html.replace('노트북에서 영상·저장·동선 분석 설정을 확인하는 현장용 가이드입니다.', '노트북 설정과 온라인 콘솔의 매장·장치 등록, 영상·방문객·동선·보고서 조회를 안내하는 가이드입니다.')
    return extend_official(html, css)
