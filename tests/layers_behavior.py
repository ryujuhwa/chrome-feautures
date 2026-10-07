"""Test technical advertising-overlay structures, without site content or remote requests."""
from pathlib import Path
from playwright.sync_api import sync_playwright
root = Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/lib/chromium/chromium',headless=True,args=['--no-sandbox'])
    context = browser.new_context()
    context.route('https://hitomi.la/**', lambda r: r.fulfill(content_type='text/html',body='''
    <style>
    .__bai-container {position:fixed;inset:0;z-index:9999999}
    .__inst-container {position:fixed;right:0;bottom:0;width:360px;height:160px;z-index:9999999}
    </style>
    <div class="__bai-container">Ad SDK overlay</div>
    <div class="__inst-container">Ad SDK corner layer</div>
    <div id="normal" role="dialog" style="position:fixed;left:0;top:0;width:300px;height:100px;z-index:20">Normal dialog</div>
    <div id="random-layer" style="position:fixed;right:0;top:0;width:360px;height:160px;z-index:1000"><span>Unidentified overlay</span></div>'''))
    page=context.new_page()
    try:
        page.goto('https://hitomi.la/fixture')
        page.evaluate('''() => {
          window.data={enabled:true,overlays:true};
          window.chrome={runtime:{onMessage:{addListener:fn=>{window.onMessage=fn;}}},
            storage:{local:{get:async()=>data,set:async v=>{Object.assign(data,v);onChange({},'local');},
            remove:async key=>{delete data[key];onChange({},'local');}},
            onChanged:{addListener:fn=>{window.onChange=fn;}}}};
        }''')
        page.add_script_tag(path=str(root/'extension/content.js'))
        page.wait_for_function("getComputedStyle(document.querySelector('.__inst-container')).display==='none'")
        assert not page.locator('.__bai-container').is_visible()
        assert page.locator('#normal').is_visible()
        assert page.locator('#random-layer').is_visible()
        print('PASS: supplied SDK fullscreen and small corner layers hidden; normal dialog preserved')
        page.locator('#random-layer').evaluate("node=>{const frame=document.createElement('iframe');frame.srcdoc='Advertising frame';frame.style.cssText='width:100%;height:100%;border:0';node.replaceChildren(frame);}")
        page.evaluate("() => onMessage({type:'pick-layer'},null,()=>{})")
        box=page.locator('#random-layer').bounding_box()
        page.mouse.click(box['x']+20,box['y']+20)
        page.wait_for_function("getComputedStyle(document.querySelector('#random-layer')).display==='none'")
        assert page.evaluate("data['layerRules:https://hitomi.la'].includes('#random-layer')")
        # Simulate a site trying to show the same node again.
        page.locator('#random-layer').evaluate("node=>node.style.setProperty('display','block','important')")
        page.wait_for_function("getComputedStyle(document.querySelector('#random-layer')).display==='none'")
        # Simulate reinsertion after the original node is removed.
        page.locator('#random-layer').evaluate("node=>{const replacement=node.cloneNode(true);replacement.style.removeProperty('display');node.replaceWith(replacement);}")
        page.wait_for_function("getComputedStyle(document.querySelector('#random-layer')).display==='none'")
        print('PASS: manual selection saved; same-node and replacement-layer recurrence hidden')
        page.evaluate("() => new Promise(resolve=>onMessage({type:'reset-layers'},null,resolve))")
        page.wait_for_function("getComputedStyle(document.querySelector('#random-layer')).display!=='none'")
        assert page.locator('#normal').is_visible()
        print('PASS: resetting custom rules restores selected overlay')
        # A saved selector must never hide ordinary content reused with the same ID.
        page.locator('#random-layer').evaluate("node=>node.style.position='static'")
        page.evaluate("() => {data['layerRules:https://hitomi.la']=['#random-layer'];onChange({},'local');}")
        page.wait_for_timeout(150)
        assert page.locator('#random-layer').is_visible()
        print('PASS: saved overlay selector preserves ordinary content')
    finally:
        context.close();browser.close()
