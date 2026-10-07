"""Exercise the real unpacked extension and Chrome popup behavior."""
from pathlib import Path
from tempfile import TemporaryDirectory
from playwright.sync_api import sync_playwright

extension = str(Path(__file__).resolve().parents[1] / 'extension')
with TemporaryDirectory() as profile, sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        profile, executable_path='/usr/lib/chromium/chromium', headless=True,
        args=[f'--disable-extensions-except={extension}', f'--load-extension={extension}', '--no-sandbox', '--enable-unsafe-extension-debugging'],
        ignore_default_args=['--disable-extensions', '--disable-popup-blocking'])
    context.set_default_timeout(15000)
    print('Browser launched', flush=True)
    try:
        session = context.browser.new_browser_cdp_session()
        session.send('Extensions.loadUnpacked', {'path': extension})
        worker = context.service_workers[0] if context.service_workers else context.wait_for_event('serviceworker')
        # Wait for installation to complete before reading its stored state.
        print('Extension worker loaded', flush=True)
        page = context.new_page()
        page.goto(f"chrome-extension://{worker.url.split('/')[2]}/popup.html")
        page.wait_for_function("!document.querySelector('#toggle').disabled")
        assert '켜짐' in page.locator('#status').inner_text()
        page.locator('#strict').uncheck()
        page.wait_for_function("!document.querySelector('#strict').disabled")
        page.locator('#toggle').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('꺼짐')")
        page.locator('#toggle').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('켜짐')")
        setting = worker.evaluate("async () => (await chrome.contentSettings.popups.get({primaryUrl:'https://example.com'})).setting")
        assert setting == 'block', setting
        target = context.new_page()
        target.route('https://popup-test.example/**', lambda route: route.fulfill(
            body='<button onclick="window.open(\'/clicked\')">Open</button>', content_type='text/html'))
        target.goto('https://popup-test.example/')
        result = target.evaluate("() => window.open('/automatic') === null")
        assert result, 'Automatic popup was not blocked'
        with context.expect_page() as event:
            target.locator('button').click()
        opened = event.value
        opened.wait_for_load_state()
        assert opened.url.endswith('/clicked'), opened.url
        page.locator('#strict').check()
        page.wait_for_function("!document.querySelector('#strict').disabled")
        with context.expect_page() as strict_event:
            target.locator('button').click()
        strict_popup = strict_event.value
        if not strict_popup.is_closed():
            strict_popup.wait_for_event('close')
        assert strict_popup.is_closed()
        page.locator('#toggle').click()
        page.wait_for_function("document.querySelector('#status').textContent.includes('꺼짐')")
        assert worker.evaluate("async () => (await chrome.storage.local.get('enabled')).enabled") is False
        print('PASS: real extension loads; toggle on/off; automatic popup blocked; clicked popup allowed')
    finally:
        context.close()
