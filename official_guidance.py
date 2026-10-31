"""Supplier documentation reconciliation. No credentials or live API calls."""
from pathlib import Path
from html import escape
import re

ROOT=Path(__file__).parent
WEB='https://yunding360.yuque.com/vsgys3/xky7zh/'
API='https://openapi-docs.yunding360.com/'
SOURCES=[
('W01','작업공간','iuqvr9mi2k9i8fdl','계정별 모듈 표시, 이름을 드래그해 정렬하고 X로 숨기는 개인화.'),
('W02','영상 감시','oamdlry4sufoafi6','매장 선택·동기/비동기 재생·1~8배속·1/4/9화면·캡처·1/5/10/30분 녹화 다운로드.'),
('W03','매장 구조','gn4gmlmkofdvnuhr','매장번호는 기업 내 고유값. 주소는 좌표/날씨/현장 순찰 위치, 상세 주소는 층·호수. 영업시간과 내부 분구 관리.'),
('W04','장치 목록','dbmx9q7916wzx8g4','구매 장치 SN으로 기능에 맞는 유형·매장 연결. 권한 상속 시 매장 접근자가 장치에도 접근. 최근 7일 오프라인 로그와 템플릿 일괄 등록.'),
('W05','실시간 방문객','rbyzcwoq7bg7sd3w','기업/매장·출입구별 흐름, 날짜·태그·지역·매장·구역 필터와 순위.'),
('W06','매장 방문객 개요','no8p8lumv9r976gg','방문객·총/평균 체류·추이·체류시간 분포, 기간·매장·전기/전년 비교와 표 출력.'),
('W07','매장 내부 흐름 개요','sygu9dh6o80d0azg','방문객 추이·평균 체류·체류시간 분포와 표 출력.'),
('W08','고객 동선 분석','hvor417if3b9suxc','날짜·매장별 궤적/구역 비율과 구역 간 고객 흐름의 Sankey 도식.'),
('W09','관심도 등급 분석','dqnanedqtr8ayx5f','구역 관심 고객·관심 시간의 추이 및 여러 구역 간 비교. 임계값 수치는 없음.'),
('W10','매장 구역 히트맵','nmvw9rt6ihvthcz4','매장 평면도 위 구역별 관심 고객·관심 시간 분포. 도면 등록/축척 절차는 미확인.'),
('W11','데이터 출력','spesqqsk18eibsis','기간·출력 차원·장소 유형/선택·지표 유형으로 방문객/매출 세부 데이터를 출력.'),
]
APISOURCES=[
('P01','접속 안내',API,'개통·공통 헤더·오류·캐시·페이지 모델'),
('P02','인증',API+'auth/','전용 account·enterpriseCode·password, 토큰 발급/갱신'),
('P03','방문객',API+'accCustomerStoreFlow/','매장 목록, v2 방문객·체류시간 조회, 지표 필드'),
('P04','관심도',API+'attention/','매장·구역 목록, 관심도 조회, 밀리초 입력/초 단위 평균'),
('P05','히트맵',API+'area_heat/','기본 지도·좌표·열값, GET/body 불일치 확인'),
('P06','매장',API+'store/','매장 목록·0 기반 페이지·상태/능력 필드'),
('P07','장치',API+'device/','장치 목록·채널·online·capabilityList·가시성'),
('P08','영상',API+'video/','SN·채널별 재생 URL과 기록 조회'),
]
# Resolved explanations move to the usage guide; remaining parts are consolidated.
REMOVED={
'B08':('문서 설명 해소','장치 권한 상속은 W04, Visible=true/false는 P07에서 확인. 실제 구역 매핑은 B04, 계정별 권한 검수는 B01에 통합.'),
'C01':('기본 정의 반영·잔여 통합','API 필드 의미·단위를 가이드에 반영. 고유 집계/제외는 C02, WEB↔API 정확한 대응은 F03에 남김.'),
'C06':('기본 사용법 반영·잔여 통합','기간·매장·전기/전년 비교는 W05~W07에 안내. 시간대·마감은 B03, 비교 정렬/집계 경계는 F03에 통합.'),
'D01':('사용 절차 해소·검수 분리','영상 선택·재생·배속·출력은 W02에 안내. 실행 환경은 A05, 저장 위치는 D06, 실물 검수는 E05에 남김.'),
'D02':('조작법 해소·호환 통합','캡처·PTZ·배치·전체화면 조작은 W02에 안내. PTZ 등 실제 모델 지원은 A02로 통합.'),
'E02':('포괄 요청을 개별 미결로 재편','이미 제공된 WEB 매뉴얼을 다시 일괄 요청하지 않음. DX 전용 도구·설정·녹화·현장 결과는 A05/A07/A09/E05에서 구체 요청.'),
}
REVISED={
'A02':'공식 가이드에 기능은 설명되어 있습니다. 이번 DX-1100·카메라·펌웨어 조합에서 영상·방문객·핫존·동선·PTZ별 수행 위치, 타사 ONVIF 지원, 실제 라이선스/요금을 모델별로 확정해 주세요.',
'B01':'기본 매장 권한 상속 원리는 확인했습니다. 이번 운영자/관리자 계정이 실제로 볼 매장·장치·분석·다운로드 범위와 활성 모듈·요금을 확정하고 권한별 조회 결과를 제시해 주세요.',
'B02':'매장번호·주소·상태·영업시간의 일반 의미는 확인했습니다. 한국 매장 주소를 지도/좌표에 등록하는 지원 방식, 한국 지역·날씨/위치 기능의 제약과 대체 입력법만 안내해 주세요.',
'B03':'영업시간이 운영시간 통계의 기준인 점은 확인했습니다. 한국 시간대·자정 넘김/휴일·일괄 변경·하루 마감과 변경 전후 과거 통계 처리 기준을 확정해 주세요.',
'B04':'내부 분구로 장치를 관리하고 분구 통계를 내는 기능은 확인했습니다. 실제 도면 업로드·축척·층/분구 생성·카메라 매핑/보정·변경/삭제 영향의 화면을 제공해 주세요.',
'B06':'SN은 본체·포장 라벨에서 확인하는 것으로 해소됐습니다. 이번 모델의 key 필수 여부·확인/발급 위치, 기존 계정 바인딩 해제·재등록·교체 오류 처리만 안내해 주세요.',
'C02':'고유 방문객 제외 항목은 콘솔 도움말에서 확인했습니다. 실제 설정 위치·기본 임계값·중복 식별 방식·일/매장/카메라 범위와 직원·배달원·단기 체류·연령 제외의 시험 결과를 제공해 주세요.',
'C03':'입점률의 표시 산식과 API 평균 체류시간의 초 단위는 확인했습니다. 입장/통행 선행 조건·분모 0 처리·체류 시작/종료·제외/상한 및 WEB와 API의 표본 일치를 확정해 주세요.',
'C05':'공식 문서/API의 관심 고객 수·연인원·평균 관심시간(초) 설명은 확인했습니다. Wandering/Interested/Purchase-inclined의 임계값·등급 규칙과 실제 히트맵 범례·좌표 보정만 확정해 주세요.',
'D03':'기간·차원·장소·지표 선택을 통한 출력 절차는 확인했습니다. 실제 파일 형식·인코딩·열 정의·최대 행/기간·오류 처리와 동일 조건의 WEB 합계 대조 파일을 제공해 주세요.',
'D04':'장치별 최근 7일 오프라인 조회 기능은 확인했습니다. 이번 계정의 경보·Data Alert 수신 대상/조건, 중복·복구 알림, 보관 기간·비용과 실제 시험 결과를 제공해 주세요.',
'D05':'일반 조회/로그 메뉴 설명의 재작성은 불필요합니다. 실제 로그 보관·필요 권한, 펌웨어 업데이트·설정 백업/복구·장치 교체·지원 연락처/SLA의 납품 기준을 안내해 주세요.',
}
EVIDENCE={
'B01':('W04','장치 권한 상속의 일반 원리 확인'),
'B02':('W03','매장 기본 필드 의미·고유 번호 확인'),
'B03':('W03','영업시간이 운영시간 통계 기준임을 확인'),
'B04':('W03','분구별 관리·통계 기능 확인'),
'B06':('W04','SN은 본체·포장 라벨에서 확인'),
'C03':('P03','평균 체류시간·총 체류시간의 초 단위 확인'),
'C05':('P04','관심 고객·연인원·평균시간 필드 확인'),
'D03':('W11','내보내기 필터·차원·지표 절차 확인'),
'D04':('W04','장치별 최근 7일 오프라인 조회 설명 확인'),
}
NEW_CHECKS=[
('F01','API 선택 연동','P0','개통·계정·요금','API를 사용할 경우 이번 기업의 개통 여부·허용 기능·요금/쿼터·전용 account/enterpriseCode/password 발급과 테스트 권한을 확인해 주세요. 콘솔 계정·장치 key와 구분해 주세요.','개통/권한표·테스트 계정 인계 절차(비밀값 별도)'),
('F02','API 선택 연동','P0','인증 헤더·수명','문서는 tokenType+accessToken 결합과 공백 없는 예시를 제시합니다. 실제 Authorization 문자열 형식, expiresIn/refreshTokenExpiresIn 단위, 캐시·갱신·권한 오류 재시도 기준을 성공 요청 예시로 확정해 주세요.','비밀값 제거한 성공 헤더·토큰 수명·오류 처리 예시'),
('F03','API 선택 연동','P0','지표·ID·시간 대응','WEB의 unique/total 방문객·체류/관심 지표와 API 필드, store/group/area/channel ID를 매핑해 주세요. 날짜/밀리초·한국 시간대·기간 끝 포함·비교 기간·갱신 지연을 맞춘 샘플을 제시해 주세요.','동일 기간 WEB↔API↔내보내기 대조표·ID표'),
('F04','API 선택 연동','P0','문서 모호점·한도','v2 getAvgTimeAndFlowNum의 storeIds 타입(uuid 단일/배열), GET area/heat/data/attention의 body/query 위치를 확정하고 페이지 크기·최대 조회기간·호출한도·재시도/지연 정책을 제공해 주세요.','정정 스키마·실행 성공 샘플·한도표'),
('F05','API 선택 연동','P0','영상·통합 검수','videos/{sn}/{channelNo}의 실제 DX 채널 번호, RTMP 재생의 현대 브라우저 지원 방식·URL 만료/권한/저장 유형을 확정해 주세요. 읽기 전용 샘플로 페이지 누락·데이터 갱신·오류·영상 접근·WEB 대조를 검수해 주세요.','지원 플레이어/전송 방식·URL 수명·마스킹된 검수 결과'),
]

def source_url(code):
    for c,title,slug,note in SOURCES:
        if c==code:return WEB+slug
    return next(url for c,title,url,note in APISOURCES if c==code)

def evidence_html(id):
    if id not in EVIDENCE:return ''
    code,note=EVIDENCE[id]
    return f'<p class="small"><a href="{source_url(code)}">{code} 공식 문서 확인</a>: {escape(note)}. 아래 요청은 미해결 부분입니다.</p>'

def evidence_md(id):
    if id not in EVIDENCE:return ''
    code,note=EVIDENCE[id]
    return f'\n\n  문서 확인: [{code}]({source_url(code)}) — {note}. 확인된 설명은 재요청하지 않습니다.'

def revise_checks(checks):
    titles={'B02':'한국 주소 지원','B06':'key·바인딩','C03':'입점률 경계·체류 표본','D05':'유지보수·로그 보관'}
    proofs={'B02':'한국 주소 시연·지원 제약/대체 입력','B06':'key 조건·해제/재등록 절차','C03':'분모 0·체류 표본 검증 예시'}
    return [(c[0],c[1],c[2],titles.get(c[0],c[3]),REVISED.get(c[0],c[4]),proofs.get(c[0],c[5])) for c in checks if c[0] not in REMOVED]+NEW_CHECKS

def table(head,rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in r)+'</tr>' for r in rows)+'</tbody></table></div>'

def link(code,label=None):
    return f'<a href="{source_url(code)}" target="_blank" rel="noopener">{escape(label or code)} ↗</a>'

def section(n,id,title,sub,body):
    return f'<section class="section" id="{id}"><div class="section-head"><span class="number">{n}</span><div><h2>{title}</h2><p>{sub}</p></div></div>{body}</section>'

def web_section():
    body=f'''<div class="notice"><strong>공급사 WEB 문서를 반영한 사용 순서</strong>{link('W01','공식 WEB 가이드')} · 기존 10~12단계는 실제 로그인 UI 점검, 이 절은 공급사 문서 근거입니다. 중국어 문서와 현재 영문 UI의 메뉴 구조가 달라 기능 목적을 기준으로 찾으세요. 모든 하위 문서를 완역한 것이 아니라 설치·주요 사용 업무에 관련된 11개 본문을 검토했습니다. 문서에 있는 기능도 이번 장치·권한·라이선스에서 실제 지원하는지는 별도 검수합니다.</div>
    <h3>01 · 매장·장치·분구 준비</h3><ol class="steps"><li><strong>System Management → Stores architecture에서 조직·매장을 구성합니다.</strong><p>지역 구조 아래 매장을 만들고 기업 내 고유 Store number를 부여합니다. Address는 지도 좌표·날씨·현장 순찰 위치, Detailed address는 층·호수에 해당합니다. 상태는 운영/중지/폐쇄이며 실제 영업시간이 통계 범위의 기준입니다. 한국 지도 입력·자정 넘김·시간대는 공급사 미결 사항입니다.</p></li><li><strong>내부 분구를 만들고 장치를 연결합니다.</strong><p>분구는 장치 구역 관리와 구역별 집계에 사용됩니다. 실제 도면 업로드·축척·다중 카메라 보정은 별도 안내가 필요합니다. Device Config에서 본체/포장 라벨의 SN과 실제 기능에 맞는 유형·매장을 선택합니다. DX-1100 등록 유형과 key 조건은 아직 미확정입니다.</p></li><li><strong>권한 상속과 목록 필터를 확인합니다.</strong><p>Inherit store access rights를 체크하면 해당 매장 접근자가 장치 접근권한도 상속합니다. 해제하면 이 방식의 권한 부여가 되지 않으므로 기존의 별도 권한까지 삭제되는 것으로 해석하지 마세요. 장치 목록은 매장 권한 범위 내 결과이며 이름/SN·유형·온라인·운영상태·Visible 필터를 확인합니다. API의 display=true/false는 가시성을 뜻합니다.</p></li></ol><p class="reference">근거: {link('W03','매장 구조')} · {link('W04','장치 목록')} · {link('P07','장치 API')}. 화면에서 실제 저장·권한 변경은 수행하지 않았습니다.</p>
    <h3>02 · 실시간 영상 → 녹화 재생 → 필요한 구간 저장</h3><ol class="steps"><li><strong>Video surveillance에서 권한이 있는 매장·채널을 선택합니다.</strong><p>매장명·조직·즐겨찾기·태그로 찾습니다. Favorite store는 즐겨찾기, Store traffic은 당일 방문객 추이, Stop all은 열린 영상 종료입니다.</p></li><li><strong>녹화 시각을 정하고 동기/비동기 재생을 선택합니다.</strong><p>동기 재생은 현재 선택 창의 재생 시각을 여러 창에 적용합니다. 비동기는 각 창을 독립 제어합니다. 공식 가이드의 배속은 1×~8×, Layout은 1/4/9화면입니다. PTZ는 지원 카메라에서만 사용합니다. Full screen은 ESC로 종료합니다.</p></li><li><strong>스냅샷 또는 녹화 구간을 저장합니다.</strong><p>Capture all은 현재 재생 중인 화면을 캡처하며 우측에서 확인·다운로드할 수 있습니다. 녹화 다운로드는 재생 시작 시각부터 1/5/10/30분 구간을 선택하는 방식입니다. 방문객/POS가 연계되면 타임라인에 사건 시각을 표시할 수 있습니다. 실제 녹화 존재·다운로드 권한·파일 재생은 E05에서 검수합니다.</p></li></ol><p class="reference">근거: {link('W02','영상 감시 공식 사용법')}. 지원 브라우저/플러그인·모델별 지원은 A02/A05에 남깁니다.</p>
    <h3>03 · 방문객·체류·동선·히트맵 조회</h3>'''
    body+=table(['업무','공식 문서의 사용 순서','해석·주의'],[
    ('실시간 흐름','Accurate traffic → Real-time traffic. 날짜·매장 태그·지역/매장·분구를 선택해 기업/매장·출입구별 흐름과 순위를 봅니다.','근거 '+link('W05')+'. 전체 기업을 볼 권한인지 확인.'),
    ('방문객·체류','Traffic analysis의 개요 화면에서 기간·지역/매장·전기/전년 비교를 지정합니다. 고객 수·총/평균 체류·추이·체류 분포를 확인하고 표로 전환해 출력합니다.','근거 '+link('W06')+' / '+link('W07')+'. API 필드와 unique 지표 대응은 자동 확정하지 않음.'),
    ('동선·구역 흐름','현재 UI는 Customer Mapping → Moving line analysis. 공식 문서는 店内动线 → 顾客动线分析에서 궤적·구역 비율과 고객 흐름 Sankey를 설명합니다.','근거 '+link('W08')+'. 현재 4개 탭과 문서 도식은 버전 차이가 있을 수 있음. UI의 10초 표본 규칙은 C04에서 확인.'),
    ('구역 관심도·히트맵','날짜·매장/구역을 선택해 구역별 관심 고객 수·평균시간의 추이/비교 또는 매장 평면도 위 분포를 확인합니다.','근거 '+link('W09')+' / '+link('W10')+'. 등급 임계값·도면 보정은 C05/B04 미결.'),
    ])
    body+=f'''<h3>04 · 맞춤 데이터 출력과 일상 점검</h3><p>현재 UI의 <strong>Accurate traffic → Export data → Export configuration</strong>에서 기간, 시간 차원, 장소 유형/대상, 지표를 정하고 Preview → Export를 진행합니다. 공식 문서 경로는 精准客流 → 数据助手 → 数据导出이며 방문객·매출 세부 데이터의 맞춤 출력을 설명합니다. 파일 형식·최대 기간/행 수는 문서에서 확정되지 않아 D03에 남겼습니다.</p><p>장치 목록의 최근 7일 오프라인 로그와 목록 필터로 연결 문제를 점검하고, 작업대 모듈이 안 보이면 계정 권한과 개인화로 숨긴 여부를 확인합니다. 작업대는 모듈명을 드래그해 정렬하고 X로 숨기는 기능이 문서에 설명되어 있습니다. 화면 배치 개인화와 분석 기능 미지원은 구분하세요.</p><p class="reference">근거: {link('W11','데이터 출력')} · {link('W04','오프라인 로그/일괄 등록')} · {link('W01','작업대 개인화')}.</p>'''
    return section('14','official-web','공식 WEB 매뉴얼로 정리한 사용가이드','이미 설명된 조작법은 재요청하지 않고, 실제 환경에서의 검수만 남깁니다.',body)

def api_section():
    body=f'''<div class="notice"><strong>API는 선택 연동입니다</strong>매장 담당자가 콘솔만 사용하는 경우 API 개통·개발은 설치 필수 단계가 아닙니다. 자체 보고서/시스템을 연계할 때 담당 개발자가 진행합니다. {link('P01','접속 안내')} · {link('P02','인증 문서')}<br>API 개통과 전용 접속 정보는 공급사가 사전 발급합니다. 본 문서 작업에서는 발급·인증·실제 호출을 수행하지 않았습니다.</div>
    <h3>준비 순서</h3><ol class="steps"><li><strong>API 사용 범위와 전용 계정을 확정합니다.</strong><p>기업의 API 개통 여부·기능·요금·권한을 확인하고 공급사 발급 account, enterpriseCode, password를 안전한 경로로 받습니다. 콘솔 계정이나 장치 key를 그대로 API 자격정보라고 가정하지 않습니다.</p></li><li><strong>서버에서 토큰을 발급·캐시합니다.</strong><p>POST <code>https://yd.yunding360.com/openapi/oauth/token</code>, JSON 필드 <code>account</code>·<code>enterpriseCode</code>·<code>password</code>. HTTPS·UTF-8 JSON을 사용하고 토큰 응답의 수명에 맞춰 캐시합니다. 비밀값은 HTML·브라우저 저장소·Git 저장소에 넣지 않습니다.</p></li><li><strong>엔드포인트별 버전과 인증 형식을 확인합니다.</strong><p>일반 안내는 <code>api-version: v1</code>, 방문객/체류 조회는 <code>v2</code>를 지정합니다. JSON 본문 요청에는 <code>Content-Type: application/json</code>을 설정합니다. 인증 문서는 tokenType+accessToken 결합 및 공백 없는 예시를 제시하므로, 실제 Authorization 공백·접두어 형식은 공급사의 성공 예시로 확정합니다.</p></li><li><strong>매장·구역·채널 ID를 얻고 읽기 조회부터 검수합니다.</strong><p>0 기반 페이지와 content/metadata를 확인해 전체 페이지를 처리합니다. 서비스별 매장 목록의 대상이 다를 수 있습니다. 같은 한국 현장 기간의 WEB·내보내기·API 숫자를 대조한 뒤 운영에 사용합니다.</p></li></ol>'''
    rows=[
    ('매장/장치','GET /stores · GET /devices/page','v1 기본 · page/size. 장치 online·display·capabilityList·channel 확인. '+link('P06')+' '+link('P07')),
    ('방문객 대상 매장','GET /accStore/store/allList','v1 · 분석 서비스 대상 매장 목록. '+link('P03')),
    ('방문객·체류','POST /accStore/getAvgTimeAndFlowNum','v2 · yyyy-MM-dd, DAY/HOUR, storeIds 또는 groupId, page/size. storeIds 단일/배열 표기 모호점은 F04. '+link('P03')),
    ('관심 구역·관심도','GET /attention/{storeId}/storeArea/list · POST /attention/analyse/data','v1 기본 · startTime/endTime은 밀리초, 평균 관심시간은 초. '+link('P04')),
    ('히트맵','GET /area/heat/map/storeId/{storeId} · POST /area/heat/data','v1 기본 · 기본 이미지 크기와 [X,Y,열값], 입력 시간은 밀리초. 지도 좌표/보정은 미결. '+link('P05')),
    ('영상 주소','GET /videos/{sn}/{channelNo}','v1 기본 · IPC는 channelNo=0으로 명시. DX 채널 번호는 실물 확인. RTMP/재생 URL을 브라우저에서 바로 재생 가능하다고 가정하지 않음. '+link('P08')),
    ]
    body+=table(['목적','문서에 확인된 상대 경로','조건·근거'],rows)
    body+='''<p class="small">모든 상대 경로의 기준 주소는 <code>https://yd.yunding360.com/openapi</code>입니다. GET/POST는 HTTP 메서드이며, POST 중에도 조회 API가 있습니다. 위 표는 실행 가능한 완성 요청 예제가 아니라 확인된 경로 안내입니다.</p>'''
    body+=table(['방문객 v2 응답 필드','문서 의미'],[
    ('totalPassTimes / indoorTimes / outdoorTimes','통행 / 입장 / 퇴장 연인원'),
    ('totalCustomerPersonNum / customerPersonNum','전체 고객 수 / 고객 수. 콘솔 unique와의 동일성·제외 범위는 별도 대조.'),
    ('totalWanderTime / avgWanderTime','총 이동·체류시간 / 평균 체류시간. 문서 단위는 초.'),
    ('processTime','데이터 최종 처리 시각. 실제 형식·시간대·지연은 샘플로 확인.'),
    ])
    body+=f'''<h3>실수하기 쉬운 차이</h3><ul><li>날짜 문자열과 밀리초 타임스탬프, 응답의 초 단위를 섞지 않습니다. 한국 시간대·기간 끝 포함 기준은 F03에서 확인합니다.</li><li>일반 API의 401/403은 문서상 토큰 재발급 후 재요청 대상이지만, 인증 자체의 401/403은 반복하지 말고 계정·권한을 확인합니다. 권한 오류의 무한 재시도는 피하고 캐시·호출 한도 정책을 합의합니다.</li><li>히트맵 <code>GET /area/heat/data/attention</code>은 문서에 파라미터 위치가 body로 표기됩니다. GET/query로 임의 수정하지 말고 공급사에 정확한 요청을 확인합니다.</li><li>영상 URL에는 토큰·key 등 접근정보가 들어갈 수 있습니다. 원문 URL·토큰을 저장소/공유 문서에 기록하지 않습니다. 문서의 RTMP와 실제 브라우저 플레이어 호환·만료·채널 매핑은 F05의 검수 대상입니다.</li></ul><p class="reference">근거: {link('P01')} · {link('P02')} · {link('P03')} · {link('P04')} · {link('P05')} · {link('P08')}. 문서 명세 확인과 실제 요청 성공은 구분합니다.</p>'''
    return section('15','api-guide','API 연동 준비·조회·검수 가이드','선택 연동 담당자용 · 비밀값이나 실제 요청 성공 기록은 포함하지 않습니다.',body)

def reconciliation_section():
    rows=[(id,reason,escape(detail)) for id,(reason,detail) in REMOVED.items()]
    body=table(['기존 ID','이번 처리','공식 문서 반영 / 남긴 미결'],rows)
    body+='''<div class="notice"><strong>활성 요청은 일반 설치·운영 31개 + 선택 API 연동 5개 = 36개</strong>설명된 조작법은 사용가이드로 옮겼습니다. 일부 항목은 전부 해소된 것이 아니라 남은 질문을 다른 항목으로 통합했습니다. 회신·검수 체크는 자동으로 완료 처리하지 않습니다. API를 사용하지 않으면 F01~F05는 사유를 적고 해당 없음으로 처리합니다.</div>'''
    body+=table(['ID','읽은 공식 WEB 본문','확인 내용'],[(c,link(c,title),escape(note)) for c,title,slug,note in SOURCES])
    body+=table(['ID','API 문서','검토 범위'],[(c,link(c,title),escape(note)) for c,title,url,note in APISOURCES])
    body+='<p class="small">확인일 2026-10-31. 공식 문서 페이지의 수정일은 항목마다 다르며, 실제 납품 펌웨어/현재 영문 UI와 일치한다는 보장은 아닙니다. 문서로 해소되지 않은 key·형번·분석 호환·한국 지역 지원·집계 임계값·테스트 결과는 계속 요청합니다.</p>'
    return section('16','doc-reconciliation','해소된 요청과 남은 확인사항','삭제·통합 근거와 검토한 공식 문서의 범위를 기록합니다.',body)

def extend_official(html,css):
    html=html.replace('<footer class="footer">',web_section()+api_section()+reconciliation_section()+'<footer class="footer">',1)
    html=html.replace('</nav>','<a href="#official-web"><span class="navnum">14</span>공식 WEB 사용법</a><a href="#api-guide"><span class="navnum">15</span>API 연동 준비</a><a href="#doc-reconciliation"><span class="navnum">16</span>요청사항 재정리</a></nav>',1)
    html=html.replace('INSTALLATION & CONSOLE · V1.1','INSTALLATION & CONSOLE · V1.2')
    html=html.replace('현재 실제 재생·다운로드·PTZ 지원·플러그인 필요 여부는 미검증입니다.','실제 재생·다운로드·모델별 PTZ/플러그인 지원은 미검증입니다.')
    html=html.replace('기존 계정 바인딩을 피하도록', '기존 계정 바인딩을 피하도록')
    html=html.replace('초기 설치 가이드 보강 요청 자료 ↗','최신 미결 요청 요약 ↗')
    html=html.replace('10~13단계', '10~16단계')
    html=html.replace('원본 2종 + 로그인 콘솔 점검 반영','원본 2종 + 로그인 콘솔 점검 + 공급사 WEB/API 문서 반영')
    html=html.replace('플랫폼 URL·계정·장치 등록 절차, 방문객 집계 기준·보정·검증 절차', '납품 계정·DX 등록 유형·key·구역 보정과 실제 집계 검수: 공식 문서로 해소되지 않은 항목만 요청')
    # Dedicated operator guide uses the same verified sections, without hardware chapters.
    parts=[]
    for id in ['console','console-setup','console-use','official-web']:
        match=re.search(r'<section class="section" id="'+id+r'">.*?</section>',html,re.S)
        if match:parts.append(match.group())
    standalone='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>YUNDVISION WEB 콘솔 사용가이드</title><style>'+css+'main{margin:0 auto!important;max-width:1120px;padding:30px 24px}@media print{main{padding:0}}</style></head><body><main><div class="topline"><span class="eyebrow">WEB CONSOLE GUIDE · V1.2</span><button onclick="window.print()">인쇄 / PDF 저장</button></div><h1>YUNDVISION WEB 콘솔 사용가이드</h1><p>공식 문서의 조작법과 실제 UI 점검을 구분합니다. 실제 장치·데이터 검수는 별도입니다. 아래 단계 번호는 통합 매뉴얼 기준이며, API 준비는 별도 링크에서 확인합니다.</p><p><a href="AI_CCTV_설치_매뉴얼.html">설치·사용 통합 매뉴얼</a> · <a href="DX-1100_공급사_설치_콘솔_체크리스트.html">공급사 미결 체크리스트</a> · <a href="API_연동_준비_가이드.md">API 연동 준비 원문</a></p>'+''.join(parts)+'</main></body></html>'
    (ROOT/'WEB콘솔_사용가이드.html').write_text(standalone)
    return html

def write_notes(checks):
    # A concise current request replaces the old, now stale supplier request draft.
    md='# DX-1100 공급사 미결 요청사항 요약 · v1.2\n\n공식 WEB 사용가이드와 API 문서를 반영하여 설명이 확인된 내용은 재요청에서 제외했습니다.\n\n일반 설치·운영 31개, 선택 API 연동 5개로 총 36개입니다. API 미사용 시 F01~F05는 해당 없음으로 회신해 주세요.\n\n상세 회신은 [미결 체크리스트 HTML](DX-1100_공급사_설치_콘솔_체크리스트.html) 또는 [Markdown](DX-1100_공급사_설치_콘솔_체크리스트.md)에 기록합니다.\n\n'
    for id,g,p,title,q,proof in checks:md+=f'- **{id} / {p} / {g} · {title}**: {q}\n\n'
    md+='## 삭제·통합 내역\n\n'
    for id,(reason,detail) in REMOVED.items():md+=f'- **{id} — {reason}**: {detail}\n\n'
    md+='## 제공받은 근거\n\n- [WEB 사용가이드]('+WEB+')\n- [API 문서]('+API+')\n\n검토일: 2026-10-31. 확인된 기본 설명과 실제 납품 환경의 검수 성공은 구분합니다. 이 요청서는 공급사에 발송하지 않았습니다.\n'
    (ROOT/'DX-1100_공급사_가이드_보강요청.md').write_text(md)
    notes='# 공식 문서 반영·미결 정리 기록\n\n기준일 2026-10-31. WEB 본문 11개와 API 분야 8개를 관련 범위에서 검토했습니다. 전체 지식베이스 151개 문서를 완역·검증한 것이 아닙니다.\n\n## 공식 WEB 본문\n\n'
    for c,title,slug,note in SOURCES:notes+=f'- [{c} {title}]({WEB+slug}): {note}\n\n'
    notes+='## API 명세\n\n'
    for c,title,url,note in APISOURCES:notes+=f'- [{c} {title}]({url}): {note}\n\n'
    notes+='## 활성 요청에서 삭제·통합한 기존 항목\n\n'
    for id,(reason,detail) in REMOVED.items():notes+=f'- **{id}: {reason}** — {detail}\n\n'
    notes+='## 검수 한계\n\n기존 콘솔 점검의 장치 0대·매장 없음 상태는 실물 분석 검수가 필요하다는 뜻이며, 이번 문서 검토로 해소되지 않았습니다. API 개통/인증/호출, 장치 등록, 운영 설정 변경은 실행하지 않았습니다. 공급사 요청 목록의 F01~F05는 API를 선택 연동할 때만 적용합니다.\n'
    (ROOT/'공식문서_반영내역.md').write_text(notes)
    api_md='''# YUNDVISION API 연동 준비 가이드\n\nAPI는 자체 시스템 연동을 선택할 때 담당 개발자가 진행합니다. 콘솔만 쓰는 매장 설치의 필수 요건이 아닙니다. 실제 호출은 수행하지 않았습니다.\n\n1. 공급사에 기업 API 개통·허용 모듈·요금·쿼터를 확인하고 전용 account / enterpriseCode / password를 별도 안전한 경로로 받습니다.\n2. HTTPS·UTF-8 JSON을 사용합니다. 기준 주소는 https://yd.yunding360.com/openapi/ 입니다.\n3. POST /oauth/token에 전용 자격정보를 JSON 본문으로 전달하는 명세입니다. 응답 accessToken·tokenType·refreshToken·수명 필드를 확인하고 서버에서 캐시합니다. HTML·브라우저 저장소·Git에 비밀값을 기록하지 않습니다.\n4. api-version은 공통 v1이지만 POST /accStore/getAvgTimeAndFlowNum은 v2입니다. JSON 본문 요청에는 Content-Type: application/json을 사용합니다.\n5. 문서의 Authorization은 tokenType+accessToken 결합, 예시는 공백 없는 형태입니다. 통상적인 Bearer 형식을 임의 적용하기 전에 성공 헤더를 공급사에서 받아 공백·접두어를 확정합니다.\n6. GET /stores, GET /devices/page, GET /accStore/store/allList로 대상 매장·장치와 권한을 확인합니다. 기본 페이지는 0부터이며 모든 content/metadata 페이지를 처리합니다.\n7. 방문객 v2는 yyyy-MM-dd·DAY/HOUR, 관심도와 히트맵은 밀리초 입력입니다. 방문객 총/평균시간과 attentionAvgDuration은 문서상 초입니다. 한국 시간대·끝 경계·비교 기간·처리 지연은 별도 합의합니다.\n8. storeIds가 단일 UUID인지 배열인지 표기 차이, GET /area/heat/data/attention의 body 표기는 실제 성공 스키마를 요청합니다. 최대 기간·크기·호출한도도 확인합니다.\n9. GET /videos/{sn}/{channelNo}는 IPC의 채널 0을 명시합니다. DX 채널 번호, RTMP/플레이어 호환·URL 만료·권한·저장 유형은 실제 장비로 검수합니다. 재생/녹화 URL은 비밀값이 포함될 수 있어 공유 로그에 남기지 않습니다.\n10. 일반 API 401/403은 토큰/권한 확인 후 제한적으로 재인증·재요청하고, 인증 자체의 401/403은 반복하지 않습니다. 최종적으로 동일 조건의 WEB·내보내기 파일·API 결과를 대조합니다.\n\n## 문서 필드와 WEB 지표 대조\n\n| 필드 | 공식 의미 | 검수 주의 |\n|---|---|---|\n| totalPassTimes / indoorTimes / outdoorTimes | 통행 / 입장 / 퇴장 연인원 | 집계선·기간·중복 조건 대조 |\n| totalCustomerPersonNum / customerPersonNum | 전체 고객 수 / 고객 수 | WEB unique와 자동으로 같다고 판단하지 않음 |\n| totalWanderTime / avgWanderTime | 총 체류·이동시간 / 평균 체류시간, 초 | 문자열/숫자 및 표본 범위 대조 |\n| attentionCustomerNum / attentionCustomerTimes | 관심 고객 수 / 관심 연인원 | 분구·중복 범위 대조 |\n| attentionAvgDuration | 평균 관심시간, 초 | 밀리초 입력과 혼동 금지 |\n\n## 근거와 미결 요청\n\n'''
    for c,title,url,note in APISOURCES:api_md+=f'- [{title}]({url})\n'
    api_md+='\n[F01~F05 공급사 미결 체크리스트](DX-1100_공급사_설치_콘솔_체크리스트.md)를 사용합니다. 공식 문서 명세 확인과 실제 API 요청 성공은 별개입니다.\n'
    (ROOT/'API_연동_준비_가이드.md').write_text(api_md)
