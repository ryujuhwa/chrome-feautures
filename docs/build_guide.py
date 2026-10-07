from pathlib import Path
from html import escape
import base64,re
from fontTools import subset

ROOT=Path(__file__).resolve().parents[1]
BLUE='#2563eb';GREEN='#12856b';RED='#dc4444';INK='#142338';MUTED='#607088';GOLD='#b9770e'

def txt(x,y,text,size=20,fill=INK,weight=500,anchor='start'):
 return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(text)}</text>'
def lines(x,y,words,size=20,fill=INK,step=30,anchor='start'):
 return ''.join(txt(x,y+i*step,t,size,fill,anchor=anchor) for i,t in enumerate(words))
def box(x,y,w,h,label='',color=BLUE,fill='#edf4ff',sub=None):
 a=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{color}" stroke-width="2"/>'
 if label:
  units=sum(0.33 if c==' ' else 1 if ord(c)>127 else .6 for c in label)
  size=min(23,(w-26)/max(units,1))
  a+=txt(x+w/2,y+42,label,size,color,700,'middle')
 if sub:
  units=max(sum(0.33 if c==' ' else 1 if ord(c)>127 else .6 for c in t) for t in sub)
  size=min(18,(w-22)/max(units,1))
  step=min(27,(h-14-78)/max(len(sub)-1,1)) if len(sub)>1 else 27
  if len(sub)>1:size=min(size,step*.93)
  a+=lines(x+w/2,y+78,sub,size,MUTED,step,'middle')
 return a
def arrow(x1,y1,x2,y2,color=BLUE,label=None):
 a=f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="3" fill="none" marker-end="url(#{color[1:]})"/>'
 if label:a+=txt((x1+x2)/2,(y1+y2)/2-12,label,17,color,anchor='middle')
 return a
def circle(x,y,r,label,color=BLUE,fill='#edf4ff',size=26):
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="2"/>'+txt(x,y+size*.35,label,size,color,700,'middle')
def badge(x,y,label,color=GREEN,w=130):
 return f'<rect x="{x}" y="{y}" width="{w}" height="36" rx="18" fill="{color}"/>'+txt(x+w/2,y+25,label,18,'white',700,'middle')
def browser(x,y,w,h,title='내가 보고 있는 웹페이지',overlay=False):
 a=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="white" stroke="#bdc9d9" stroke-width="2"/><path d="M{x},{y+43} H{x+w}" stroke="#bdc9d9"/>'
 a+= ''.join(f'<circle cx="{x+18+i*15}" cy="{y+21}" r="4" fill="#aab9ca"/>' for i in range(3))
 a+=f'<rect x="{x+73}" y="{y+10}" width="{w-90}" height="22" rx="6" fill="#edf1f7"/>'
 a+=txt(x+20,y+79,title,20,INK,700)
 for i in range(3):a+=f'<rect x="{x+20}" y="{y+99+i*26}" width="{max(60,w-70-i*15)}" height="11" rx="5" fill="#e6edf6"/>'
 if overlay:
  a+=f'<rect x="{x+2}" y="{y+45}" width="{w-4}" height="{h-47}" rx="8" fill="#142338" opacity=".36"/>'
  a+=box(x+w*.14,y+85,w*.72,110,'화면을 덮는 광고',RED,'#fff1f0',['본문 위에 올라온 덮개'])
 return a
def svg(body):
 markers=''.join(f'<marker id="{c[1:]}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{c}"/></marker>' for c in [BLUE,GREEN,RED,GOLD,MUTED])
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 430" role="img"><defs>{markers}</defs>{body}</svg>'
slides=[]
def slide(title,subtitle,drawing,takeaway,note=''):
 slides.append((title,subtitle,svg(drawing),takeaway,note))

# 1
b=browser(40,75,350,265,'내가 고른 링크와 본문')
b+=box(485,50,240,260,'확장 프로그램',BLUE,'#edf4ff',['새 창 검사','광고 요청 차단','광고 덮개 숨기기'])
b+=arrow(395,150,475,150)
b+=box(785,35,180,105,'원하는 새 창',GREEN,'#eaf8f2',['계속 사용'])+arrow(725,95,775,95,GREEN)
b+=box(785,190,180,105,'불청객 광고',RED,'#fff1f0',['차단 또는 숨김'])+arrow(725,245,775,245,RED)
b+=txt(500,370,'목표는 “새 창을 전부 없애기”가 아닙니다.',26,INK,700,'middle')
slide('원하는 창은 열고, 불청객 광고는 막습니다','자동 새 창·광고 레이어 차단 v1.3.0  |  개발 지식 없이 읽는 그림 설명서',b,'웹사이트를 이용하는 중 끼어드는 광고를 줄여 주는 크롬 보조 도구입니다.','그림은 설명을 위한 예시입니다. 모든 광고를 완벽하게 구분하는 기능은 아닙니다.')
# 2
b=browser(35,80,390,265)
b+=browser(270,200,200,180,'새 광고 창')+badge(50,24,'새 창 광고',RED,150)
b+=browser(575,80,390,265,overlay=True)+badge(590,24,'광고 레이어',RED,160)
b+=lines(205,403,['별도의 창·탭이 열림'],21,INK,anchor='middle')+lines(775,403,['기존 화면 위를 덮음'],21,INK,anchor='middle')
slide('광고가 끼어드는 방법은 크게 두 가지','둘은 모습도, 막는 방법도 다릅니다.',b,'새 창 광고에는 “창 열기 검사”, 화면 덮개에는 “광고 레이어 숨기기”가 필요합니다.')
# 3
b=box(20,65,220,225,'① 도착 전 검사',BLUE,'#edf4ff',['알려진 광고 서버의','프로그램·광고 화면을','가져오지 않음'])
b+=box(265,65,220,225,'② 새 창 검사',GREEN,'#eaf8f2',['사이트가 새 창을','열려 하면','최근 클릭과 비교'])
b+=box(510,65,220,225,'③ 화면 검사',GOLD,'#fff8e8',['광고로 확인되는','덮개를 찾아','화면에서 숨김'])
b+=box(755,65,220,225,'④ 직접 지정',RED,'#fff1f0',['자동 검사가 놓친','광고 덮개를','사용자가 선택'])
b+=circle(130,328,24,'망',BLUE,size=19)+circle(375,328,24,'창',GREEN,size=19)+circle(620,328,24,'면',GOLD,size=19)+circle(865,328,24,'선',RED,size=19)
b+=txt(500,405,'세 가지 자동 점검 + 사용자가 정하는 추가 규칙',25,INK,700,'middle')
slide('한 가지 방법 대신 네 가지 역할을 나눕니다','각 역할은 서로 보완합니다. 항상 이 순서로만 작동하는 것은 아닙니다.',b,'크롬 기본 팝업 차단도 함께 켜서 자동 팝업 차단을 보조합니다.')
# 4
b=box(30,145,185,125,'웹사이트',BLUE,'#edf4ff',['여러 자료를 요청'])
b+=arrow(220,180,355,90,BLUE)+arrow(220,225,355,310,RED)
b+=box(365,25,235,130,'본문용 자료',GREEN,'#eaf8f2',['정상 기능용 프로그램','일반 콘텐츠'])
b+=box(365,245,235,130,'알려진 광고 자료',RED,'#fff1f0',['광고를 실행하는 코드','웹페이지 안의 광고 창'])
b+=arrow(610,90,745,90,GREEN)+arrow(610,310,700,310,RED)
b+=browser(755,25,220,145,'정상 자료 도착')+circle(750,310,35,'×',RED,'#fff1f0',44)
b+=lines(820,290,['다운로드 차단','광고 실행을 줄임'],19,RED)
b+=txt(500,422,'일반 페이지 이동 전체를 금지하는 방식은 아닙니다.',20,INK,600,'middle')
slide('① 광고가 도착하기 전에 막습니다','크롬이 “광고 서버 목록”과 요청 종류를 비교합니다.',b,'목록에 등록된 서버의 광고 코드·광고 프레임이 대상입니다. 모든 광고 이미지를 지우는 기능은 아닙니다.')
# 5
b=box(25,40,210,110,'직접 누른 링크',GREEN,'#eaf8f2',['일반 링크·Ctrl+클릭'])+arrow(240,95,355,95,GREEN)+box(365,40,240,110,'크롬이 정상 처리',GREEN,'#eaf8f2',['새 탭을 일괄 닫지 않음'])
b+=box(25,230,210,110,'사이트의 새 창 요청',BLUE,'#edf4ff',['사이트 프로그램이 실행'])
b+=arrow(240,285,320,285)+f'<polygon points="455,190 590,285 455,380 320,285" fill="#edf4ff" stroke="{BLUE}" stroke-width="2"/>'
b+=lines(455,263,['방금 고른','링크·버튼과 맞나?'],20,BLUE,30,'middle')
b+=arrow(590,265,755,225,GREEN,'맞음')+box(765,175,205,95,'허용',GREEN,'#eaf8f2',['로그인 등 정상 사용'])
b+=arrow(590,305,755,350,RED,'맞지 않음')+box(765,305,205,95,'차단',RED,'#fff1f0',['불청객 팝업'])
slide('② 새 창 요청을 최근 행동과 비교합니다','“실제 사용자가 방금 누른 링크나 버튼인가?”를 단서로 삼습니다.',b,'링크는 요청 주소가 일치해야 합니다. 버튼은 정상 팝업을 우선 허용하되 알려진 광고 주소는 막습니다.','프로그램이 여는 창의 기본 판단 범위는 약 1초이며, 크롬도 실제 사용자 동작으로 인정해야 합니다.')
# 6
b=''
for x,y,n,title,sub,color in [(25,30,'1','링크를 새 탭으로 열기',['직접 선택한 주소','→ 보통 허용'],GREEN),(520,30,'2','로그인 버튼 누르기',['직후 정상 로그인 창','→ 보통 허용'],GREEN),(25,235,'3','빈 곳 클릭 후 광고 창',['고른 링크·버튼이 없음','→ 차단 대상'],RED),(520,235,'4','버튼에 광고가 섞임',['정상 동작과 구분이 어려움','→ 일부는 남을 수 있음'],GOLD)]:
 b+=box(x,y,450,165,title,color,{'#12856b':'#eaf8f2','#dc4444':'#fff1f0','#b9770e':'#fff8e8'}[color],sub)+circle(x+30,y+32,17,n,color,size=18)
slide('이런 경우는 어떻게 처리할까요?','사용자의 의도는 화면 밖에서 직접 알 수 없으므로, 행동을 단서로 판단합니다.',b,'정상 창을 무조건 보장하거나 모든 광고를 완벽하게 판별할 수는 없습니다.','특수하게 만든 사이트 버튼의 정상 팝업이 막히면 전체 차단을 잠시 꺼서 사용하세요.')
# 7
b=browser(25,75,300,250,overlay=True)+arrow(335,195,435,195)
b+=box(445,80,240,210,'광고 표시 확인',GOLD,'#fff8e8',['광고 덮개로 알려진 이름?','알려진 광고 화면?','화면 위에 덮인 요소?'])+arrow(695,195,765,195,GREEN)
b+=browser(775,75,200,250,'본문이 다시 보임')
b+=badge(420,345,'광고로 확인되면 숨김',GREEN,270)
slide('③ 광고 레이어는 화면에서 숨깁니다','레이어는 투명한 종이를 본문 위에 올려놓은 것과 비슷합니다.',b,'정상 메뉴나 로그인 창까지 지우지 않도록, 광고라는 단서가 있는 요소를 우선 찾습니다.','일반 자동 규칙은 큰 덮개를 대상으로 합니다. 확인된 사이트별 광고 규칙은 작은 광고도 처리합니다.')
# 8
b=box(25,90,215,150,'사용자가 준 자료',BLUE,'#edf4ff',['페이지의 구조 정보','광고 코드 주소'])+arrow(250,165,335,165)
b+=box(345,50,295,235,'광고 부분만 식별',GOLD,'#fff8e8',['광고를 만드는 외부 코드','전체 화면 덮개','화면 모서리 광고'])+arrow(650,165,745,165)
b+=box(755,90,220,150,'사이트 전용 규칙',GREEN,'#eaf8f2',['hitomi.la에 추가 적용','본문용 자료는 유지'])
b+=f'<rect x="50" y="325" width="900" height="76" rx="16" fill="#f0f3f8"/>'+lines(75,354,['광고 이름이 제각각이면 일반 규칙이 놓칠 수 있습니다.','실제 자료에서 확인한 광고 코드·덮개 이름을 사이트별 규칙에 더합니다.'],18,MUTED,27)
slide('문제가 있던 사이트에는 전용 규칙을 더했습니다','제공된 HTML을 바탕으로 광고 서버와 광고 덮개 식별자를 추가했습니다.',b,'추가한 광고 서버 차단은 해당 사이트에 한정합니다. 일반 광고 서버 목록은 여러 사이트에 적용됩니다.','실제 사이트 접속은 제한되어, 제공된 광고 구조를 재현한 테스트 페이지에서 검사했습니다.')
# 9
b=''
for x,num,title,overlay in [(20,'1','직접 선택 누르기',True),(270,'2','빨간 테두리 확인',True),(520,'3','클릭하면 숨김',False),(770,'4','다시 나타나도 숨김',False)]:
 b+=circle(x+105,35,23,num,BLUE,size=22)+browser(x,85,220,210,title,overlay)
 if num=='2':b+=f'<rect x="{x+28}" y="170" width="164" height="110" rx="10" fill="none" stroke="{RED}" stroke-width="5"/>'
 if num in ['3','4']:b+=badge(x+35,315,'본문 유지',GREEN,150)
 if num!='4':b+=arrow(x+225,200,x+244,200)
b+=txt(500,412,'처음 한 번 지정 → 같은 사이트의 같은 덮개를 기억',23,INK,700,'middle')
slide('④ 자동으로 놓친 덮개는 직접 선택합니다','확장 프로그램 메뉴 → “광고 레이어 직접 선택” → 광고 위에서 클릭',b,'이름·구조가 바뀌면 다시 선택해야 합니다. Esc로 취소하고, 잘못 선택하면 사이트 규칙을 초기화하세요.','직접 선택 대상도 화면 위에 배치된 덮개입니다. 웹페이지 전체나 일반 본문을 선택하는 기능은 아닙니다.')
# 10
b=box(300,20,400,375,'자동 새 창 차단',BLUE,'white')
b+=f'<rect x="330" y="84" width="340" height="45" rx="9" fill="{BLUE}"/>'+txt(500,114,'이 확장 프로그램의 차단 해제',18,'white',700,'middle')
b+=f'<rect x="336" y="155" width="21" height="21" rx="3" fill="{GREEN}"/>'+txt(346,172,'✓',17,'white',700,'middle')+txt(370,173,'광고 레이어 숨기기',19)
b+=f'<rect x="330" y="202" width="340" height="46" rx="8" fill="#edf4ff"/>'+txt(500,232,'광고 레이어 직접 선택',19,BLUE,700,'middle')
b+=f'<rect x="330" y="267" width="340" height="46" rx="8" fill="#edf4ff"/>'+txt(500,297,'이 사이트의 선택 차단 초기화',18,BLUE,700,'middle')
b+=lines(25,102,['전체 차단 켜기·끄기','광고 요청·새 창·덮개'],18,INK,27)+arrow(230,110,290,110)
b+=lines(730,146,['덮개 숨기기만 제어','새 창 검사는 그대로'],18,INK,27)+arrow(710,165,680,165)
b+=lines(25,220,['자동 검사가 놓친','광고를 직접 지정'],18,INK,27)+arrow(235,225,290,225)
b+=lines(730,280,['내가 선택한 규칙 삭제','기본 광고 규칙은 유지'],18,INK,27)+arrow(710,290,680,290)
slide('메뉴의 네 가지 조작은 역할이 다릅니다','전체 차단과 광고 레이어 숨기기는 서로 다른 설정입니다.',b,'전체 차단을 꺼도 원래 크롬 설정이 팝업 차단이면 크롬의 기본 차단은 계속될 수 있습니다.','버튼을 배치한 설명용 그림입니다. 실제 크롬 화면과 글자 배치가 조금 다를 수 있습니다.')
# 11
b=f'<rect x="25" y="50" width="620" height="330" rx="24" fill="#edf4ff" stroke="{BLUE}" stroke-width="2"/>'+txt(55,91,'내 PC의 크롬 프로필',26,BLUE,700)
b+=box(60,130,250,180,'설정 저장',BLUE,'white',['차단 켜짐·꺼짐','광고 덮개 숨김 여부'])+box(345,130,265,180,'직접 선택 규칙',BLUE,'white',['현재 사이트 주소','숨길 덮개의 위치·이름'])
b+=box(745,140,220,155,'외부 수집 서버',MUTED,'#f0f3f8',['이 확장에는 없음'])+arrow(655,216,725,216,RED)+circle(693,216,23,'×',RED,'#fff1f0',31)
b+=txt(810,353,'방문 기록을 수집해',19,MUTED,anchor='middle')+txt(810,380,'전송하는 기능 없음',19,MUTED,anchor='middle')
slide('내가 정한 규칙은 내 크롬에 저장됩니다','설정과 사이트별 선택 규칙은 다른 사람의 PC로 자동 공유되지 않습니다.',b,'삭제 후 재설치하면 직접 선택한 규칙도 없어집니다. 사이트의 이름·구조가 바뀌면 규칙이 맞지 않을 수 있습니다.','확장 프로그램의 저장·전송 동작에 대한 설명입니다. 웹사이트 자체의 통신이나 수집까지 없애는 것은 아닙니다.')
# 12
b=box(20,40,450,190,'검사에서 확인한 동작',GREEN,'#eaf8f2',['자동·빈 영역 클릭 팝업 차단','정상 링크·Ctrl+클릭·로그인 유지','광고 덮개 숨김·재등장 처리'])
b+=box(520,40,450,190,'남아 있는 한계',GOLD,'#fff8e8',['새 광고 서버·바뀐 덮개는 놓칠 수 있음','버튼에 섞인 광고는 구분이 어려움','사이트가 차단을 우회할 수 있음'])
b+=f'<rect x="20" y="260" width="950" height="135" rx="18" fill="#edf4ff"/>'+txt(45,298,'문제가 남으면 이렇게 사용하세요',23,BLUE,700)
b+=lines(45,334,['① 업데이트 후 해당 페이지 새로고침   ② 남은 덮개는 직접 선택','③ 정상 기능이 막히면 잠시 끄기   ④ 잘못 선택했으면 사이트 규칙 초기화'],20,INK,30)
slide('편리한 보조 도구이며, 완벽한 광고 판별기는 아닙니다','의도한 새 창을 보존하는 것과 광고를 최대한 줄이는 것 사이에서 신중하게 판단합니다.',b,'광고 없는 안전한 사이트임을 보증하거나, 외부 프로그램이 여는 창까지 막는 기능은 아닙니다.','현재 검증: 실제 Chromium의 테스트 페이지와 단위 테스트 통과. 관리자 정책으로 확장 설치·네트워크 규칙 통합 검증 및 실제 대상 사이트 검증은 미완료입니다.')

# Technical appendix: exact v1.3.0 implementation.
b=box(20,20,245,115,'manifest.json',BLUE,'#edf4ff',['크롬이 읽는 설계도','권한·실행 위치·파일 지정'])
b+=box(20,205,245,145,'background.js',GOLD,'#fff8e8',['설치·업데이트 때 실행','기본 팝업 설정 적용','네트워크 규칙 활성화'])
b+=box(370,20,255,115,'page-guard.js',GREEN,'#eaf8f2',['웹페이지와 같은 실행 공간','새 창 열기 함수 검사'])
b+=box(370,205,255,145,'content.js',BLUE,'#edf4ff',['확장 전용 실행 공간','화면 요소 탐지·숨김','직접 선택·규칙 저장'])
b+=box(730,20,245,115,'ad-rules.json',RED,'#fff1f0',['크롬 네트워크 엔진이','검사하는 광고 목록'])
b+=box(730,205,245,145,'popup.html / .js',BLUE,'#edf4ff',['도구 모음 메뉴','설정 변경·선택 명령'])
b+=arrow(270,75,355,75)+arrow(270,285,355,285)+arrow(720,285,640,285)
b+=txt(500,402,'실행 공간을 분리하고, 필요한 정보만 전달합니다.',24,INK,700,'middle')
slide('기술 부록 ① 파일별 역할과 실행 위치','JavaScript(.js)는 동작을 실행하는 코드, JSON(.json)은 설정·규칙을 담는 자료입니다.',b,'백그라운드는 항상 켜진 서버가 아닙니다. 크롬이 필요한 이벤트에 맞춰 실행하는 서비스 워커입니다.','manifest.json은 Manifest V3 형식입니다. 페이지 스크립트는 document_start에 시작하며 해당 프레임에도 주입됩니다.')

b=box(20,45,220,190,'저장된 설정',BLUE,'#edf4ff',['chrome.storage.local','enabled / overlays','사이트별 선택 규칙'])
b+=arrow(250,145,355,145,BLUE,'읽기')+box(365,45,245,190,'content.js',BLUE,'#edf4ff',['확장 전용 공간','설정 읽기·화면 처리','변경 이벤트 수신'])
b+=arrow(620,145,725,145,GREEN,'설정 전달')+box(735,45,245,190,'page-guard.js',GREEN,'#eaf8f2',['웹페이지 실행 공간','새 창 검사 활성 여부','window.open 래핑'])
b+=box(235,295,530,100,'popup-blocker-setting',GOLD,'#fff8e8',['CustomEvent로 enabled 값을 JSON 문자열로 전달'])
b+=txt(500,422,'저장값 변경 → 다시 읽기 → 화면 처리·새 창 검사에 반영',22,INK,700,'middle')
slide('기술 부록 ② 설정이 페이지로 전달되는 과정','두 실행 공간은 같은 웹 문서를 보지만, JavaScript 변수 공간은 분리되어 있습니다.',b,'storage.onChanged는 저장값 변경을 알려 줍니다. content.js가 읽은 enabled만 페이지 쪽으로 전달합니다.','이 문서 이벤트는 페이지 코드도 조작할 수 있습니다. 편의 기능을 위한 연결이며 보안 경계가 아닙니다.')

b=box(20,25,290,140,'window.open 요청',BLUE,'#edf4ff',['원래 함수를 먼저 보관','검사 함수를 대신 배치'])+arrow(320,95,380,95)
b+=box(390,25,590,140,'새 창 검사가 필요한 요청인가?',BLUE,'#edf4ff',['차단 꺼짐 → 원래 함수 호출','_self / _parent / _top → 새 창 검사 우회'])
b+=box(20,225,290,165,'최근 실제 사용자 동작',GOLD,'#fff8e8',['isTrusted인 클릭·키 입력','링크 또는 버튼을 선택','1초 미만 + userActivation'])+arrow(320,300,380,300)
b+=box(390,225,275,165,'링크에서 시작',GREEN,'#eaf8f2',['요청 URL을 정규화','선택 링크 URL과 비교','동일해야 허용'])
b+=box(700,225,280,165,'버튼에서 시작',GREEN,'#eaf8f2',['알려진 광고 주소 제외','나머지는 정상 동작 우선','원래 함수로 전달'])
slide('기술 부록 ③ 새 창 검사 조건을 코드로 풀면','window.open은 사이트 프로그램이 창이나 탭을 열 때 사용하는 브라우저 함수입니다.',b,'허용하면 Reflect.apply로 원래 함수를 호출합니다. 차단하면 null을 돌려주어 새 창 열기를 중단합니다.','합성 클릭도 검사해 preventDefault()로 막습니다. 이 함수의 광고 주소 목록은 기본 7개이며 사이트별 네트워크 목록과 별개입니다.')

b=box(20,70,220,210,'웹페이지의 요청',BLUE,'#edf4ff',['요청한 서버 주소','요청 종류','요청을 시작한 사이트'])+arrow(250,175,345,175)
b+=box(355,25,360,305,'크롬 네트워크 규칙 엔진',RED,'#fff1f0',['declarativeNetRequest','requestDomains: 광고 서버','resourceTypes: script, sub_frame','사이트 전용: initiatorDomains','조건이 맞으면 action: block'])
b+=arrow(725,135,800,100,RED)+circle(850,100,30,'×',RED,'#fff1f0',39)+txt(850,155,'광고 코드 차단',20,RED,anchor='middle')
b+=arrow(725,245,800,280,GREEN)+circle(850,280,30,'✓',GREEN,'#eaf8f2',32)+txt(850,335,'나머지 요청 진행',20,GREEN,anchor='middle')
b+=txt(500,403,'현재 목록: 일반 광고 서버 규칙 + hitomi.la 전용 규칙',23,INK,700,'middle')
slide('기술 부록 ④ 광고 코드를 실행 전에 차단합니다','script는 외부 실행 코드, sub_frame은 페이지 안에 삽입되는 별도 웹 화면입니다.',b,'이 검사는 페이지의 JavaScript 함수 교체와 별개로 크롬이 처리합니다. 일반 페이지 이동(main_frame)은 이 목록의 대상이 아닙니다.','popup.js는 updateEnabledRulesets로 규칙 묶음을 켜거나 끕니다. 광고로 알려진 서버라도 다른 종류의 요청은 이 규칙만으로 차단하지 않습니다.')

b=box(20,30,250,165,'MutationObserver',BLUE,'#edf4ff',['화면 요소 추가·삭제 감시','id, class, src, style 등','속성 변경도 감시'])+arrow(280,110,360,110)
b+=box(370,30,250,165,'schedule → scan',GOLD,'#fff8e8',['대기 중 검사 하나로 합침','setTimeout(..., 50)','변경 후 화면 다시 검사'])+arrow(630,110,710,110)
b+=box(720,30,250,165,'광고 후보 선택',RED,'#fff1f0',['광고 이름·data-ad-overlay','알려진 광고 iframe 주소','후보만 위치·크기 검사'])
b+=box(115,255,770,120,'일반 자동 규칙의 위치·크기 조건',BLUE,'#edf4ff',['fixed 또는 absolute + 가로·세로 크기 > 0','면적 ≥ 화면의 15%  그리고  z-index ≥ 10 또는 fixed'])
slide('기술 부록 ⑤ 광고 레이어를 찾는 조건','DOM은 화면 요소의 구조, CSS는 각 요소의 위치·크기·모양을 정하는 규칙입니다.',b,'50ms는 검사 예약 시간입니다. 정확한 실행 시간을 보장하거나 화면을 50ms마다 무조건 검사한다는 뜻은 아닙니다.','별도 예외: 확인된 사이트의 광고 클래스는 크기와 무관하게 숨깁니다. 직접 선택한 요소는 면적 15% 조건을 제외하고 위치 조건을 확인합니다.')

b=box(20,65,230,240,'숨기기 전 보관',BLUE,'#edf4ff',['hidden이라는 Map','요소 객체를 열쇠로 사용','원래 inline display 저장','원래 !important 여부 저장'])+arrow(260,180,335,180)
b+=box(345,65,300,240,'화면에서 숨기기',RED,'#fff1f0',['display: none !important','DOM에서 삭제하지 않음','사이트가 다시 표시하면','검사에서 다시 숨김'])+arrow(655,180,730,180,GREEN)
b+=box(740,65,235,240,'설정 해제·복원',GREEN,'#eaf8f2',['직접 넣은 숨김이','유지되는 요소만 복원','보관한 원래 스타일 적용','화면에서 떠난 요소 정리'])
b+=txt(500,402,'숨김 기록은 페이지 메모리에, 선택 규칙은 크롬 저장소에 남습니다.',21,INK,700,'middle')
slide('기술 부록 ⑥ 삭제 대신 숨김과 복원을 사용합니다','Map은 요소와 원래 인라인 display 스타일을 짝지어 보관하는 임시 기록입니다.',b,'전체 차단·레이어 숨기기를 끄면 저장해 둔 스타일로 복원합니다. 직접 선택 규칙을 바꾸거나 초기화할 때도 복원 후 다시 검사합니다.','페이지를 새로고침하면 요소 객체와 Map은 새로 만들어집니다. 저장된 선택 규칙은 다시 읽어 재적용합니다.')

b=box(20,25,220,145,'선택 명령 보내기',BLUE,'#edf4ff',['popup.js → 현재 탭','tabs.sendMessage','pick-layer, frameId: 0'])+arrow(250,98,345,98)
b+=box(355,25,270,145,'클릭 지점의 요소 찾기',GOLD,'#fff8e8',['투명 선택 화면 + Shadow DOM','elementFromPoint(x, y)','조건에 맞는 부모까지 탐색'])+arrow(635,98,720,98)
b+=box(730,25,245,145,'클릭을 광고에 전달 안 함',RED,'#fff1f0',['preventDefault','stopImmediatePropagation','선택용 클릭만 처리'])
b+=box(65,265,360,130,'요소의 주소 만들기',BLUE,'#edf4ff',['고유 id → #id를 우선 사용','없으면 부모 경로 + nth-of-type','CSS.escape로 id 문자 처리'])+arrow(435,330,535,330)
b+=box(545,265,400,130,'사이트별 선택 규칙 저장',GREEN,'#eaf8f2',['layerRules:https://사이트주소','CSS 선택자 목록을 로컬에 저장','다시 나타난 덮개에 동일 규칙 적용'])
slide('기술 부록 ⑦ 직접 선택은 요소의 “주소”를 기억합니다','CSS 선택자는 화면에서 특정 요소를 다시 찾아낼 때 사용하는 주소 표현입니다.',b,'선택 화면의 클릭 감지를 잠깐 비켜서 아래 요소를 찾습니다. 선택이 끝나거나 Esc를 누르면 선택 화면과 이벤트를 제거합니다.','규칙의 범위는 origin(프로토콜 + 호스트 + 포트)입니다. 다른 페이지에서도 구조가 같으면 적용되며, 구조가 달라지면 다시 선택해야 합니다.')

b=box(20,25,460,195,'필요한 권한',BLUE,'#edf4ff',['contentSettings: 크롬 팝업 설정','storage: 설정·사이트별 규칙 저장','declarativeNetRequest: 광고 요청 차단','activeTab: 사용자가 연 현재 탭 선택'])
b+=box(520,25,455,195,'코드 구조에서 생기는 한계',GOLD,'#fff8e8',['페이지 코드가 함수·이벤트를 우회할 수 있음','저장값 읽기는 비동기: 시작 시 기본값은 켜짐','특수한 정상 컨트롤은 차단될 수 있음','저장한 주소가 바뀌면 선택 규칙은 놓칠 수 있음'])
b+=box(20,270,955,130,'검증 범위를 구분해야 합니다',GREEN,'#eaf8f2',['확인: 단위 테스트 + 실제 Chromium 테스트 페이지에서 배포 스크립트 실행','미확인: 실제 확장 설치·네트워크 규칙의 통합 동작, 실제 대상 사이트 전체 동작'])
slide('기술 부록 ⑧ 권한·한계·검증 범위','설명을 코드 구조와 대조한 기술 부록입니다. 새로운 기능을 추가한 업데이트는 아닙니다.',b,'네트워크 차단은 크롬 엔진의 규칙 처리이고, 새 창·레이어 처리는 페이지 코드의 동작입니다. 두 검증을 혼동하지 않아야 합니다.','현재 클라우드는 관리자 정책으로 확장 로딩을 제한하고, 대상 사이트는 프록시가 접근을 거부합니다. 기능이 보안 경계나 완전한 광고 방어 수단이라는 의미는 아닙니다.')


css='''@font-face{font-family:Guide;src:url(FONTDATA) format('woff');font-weight:100 900;font-display:block}*{box-sizing:border-box}body{margin:0;background:#e6edf5;color:#142338;font-family:Guide,"Noto Sans CJK KR",sans-serif}.toolbar{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:center;gap:14px;padding:12px;background:#142338;color:white}.toolbar button{border:0;border-radius:7px;background:#fff;color:#142338;padding:9px 15px;font:inherit;font-size:14px;cursor:pointer}.toolbar button:focus-visible{outline:3px solid #60a5fa}.slide{position:relative;width:1123px;height:794px;margin:26px auto;padding:42px 44px 55px;background:white;box-shadow:0 10px 40px #14233815;display:none;overflow:hidden}.slide.active,body.all .slide{display:block}.eyebrow{font-size:12px;letter-spacing:.06em;color:#607088;margin-bottom:12px}.slide h1{font-size:34px;line-height:1.3;margin:0 0 12px;font-weight:700;letter-spacing:-.8px}.subtitle{font-size:17px;line-height:1.7;margin:0;color:#607088}.drawing{height:450px;display:flex;align-items:center;margin-top:12px}.drawing svg{width:100%;max-height:450px;font-family:Guide,sans-serif}.takeaway{padding:14px 18px;border-left:5px solid #2563eb;background:#f1f6ff;font-size:18px;line-height:1.6;margin-top:8px;border-radius:0 10px 10px 0}.note{font-size:12px;line-height:1.65;color:#607088;margin:10px 0 0}.footer{position:absolute;bottom:19px;left:44px;right:44px;display:flex;justify-content:space-between;font-size:11px;color:#607088}.screen-note{text-align:center;color:#607088;font-size:13px;margin:15px}@page{size:A4 landscape;margin:0}@media print{body{background:white}.toolbar,.screen-note{display:none!important}.slide{display:block!important;width:297mm;height:210mm;margin:0;padding:11mm 12mm 14mm;box-shadow:none;break-after:page;page-break-after:always}.slide:last-of-type{break-after:auto;page-break-after:auto}.drawing{height:116mm}.slide h1{font-size:25pt}.subtitle{font-size:12pt}.takeaway{font-size:13pt}.note{font-size:9pt}.footer{left:12mm;right:12mm;bottom:5mm}.drawing svg{max-height:116mm}}'''
sections=[]
for i,(title,sub,drawing,takeaway,note) in enumerate(slides,1):
 sections.append(f'<section class="slide {"active" if i==1 else ""}" id="slide-{i}" aria-label="{i}. {escape(title)}"><div class="eyebrow">CHROME POPUP BLOCKER · 그림으로 이해하기</div><h1>{escape(title)}</h1><p class="subtitle">{escape(sub)}</p><div class="drawing">{drawing}</div><div class="takeaway">{escape(takeaway)}</div><p class="note">{escape(note)}</p><div class="footer"><span>v1.3.0 기준 · 2026.10.07 · 비개발자용 설명 자료</span><span>{i:02d} / {len(slides):02d}</span></div></section>')
script='''const slides=[...document.querySelectorAll('.slide')];let index=0;function show(n){index=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===index));document.querySelector('#count').textContent=`${index+1} / ${slides.length}`;history.replaceState(null,'',`#slide-${index+1}`);document.querySelector('#prev').disabled=index===0;document.querySelector('#next').disabled=index===slides.length-1;}document.querySelector('#prev').onclick=()=>show(index-1);document.querySelector('#next').onclick=()=>show(index+1);document.querySelector('#all').onclick=()=>{document.body.classList.toggle('all');document.querySelector('#all').textContent=document.body.classList.contains('all')?'한 장씩 보기':'모두 보기';};document.querySelector('#print').onclick=()=>window.print();document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();show(index+1);}if(e.key==='ArrowLeft'){e.preventDefault();show(index-1);}});show((parseInt(location.hash.replace('#slide-',''))||1)-1);'''
html='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>그림으로 이해하는 자동 새 창·광고 레이어 차단</title><style>'+css+'</style></head><body><nav class="toolbar" aria-label="자료 탐색"><button id="prev">이전</button><span id="count">1 / 12</span><button id="next">다음</button><button id="all">모두 보기</button><button id="print">인쇄 / PDF 저장</button></nav><p class="screen-note">← → 키로 이동할 수 있습니다. 인터넷 연결 없이 열리는 설명 자료입니다.</p>'+''.join(sections)+'<script>'+script+'</script></body></html>'
html=html.replace('1 / 12',f'1 / {len(slides)}')
# Embed a subset Korean font, so Windows readers see the same diagrams offline.
font=subset.load_font('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',subset.Options(font_number=1))
opts=subset.Options();sub=subset.Subsetter(options=opts);sub.populate(text=''.join(set(re.sub('<[^>]+>','',html))));sub.subset(font);font.flavor='woff';path=Path('/tmp/popup-guide-font.woff');font.save(path)
html=html.replace('FONTDATA','data:font/woff;base64,'+base64.b64encode(path.read_bytes()).decode())
license_path=ROOT/'docs/FONT-LICENSE.txt'
if license_path.exists():html=html.replace('</head>','<!--\n'+license_path.read_text()+'\n--></head>')
(ROOT/'docs/popup-blocker-guide.html').write_text(html)
print('Created',len(slides),'slides; HTML bytes',len(html.encode()))
