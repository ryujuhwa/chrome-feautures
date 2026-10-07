from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/lib/chromium/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport={'width':1220,'height':960},device_scale_factor=1)
 page.set_content((root/'docs/popup-blocker-guide.html').read_text(), wait_until='load')
 page.evaluate('document.fonts.ready')
 page.pdf(path=str(root/'downloads/popup-blocker-guide.pdf'),print_background=True,prefer_css_page_size=True)
 page.locator('#all').click()
 for i in [1,5,9,12,13,15,17,19,20]:
  page.locator(f'#slide-{i}').screenshot(path=f'/tmp/popup-guide-{i}.png')
 checks=page.evaluate('''() => [...document.querySelectorAll('.slide')].map(s=>({id:s.id,items:[...s.querySelectorAll('h1,.drawing,.takeaway,.note')].map(e=>({tag:e.tagName,bottom:e.getBoundingClientRect().bottom-s.getBoundingClientRect().top})),footer:s.querySelector('.footer').getBoundingClientRect().top-s.getBoundingClientRect().top}))''')
 for s in checks:
  bad=[v for v in s['items'] if v['bottom']>s['footer']-3]
  if bad: print('OVERFLOW',s['id'],bad,'footer',s['footer'])
 page.locator('#all').click()
 page.locator('#next').click()
 assert page.locator('#count').inner_text()=='2 / 20'
 page.keyboard.press('ArrowLeft')
 assert page.locator('#count').inner_text()=='1 / 20'
 assert page.locator('.slide.active').count()==1
 print('PDF generated; offline navigation verified; slides',page.locator('.slide').count())
 browser.close()
try:
 import fitz
 doc=fitz.open(root/'downloads/popup-blocker-guide.pdf')
 print('PDF pages',len(doc),'dimensions',tuple(round(v,1) for v in doc[0].rect))
 assert len(doc)==20
 for i,page in enumerate(doc):
  text=page.get_text()
  assert len(text)>80,(i,len(text))
 print('PDF text is selectable on all pages')
except ImportError: print('PDF parser unavailable')
