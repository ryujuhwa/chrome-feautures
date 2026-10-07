"""Run the shipped guards in a real DOM. Chrome storage is a test fixture.
This does not claim unpacked-extension installation has been tested.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/lib/chromium/chromium', headless=True,
                                args=['--no-sandbox'], ignore_default_args=['--disable-popup-blocking'])
    context = browser.new_context()
    context.route('https://fixture.example/**', lambda route: route.fulfill(
        body='''<a id="link" href="/manual" target="_blank">Manual link</a>
        <a id="same" href="/ctrl">Same-tab link</a>
        <a id="hijack" href="/intended" onclick="event.preventDefault();window.hijackResult=window.open('about:blank')">Link with ad side effect</a>
        <button id="login" onclick="window.open('/login')">Login</button>
        <div id="empty" onclick="window.result = window.open('about:blank')">Empty area advertisement</div>
        <div id="ad-overlay" style="position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.1)">Advertising</div>
        <div id="login-modal" role="dialog" style="position:fixed;top:20px;left:400px;width:300px;height:300px;z-index:20">Normal login dialog</div>''',
        content_type='text/html'))
    context.add_init_script(path=str(root / 'extension/page-guard.js'))
    page = context.new_page()
    try:
        page.goto('https://fixture.example/')
        assert page.evaluate("window.open('/automatic') === null")
        # A trusted click on a noninteractive region must not grant popup intent.
        page.locator('#ad-overlay').evaluate("node => node.style.display='none'")
        page.locator('#empty').click(position={'x':10,'y':5})
        assert page.evaluate('window.result === null')
        print('PASS: automatic and unrelated-click popup blocked')
        with context.expect_page() as event:
            page.locator('#link').click()
        manual = event.value
        manual.wait_for_load_state()
        assert manual.url.endswith('/manual')
        manual.close()
        with context.expect_page() as event:
            page.locator('#same').click(modifiers=['Control'])
        ctrl = event.value
        ctrl.wait_for_load_state()
        assert ctrl.url.endswith('/ctrl')
        ctrl.close()
        page.locator('#hijack').click()
        assert page.evaluate('window.hijackResult === null')
        with context.expect_page() as event:
            page.locator('#login').click()
        login = event.value
        login.wait_for_load_state()
        assert login.url.endswith('/login')
        login.close()
        print('PASS: intentional native new-tab link and login button preserved')
        page.wait_for_timeout(1100)
        assert page.evaluate("""() => {
          const a=document.createElement('a');a.href='/synthetic';a.target='_blank';
          document.body.append(a);
          const event=new MouseEvent('click',{bubbles:true,cancelable:true});
          a.dispatchEvent(event);a.remove();return event.defaultPrevented;
        }""")
        print('PASS: synthetic new-tab anchor blocked')
        page.evaluate("""() => {
          window.fixtureSettings={enabled:true,overlays:true};
          window.chrome={storage:{local:{get:async()=>window.fixtureSettings},
            onChanged:{addListener:fn=>{window.fixtureChanged=fn;}}}};
          document.querySelector('#ad-overlay').style.removeProperty('display');
        }""")
        page.add_script_tag(path=str(root / 'extension/content.js'))
        page.wait_for_function("getComputedStyle(document.querySelector('#ad-overlay')).display === 'none'")
        assert page.locator('#login-modal').is_visible()
        page.evaluate('''() => {
          const layer=document.createElement('div');layer.id='ads-modal';
          layer.style.cssText='position:fixed;inset:0;z-index:500';
          document.body.append(layer);
        }''')
        page.wait_for_function("getComputedStyle(document.querySelector('#ads-modal')).display === 'none'")
        print('PASS: initial and dynamically inserted ad overlays hidden; normal dialog preserved')
        page.evaluate("() => {fixtureSettings.overlays=false;fixtureChanged({},'local');}")
        page.wait_for_function("getComputedStyle(document.querySelector('#ad-overlay')).display !== 'none'")
        page.evaluate("() => {fixtureSettings.enabled=false;fixtureChanged({},'local');}")
        page.wait_for_timeout(100)
        with context.expect_page() as event:
            page.locator('#ad-overlay, #ads-modal').evaluate_all("nodes => nodes.forEach(node => node.style.display='none')")
            page.locator('#empty').click(position={'x':10,'y':5})
        event.value.close()
        print('PASS: disable restores overlay and allows previously blocked click popup')
    finally:
        context.close()
        browser.close()
