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
def browser(x,y,w,h,title='The page you are viewing',overlay=False):
 a=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="white" stroke="#bdc9d9" stroke-width="2"/><path d="M{x},{y+43} H{x+w}" stroke="#bdc9d9"/>'
 a+= ''.join(f'<circle cx="{x+18+i*15}" cy="{y+21}" r="4" fill="#aab9ca"/>' for i in range(3))
 a+=f'<rect x="{x+73}" y="{y+10}" width="{w-90}" height="22" rx="6" fill="#edf1f7"/>'
 a+=txt(x+20,y+79,title,20,INK,700)
 for i in range(3):a+=f'<rect x="{x+20}" y="{y+99+i*26}" width="{max(60,w-70-i*15)}" height="11" rx="5" fill="#e6edf6"/>'
 if overlay:
  a+=f'<rect x="{x+2}" y="{y+45}" width="{w-4}" height="{h-47}" rx="8" fill="#142338" opacity=".36"/>'
  a+=box(x+w*.14,y+85,w*.72,110,'Ad overlay',RED,'#fff1f0',['Covers the page'])
 return a
def svg(body):
 markers=''.join(f'<marker id="{c[1:]}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="{c}"/></marker>' for c in [BLUE,GREEN,RED,GOLD,MUTED])
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 430" role="img"><defs>{markers}</defs>{body}</svg>'
slides=[]
def slide(title,subtitle,drawing,takeaway,note=''):
 slides.append((title,subtitle,svg(drawing),takeaway,note))

# 1
b=browser(40,75,350,265,'Your links and content')
b+=box(485,50,240,260,'Extension',BLUE,'#edf4ff',['Popup check','Ad request blocking','Hide ad overlays'])
b+=arrow(395,150,475,150)
b+=box(785,35,180,105,'Wanted window',GREEN,'#eaf8f2',['Keep using it'])+arrow(725,95,775,95,GREEN)
b+=box(785,190,180,105,'Unwanted ad',RED,'#fff1f0',['Block or hide'])+arrow(725,245,775,245,RED)
b+=txt(500,370,'The goal is to preserve the windows you choose to open.',26,INK,700,'middle')
slide('Keep wanted windows. Block unwanted ads.','Popup & Ad Overlay Blocker v1.3.0 | An illustrated guide for everyone',b,'A Chrome extension that reduces ads interrupting your browsing.','Diagrams are illustrative. The extension cannot identify every ad perfectly.')
# 2
b=browser(35,80,390,265)
b+=browser(270,200,200,180,'Ad popup')+badge(50,24,'Popup ad',RED,150)
b+=browser(575,80,390,265,overlay=True)+badge(590,24,'Ad overlay',RED,160)
b+=lines(205,403,['A separate window or tab opens'],21,INK,anchor='middle')+lines(775,403,['An extra layer covers the page'],21,INK,anchor='middle')
slide('Ads can interrupt browsing in two different ways','They look different and need different blocking methods.',b,'Popup checks handle new windows. Overlay hiding handles layers covering the page.')
# 3
b=box(20,65,220,225,'1. Request filtering',BLUE,'#edf4ff',['Known ad servers:','scripts and embedded ads','are not downloaded'])
b+=box(265,65,220,225,'2. Popup checks',GREEN,'#eaf8f2',['A site wants to open','a new window:','check your recent action'])
b+=box(510,65,220,225,'3. Page scanning',GOLD,'#fff8e8',['Find elements identified','as advertising overlays','and hide them'])
b+=box(755,65,220,225,'4. Manual selection',RED,'#fff1f0',['For overlays missed','by automatic detection,','you choose what to hide'])
b+=circle(130,328,24,'N',BLUE,size=19)+circle(375,328,24,'W',GREEN,size=19)+circle(620,328,24,'P',GOLD,size=19)+circle(865,328,24,'S',RED,size=19)
b+=txt(500,405,'Three automatic checks + your own selections',25,INK,700,'middle')
slide('Four complementary roles','The roles complement one another; they do not always run in this order.',b,'Chrome’s built-in popup blocking is also enabled as an additional safeguard.')
# 4
b=box(30,145,185,125,'Website',BLUE,'#edf4ff',['Requests several resources'])
b+=arrow(220,180,355,90,BLUE)+arrow(220,225,355,310,RED)
b+=box(365,25,235,130,'Content resources',GREEN,'#eaf8f2',['Code for normal features','Regular content'])
b+=box(365,245,235,130,'Known ad resources',RED,'#fff1f0',['Code that runs ads','An embedded ad frame'])
b+=arrow(610,90,745,90,GREEN)+arrow(610,310,700,310,RED)
b+=browser(755,25,220,145,'Content arrives')+circle(750,310,35,'×',RED,'#fff1f0',44)
b+=lines(820,290,['Download blocked','Fewer ads can run'],19,RED)
b+=txt(500,422,'Regular page navigation is not blocked by these rules.',20,INK,600,'middle')
slide('1. Block known ads before they arrive','Chrome checks the server address and the type of resource requested.',b,'Rules target scripts and ad frames from listed servers. They do not remove every ad image.')
# 5
b=box(25,40,210,110,'Your chosen link',GREEN,'#eaf8f2',['Regular links / Ctrl-click'])+arrow(240,95,355,95,GREEN)+box(365,40,240,110,'Chrome handles it',GREEN,'#eaf8f2',['No blanket tab closing'])
b+=box(25,230,210,110,'Script popup request',BLUE,'#edf4ff',['Requested by website code'])
b+=arrow(240,285,320,285)+f'<polygon points="455,190 590,285 455,380 320,285" fill="#edf4ff" stroke="{BLUE}" stroke-width="2"/>'
b+=lines(455,263,['Does it match your','recent link or button?'],20,BLUE,30,'middle')
b+=arrow(590,265,755,225,GREEN,'Match')+box(765,175,205,95,'Allow',GREEN,'#eaf8f2',['Normal sign-in, etc.'])
b+=arrow(590,305,755,350,RED,'No match')+box(765,305,205,95,'Block',RED,'#fff1f0',['Unwanted popup'])
slide('2. Compare popup requests with your recent action','The key clue is whether you just selected a real link or button.',b,'For links, the destination must match. Buttons normally allow popups, except to known ad hosts.','The time window is under one second, and Chrome must also recognize an active user gesture.')
# 6
b=''
for x,y,n,title,sub,color in [(25,30,'1','Open a link in a new tab',['The address you selected','Usually allowed'],GREEN),(520,30,'2','Click a sign-in button',['A normal sign-in popup','Usually allowed'],GREEN),(25,235,'3','An ad opens after an empty-area click',['No link or button selected','A blocking candidate'],RED),(520,235,'4','An ad is attached to a button',['Hard to separate from normal use','Some ads may still get through'],GOLD)]:
 b+=box(x,y,450,165,title,color,{'#12856b':'#eaf8f2','#dc4444':'#fff1f0','#b9770e':'#fff8e8'}[color],sub)+circle(x+30,y+32,17,n,color,size=18)
slide('How are common situations handled?','The extension infers intent from your actions; it cannot read your mind.',b,'It cannot guarantee every wanted popup or perfectly identify every ad.','If a site’s custom button is blocked, temporarily turn off blocking to use it.')
# 7
b=browser(25,75,300,250,overlay=True)+arrow(335,195,435,195)
b+=box(445,80,240,210,'Look for ad clues',GOLD,'#fff8e8',['A known ad overlay name?','An ad frame from a known host?','An element covering the page?'])+arrow(695,195,765,195,GREEN)
b+=browser(775,75,200,250,'Content is visible')
b+=badge(420,345,'Hide identified ad overlays',GREEN,270)
slide('3. Hide identified advertising overlays','An overlay is like placing another sheet on top of the page.',b,'Look for advertising clues first, to avoid hiding ordinary menus or sign-in dialogs.','General automatic rules target large overlays. Confirmed site-specific rules also handle smaller ads.')
# 8
b=box(25,90,215,150,'User-provided HTML',BLUE,'#edf4ff',['Page structure','Advertising script URLs'])+arrow(250,165,335,165)
b+=box(345,50,295,235,'Identify ad components',GOLD,'#fff8e8',['External ad-generating code','Full-screen overlays','Corner ad panels'])+arrow(650,165,745,165)
b+=box(755,90,220,150,'Site-specific rules',GREEN,'#eaf8f2',['Added for hitomi.la','Keep content resources'])
b+=f'<rect x="50" y="325" width="900" height="76" rx="16" fill="#f0f3f8"/>'+lines(75,354,['Varying overlay names can evade general rules.','Confirmed script hosts and overlay identifiers become site-specific rules.'],18,MUTED,27)
slide('Add targeted rules for the reported site','The supplied HTML identified additional ad hosts and overlay selectors.',b,'Additional host rules are scoped to that site. General ad host rules apply across sites.','Live access was restricted, so testing used a page reproducing the supplied ad structures.')
# 9
b=''
for x,num,title,overlay in [(20,'1','Start selecting',True),(270,'2','Check the red outline',True),(520,'3','Click to hide',False),(770,'4','Hide it next time',False)]:
 b+=circle(x+105,35,23,num,BLUE,size=22)+browser(x,85,220,210,title,overlay)
 if num=='2':b+=f'<rect x="{x+28}" y="170" width="164" height="110" rx="10" fill="none" stroke="{RED}" stroke-width="5"/>'
 if num in ['3','4']:b+=badge(x+35,315,'Keep content',GREEN,150)
 if num!='4':b+=arrow(x+225,200,x+244,200)
b+=txt(500,412,'Select once: remember matching overlays on the same site',23,INK,700,'middle')
slide('4. Select overlays that automatic checks miss','Extension menu → Select an ad overlay → Click the unwanted overlay',b,'If the structure changes, select again. Esc cancels selection; reset site rules to undo a mistake.','Manual selection targets positioned overlays, not the whole page or ordinary page content.')
# 10
b=box(300,20,400,375,'Popup Blocker',BLUE,'white')
b+=f'<rect x="330" y="84" width="340" height="45" rx="9" fill="{BLUE}"/>'+txt(500,114,'Turn off extension blocking',18,'white',700,'middle')
b+=f'<rect x="336" y="155" width="21" height="21" rx="3" fill="{GREEN}"/>'+txt(346,172,'✓',17,'white',700,'middle')+txt(370,173,'Hide ad overlays',19)
b+=f'<rect x="330" y="202" width="340" height="46" rx="8" fill="#edf4ff"/>'+txt(500,232,'Select an ad overlay',19,BLUE,700,'middle')
b+=f'<rect x="330" y="267" width="340" height="46" rx="8" fill="#edf4ff"/>'+txt(500,297,'Reset selected rules for this site',18,BLUE,700,'middle')
b+=lines(25,102,['Toggle all blocking','Requests, popups, overlays'],18,INK,27)+arrow(230,110,290,110)
b+=lines(730,146,['Toggle only overlay hiding','Popup checks stay active'],18,INK,27)+arrow(710,165,680,165)
b+=lines(25,220,['For overlays missed','Select the missed overlay'],18,INK,27)+arrow(235,225,290,225)
b+=lines(730,280,['Remove your selections','Keep built-in ad rules'],18,INK,27)+arrow(710,290,680,290)
slide('Four menu controls, four different roles','Overall blocking and overlay hiding are separate settings.',b,'Turning off the extension restores Chrome’s prior popup setting, which may still block popups.','This is an illustrative menu. Its labels are translated; the extension interface remains Korean.')
# 11
b=f'<rect x="25" y="50" width="620" height="330" rx="24" fill="#edf4ff" stroke="{BLUE}" stroke-width="2"/>'+txt(55,91,'Chrome profile on your PC',26,BLUE,700)
b+=box(60,130,250,180,'Saved settings',BLUE,'white',['Blocking on / off','Overlay hiding on / off'])+box(345,130,265,180,'Selected overlay rules',BLUE,'white',['Current site origin','Selector for an overlay'])
b+=box(745,140,220,155,'Collection server',MUTED,'#f0f3f8',['None in this extension'])+arrow(655,216,725,216,RED)+circle(693,216,23,'×',RED,'#fff1f0',31)
b+=txt(810,353,'No feature that collects',19,MUTED,anchor='middle')+txt(810,380,'and sends browsing history',19,MUTED,anchor='middle')
slide('Your rules are stored in your Chrome profile','Settings and selected rules are not automatically shared with other people’s computers.',b,'Removing and reinstalling clears your selections. Changed site structure can invalidate them.','This describes the extension itself. It does not stop all traffic or data collection by websites.')
# 12
b=box(20,40,450,190,'Verified in tests',GREEN,'#eaf8f2',['Block automatic and unrelated-click popups','Keep chosen links, Ctrl-click and sign-in','Hide overlays and handle recurrence'])
b+=box(520,40,450,190,'Remaining limitations',GOLD,'#fff8e8',['New ad hosts or changed overlays may be missed','Ads attached to buttons are hard to distinguish','Sites can bypass the page guard'])
b+=f'<rect x="20" y="260" width="950" height="135" rx="18" fill="#edf4ff"/>'+txt(45,298,'If something still goes wrong',23,BLUE,700)
b+=lines(45,334,['1. Refresh after updates.  2. Select remaining ad overlays.','3. Turn blocking off if needed.  4. Reset mistaken selections.'],20,INK,30)
slide('A useful helper, not a perfect ad detector','The aim is to reduce unwanted ads while preserving intentional windows.',b,'It does not certify site safety or block windows opened by external programs.','Unit and Chromium fixture tests passed. Extension installation, network-rule integration and live-site behavior remain unverified due to policy restrictions.')

# Technical appendix: exact v1.3.0 implementation.
b=box(20,20,245,115,'manifest.json',BLUE,'#edf4ff',['Configuration read by Chrome','Permissions, worlds and files'])
b+=box(20,205,245,145,'background.js',GOLD,'#fff8e8',['Runs on install or update','Sets native popup blocking','Enables request rules'])
b+=box(370,20,255,115,'page-guard.js',GREEN,'#eaf8f2',['Shares the page’s JS world','Checks the popup function'])
b+=box(370,205,255,145,'content.js',BLUE,'#edf4ff',['Extension’s isolated world','Detects and hides elements','Picker and rule storage'])
b+=box(730,20,245,115,'ad-rules.json',RED,'#fff1f0',['Ad rules evaluated by','Chrome’s network engine'])
b+=box(730,205,245,145,'popup.html / .js',BLUE,'#edf4ff',['Toolbar menu','Settings and picker commands'])
b+=arrow(270,75,355,75)+arrow(270,285,355,285)+arrow(720,285,640,285)
b+=txt(500,402,'Separate execution worlds exchange only necessary settings.',24,INK,700,'middle')
slide('Technical 1: Files and execution worlds','JavaScript (.js) runs behavior; JSON (.json) contains configuration and rules.',b,'The background is an event-driven service worker started by Chrome, not an always-running server.','The manifest uses Manifest V3. Content scripts start at document_start and also run in matching frames.')

b=box(20,45,220,190,'Stored settings',BLUE,'#edf4ff',['chrome.storage.local','enabled / overlays','Per-origin selected rules'])
b+=arrow(250,145,355,145,BLUE,'Read')+box(365,45,245,190,'content.js',BLUE,'#edf4ff',['Isolated extension world','Read settings; process DOM','Receive storage changes'])
b+=arrow(620,145,725,145,GREEN,'Publish')+box(735,45,245,190,'page-guard.js',GREEN,'#eaf8f2',['Page’s MAIN world','Popup guard enabled state','Wraps window.open'])
b+=box(235,295,530,100,'popup-blocker-setting',GOLD,'#fff8e8',['CustomEvent carries enabled as a JSON string'])
b+=txt(500,422,'Storage changes → refresh settings → update page behavior',22,INK,700,'middle')
slide('Technical 2: Delivering settings to the page','Both worlds share the document, but their JavaScript variables are separate.',b,'storage.onChanged triggers a refresh. content.js passes only enabled to the page guard.','Page scripts can tamper with this document event. It is a convenience bridge, not a security boundary.')

b=box(20,25,290,140,'window.open request',BLUE,'#edf4ff',['Keep the original function','Install a checking wrapper'])+arrow(320,95,380,95)
b+=box(390,25,590,140,'Does this request need a popup check?',BLUE,'#edf4ff',['Disabled → call the original function','_self / _parent / _top → bypass popup checks'])
b+=box(20,225,290,165,'Recent real user action',GOLD,'#fff8e8',['Trusted click or key input','An eligible link or button','Under 1 s + userActivation'])+arrow(320,300,380,300)
b+=box(390,225,275,165,'From a link',GREEN,'#eaf8f2',['Normalize the requested URL','Compare it with the link URL','Allow only an exact match'])
b+=box(700,225,280,165,'From a button',GREEN,'#eaf8f2',['Reject known ad hosts','Otherwise favor normal use','Call the original function'])
slide('Technical 3: Popup checks in the code','window.open is a browser function that page code uses to open a window or tab.',b,'Allowed requests call the original via Reflect.apply. Blocked requests return null without opening a window.','Synthetic clicks are also checked with preventDefault(). This function uses seven basic ad hosts, separate from site-specific network rules.')

b=box(20,70,220,210,'Page request',BLUE,'#edf4ff',['Destination host','Resource type','Initiating site'])+arrow(250,175,345,175)
b+=box(355,25,360,305,'Chrome’s request-rule engine',RED,'#fff1f0',['declarativeNetRequest','requestDomains: ad hosts','resourceTypes: script, sub_frame','Site scope: initiatorDomains','Matching request: action = block'])
b+=arrow(725,135,800,100,RED)+circle(850,100,30,'×',RED,'#fff1f0',39)+txt(850,155,'Block ad code',20,RED,anchor='middle')
b+=arrow(725,245,800,280,GREEN)+circle(850,280,30,'✓',GREEN,'#eaf8f2',32)+txt(850,335,'Other requests proceed',20,GREEN,anchor='middle')
b+=txt(500,403,'Current rules: general ad hosts + site-scoped hitomi.la hosts',23,INK,700,'middle')
slide('Technical 4: Block ad code before execution','A script is external executable code. A sub_frame is a separate embedded web page.',b,'Chrome applies these rules independently of the page wrapper. They do not target main_frame navigation.','popup.js uses updateEnabledRulesets to toggle the ruleset. Other resource types from those hosts are not blocked by these rules alone.')

b=box(20,30,250,165,'MutationObserver',BLUE,'#edf4ff',['Watch DOM additions/removals','id, class, src, style, etc.','Also watch attribute changes'])+arrow(280,110,360,110)
b+=box(370,30,250,165,'schedule → scan',GOLD,'#fff8e8',['One pending scan at a time','setTimeout(..., 50)','Rescan after changes'])+arrow(630,110,710,110)
b+=box(720,30,250,165,'Find ad candidates',RED,'#fff1f0',['Ad names / data-ad-overlay','Known advertising iframe URLs','Check candidate geometry'])
b+=box(115,255,770,120,'Geometry checks for general automatic rules',BLUE,'#edf4ff',['position: fixed or absolute; width and height > 0','area ≥ 15% of viewport AND (z-index ≥ 10 OR position: fixed)'])
slide('Technical 5: Detecting ad overlays','The DOM describes page elements. CSS controls their position, dimensions and appearance.',b,'50 ms schedules a scan; it is not a strict execution deadline or an unconditional polling interval.','Confirmed site ad classes bypass size checks. Manually selected overlays omit the 15% threshold but still require positioned geometry.')

b=box(20,65,230,240,'Save before hiding',BLUE,'#edf4ff',['A Map named hidden','Element objects are keys','Save original inline display','Save its priority as well'])+arrow(260,180,335,180)
b+=box(345,65,300,240,'Hide from view',RED,'#fff1f0',['display: none !important','Do not delete from the DOM','If the site shows it again,','the next scan hides it again'])+arrow(655,180,730,180,GREEN)
b+=box(740,65,235,240,'Disable and restore',GREEN,'#eaf8f2',['Restore only elements with','our hiding style still applied','Reapply the original style','Drop detached elements'])
b+=txt(500,402,'Hiding records live in page memory; selected rules live in Chrome storage.',21,INK,700,'middle')
slide('Technical 6: Hiding and restoration','The Map is a temporary record pairing an element with its original inline display style.',b,'Disabling blocking or overlay hiding restores styles. Changing or resetting selected rules restores elements before rescanning.','A page refresh creates new elements and a new Map. Saved selectors are read again and reapplied.')

b=box(20,25,220,145,'Send picker command',BLUE,'#edf4ff',['popup.js → active tab','tabs.sendMessage','pick-layer, frameId: 0'])+arrow(250,98,345,98)
b+=box(355,25,270,145,'Find the clicked element',GOLD,'#fff8e8',['Selection layer + Shadow DOM','elementFromPoint(x, y)','Walk up to an eligible ancestor'])+arrow(635,98,720,98)
b+=box(730,25,245,145,'Intercept the selection click',RED,'#fff1f0',['preventDefault','stopImmediatePropagation','Use the click only for selection'])
b+=box(65,265,360,130,'Build an element selector',BLUE,'#edf4ff',['Prefer a unique #id','Otherwise: path + nth-of-type','Escape the id with CSS.escape'])+arrow(435,330,535,330)
b+=box(545,265,400,130,'Save per-origin selectors',GREEN,'#eaf8f2',['layerRules:https://example.com','Store the selector list locally','Reapply to matching overlays'])
slide('Technical 7: Remember an element’s selector','A CSS selector is an expression used to find matching elements in the document.',b,'Temporarily bypass the selection layer to find the element below. Finish or press Esc to remove the picker and its listeners.','Rules are scoped to an origin (scheme + host + port). Matching structures on other pages also apply; changed structures need a new selection.')

b=box(20,25,460,195,'Required permissions',BLUE,'#edf4ff',['contentSettings: popup settings','storage: settings and site rules','declarativeNetRequest: block requests','activeTab: access the selected tab'])
b+=box(520,25,455,195,'Implementation limitations',GOLD,'#fff8e8',['Page code can bypass functions or events','Async settings read; initially enabled','Custom legitimate controls may be blocked','Changed selectors can miss an overlay'])
b+=box(20,270,955,130,'Separate behavior tests from integration tests',GREEN,'#eaf8f2',['Verified: unit tests and shipped scripts running on Chromium fixture pages','Unverified: installed extension, network-rule integration and live target-site behavior'])
slide('Technical 8: Permissions, limits and validation','This appendix describes the current code. It does not introduce new extension functionality.',b,'Network blocking uses Chrome’s engine; popup and overlay behavior uses page scripts. Testing one does not validate the other.','Cloud policy blocks unpacked extensions and the proxy denies the target site. The extension is not a security boundary or comprehensive ad defense.')


css='''@font-face{font-family:Guide;src:url(FONTDATA) format('woff');font-weight:100 900;font-display:block}*{box-sizing:border-box}body{margin:0;background:#e6edf5;color:#142338;font-family:Guide,"Noto Sans CJK KR",sans-serif}.toolbar{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:center;gap:14px;padding:12px;background:#142338;color:white}.toolbar button{border:0;border-radius:7px;background:#fff;color:#142338;padding:9px 15px;font:inherit;font-size:14px;cursor:pointer}.toolbar button:focus-visible{outline:3px solid #60a5fa}.slide{position:relative;width:1123px;height:794px;margin:26px auto;padding:42px 44px 55px;background:white;box-shadow:0 10px 40px #14233815;display:none;overflow:hidden}.slide.active,body.all .slide{display:block}.eyebrow{font-size:12px;letter-spacing:.06em;color:#607088;margin-bottom:12px}.slide h1{font-size:34px;line-height:1.3;margin:0 0 12px;font-weight:700;letter-spacing:-.8px}.subtitle{font-size:17px;line-height:1.7;margin:0;color:#607088}.drawing{height:450px;display:flex;align-items:center;margin-top:12px}.drawing svg{width:100%;max-height:450px;font-family:Guide,sans-serif}.takeaway{padding:14px 18px;border-left:5px solid #2563eb;background:#f1f6ff;font-size:18px;line-height:1.6;margin-top:8px;border-radius:0 10px 10px 0}.note{font-size:12px;line-height:1.65;color:#607088;margin:10px 0 0}.footer{position:absolute;bottom:19px;left:44px;right:44px;display:flex;justify-content:space-between;font-size:11px;color:#607088}.screen-note{text-align:center;color:#607088;font-size:13px;margin:15px}@page{size:A4 landscape;margin:0}@media print{body{background:white}.toolbar,.screen-note{display:none!important}.slide{display:block!important;width:297mm;height:210mm;margin:0;padding:11mm 12mm 14mm;box-shadow:none;break-after:page;page-break-after:always}.slide:last-of-type{break-after:auto;page-break-after:auto}.drawing{height:116mm}.slide h1{font-size:25pt}.subtitle{font-size:12pt}.takeaway{font-size:13pt}.note{font-size:9pt}.footer{left:12mm;right:12mm;bottom:5mm}.drawing svg{max-height:116mm}}'''
sections=[]
for i,(title,sub,drawing,takeaway,note) in enumerate(slides,1):
 sections.append(f'<section class="slide {"active" if i==1 else ""}" id="slide-{i}" aria-label="{i}. {escape(title)}"><div class="eyebrow">CHROME POPUP BLOCKER · An illustrated guide</div><h1>{escape(title)}</h1><p class="subtitle">{escape(sub)}</p><div class="drawing">{drawing}</div><div class="takeaway">{escape(takeaway)}</div><p class="note">{escape(note)}</p><div class="footer"><span>Based on v1.3.0 · October 7, 2026 · Illustrated guide</span><span>{i:02d} / {len(slides):02d}</span></div></section>')
script='''const slides=[...document.querySelectorAll('.slide')];let index=0;function show(n){index=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===index));document.querySelector('#count').textContent=`${index+1} / ${slides.length}`;history.replaceState(null,'',`#slide-${index+1}`);document.querySelector('#prev').disabled=index===0;document.querySelector('#next').disabled=index===slides.length-1;}document.querySelector('#prev').onclick=()=>show(index-1);document.querySelector('#next').onclick=()=>show(index+1);document.querySelector('#all').onclick=()=>{document.body.classList.toggle('all');document.querySelector('#all').textContent=document.body.classList.contains('all')?'Single slide':'Show all';};document.querySelector('#print').onclick=()=>window.print();document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();show(index+1);}if(e.key==='ArrowLeft'){e.preventDefault();show(index-1);}});show((parseInt(location.hash.replace('#slide-',''))||1)-1);'''
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Popup & Ad Overlay Blocker: Illustrated Guide</title><style>'+css+'</style></head><body><nav class="toolbar" aria-label="Guide navigation"><button id="prev">Previous</button><span id="count">1 / 12</span><button id="next">Next</button><button id="all">Show all</button><button id="print">Print / Save PDF</button></nav><p class="screen-note">Use the left/right arrow keys to navigate. This guide works offline.</p>'+''.join(sections)+'<script>'+script+'</script></body></html>'
html=html.replace('1 / 12',f'1 / {len(slides)}')
# Embed a subset font so the guide renders consistently offline.
font=subset.load_font('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',subset.Options(font_number=1))
opts=subset.Options();sub=subset.Subsetter(options=opts);sub.populate(text=''.join(set(re.sub('<[^>]+>','',html))));sub.subset(font);font.flavor='woff';path=Path('/tmp/popup-guide-font.woff');font.save(path)
html=html.replace('FONTDATA','data:font/woff;base64,'+base64.b64encode(path.read_bytes()).decode())
license_path=ROOT/'docs/FONT-LICENSE.txt'
if license_path.exists():html=html.replace('</head>','<!--\n'+license_path.read_text()+'\n--></head>')
(ROOT/'docs/popup-blocker-guide.html').write_text(html)
print('Created',len(slides),'slides; HTML bytes',len(html.encode()))
