(() => {
  let enabled = true;
  let overlays = true;
  let timer = null;
  const hidden = new Map();
  const ruleKey = `layerRules:${location.origin}`;
  let customRules = [];
  let cancelPicker = null;
  let pickerHost = null;
  const adHost = /(^|\.)(doubleclick\.net|googlesyndication\.com|popads\.net|popcash\.net|adsterra\.com|exoclick\.com|juicyads\.com)$/i;
  const marker = /(?:^|[\s_-])(?:ad|ads|advert|advertisement)[_-](?:overlay|modal|popup|interstitial)(?:$|[\s_-])|(?:^|[\s_-])(?:overlay|modal|popup|interstitial)[_-](?:ad|ads|advert|advertisement)(?:$|[\s_-])/i;

  function advertisingFrame(element) {
    try { return element.tagName === 'IFRAME' && adHost.test(new URL(element.src, location.href).hostname); }
    catch { return false; }
  }
  function isOverlay(element, minimumArea = 0.15) {
    const style = getComputedStyle(element);
    const box = element.getBoundingClientRect();
    return ['fixed', 'absolute'].includes(style.position) &&
      box.width > 0 && box.height > 0 &&
      box.width * box.height >= innerWidth * innerHeight * minimumArea &&
      (Number.parseInt(style.zIndex, 10) >= 10 || style.position === 'fixed');
  }
  function hide(element) {
    if (hidden.has(element)) return;
    hidden.set(element, {value: element.style.getPropertyValue('display'), priority: element.style.getPropertyPriority('display')});
    element.style.setProperty('display', 'none', 'important');
  }
  function restore() {
    for (const [element, previous] of hidden) {
      if (element.style.getPropertyValue('display') === 'none' && element.style.getPropertyPriority('display') === 'important') {
        if (previous.value) element.style.setProperty('display', previous.value, previous.priority);
        else element.style.removeProperty('display');
      }
    }
    hidden.clear();
  }
  function scan() {
    timer = null;
    if (!enabled || !overlays) return;
    for (const element of hidden.keys()) {
      if (element.isConnected && (element.style.getPropertyValue('display') !== 'none' || element.style.getPropertyPriority('display') !== 'important')) {
        element.style.setProperty('display', 'none', 'important');
      }
    }
    for (const element of document.querySelectorAll('[data-ad-overlay], [id*="ad" i], [class*="ad" i], iframe')) {
      if (hidden.has(element)) continue;
      const marked = element.hasAttribute('data-ad-overlay') || marker.test(`${element.id} ${element.getAttribute('class') || ''}`);
      if ((marked || advertisingFrame(element)) && isOverlay(element)) hide(element);
    }
    // These advertising SDK classes were supplied in the user's captured HTML.
    // Scope exact vendor markers to the affected site; small corner ads count too.
    if (location.hostname === 'hitomi.la' || location.hostname.endsWith('.hitomi.la')) {
      for (const element of document.querySelectorAll('.gfpl-overlay, .__bai-container, .__inst-container')) hide(element);
    }
    for (const selector of customRules) {
      try {
        for (const element of document.querySelectorAll(selector)) {
          // A reused selector must still identify an overlay, never ordinary page content.
          if (isOverlay(element, 0) && element !== document.body && element !== document.documentElement) hide(element);
        }
      } catch { /* Ignore obsolete selectors. */ }
    }
    // Do not retain detached nodes indefinitely on long-lived pages.
    for (const element of hidden.keys()) if (!element.isConnected) hidden.delete(element);
  }
  function schedule() {
    if (timer === null) timer = setTimeout(scan, 50);
  }
  function publish() {
    document.dispatchEvent(new CustomEvent('popup-blocker-setting', {detail: JSON.stringify({enabled})}));
  }
  async function refresh() {
    const settings = await chrome.storage.local.get(['enabled', 'overlays', ruleKey]);
    const nextRules = Array.isArray(settings[ruleKey]) ? settings[ruleKey].filter(value => typeof value === 'string') : [];
    if (JSON.stringify(nextRules) !== JSON.stringify(customRules)) restore();
    customRules = nextRules;
    enabled = settings.enabled ?? true;
    overlays = settings.overlays ?? true;
    publish();
    if (!enabled || !overlays) {
      if (cancelPicker) cancelPicker();
      restore();
    }
    else schedule();
  }
  function selectorFor(element) {
    const segments = [];
    for (let current = element; current && current !== document.body; current = current.parentElement) {
      if (current.id) {
        const id = `#${CSS.escape(current.id)}`;
        if (document.querySelectorAll(id).length === 1) return [id, ...segments].join(' > ');
      }
      const siblings = [...current.parentElement.children].filter(node => node.tagName === current.tagName);
      segments.unshift(`${current.tagName.toLowerCase()}:nth-of-type(${siblings.indexOf(current) + 1})`);
    }
    return `body > ${segments.join(' > ')}`;
  }
  function candidateAt(x, y) {
    if (pickerHost) pickerHost.style.setProperty('pointer-events', 'none', 'important');
    let element = document.elementFromPoint(x, y);
    if (pickerHost) pickerHost.style.setProperty('pointer-events', 'auto', 'important');
    for (; element && element !== document.body && element !== document.documentElement; element = element.parentElement) {
      if (isOverlay(element, 0)) return element;
    }
    return null;
  }
  function startPicker() {
    if (cancelPicker) cancelPicker();
    const host = document.createElement('div');
    host.style.cssText = 'position:fixed!important;inset:0!important;z-index:2147483647!important;pointer-events:auto!important;display:block!important';
    pickerHost = host;
    const shadow = host.attachShadow({mode: 'closed'});
    const help = document.createElement('div');
    help.style.cssText = 'position:fixed;top:12px;left:12px;background:#111;color:#fff;padding:14px;border-radius:8px;font:14px system-ui;max-width:400px;pointer-events:none';
    help.textContent = '숨길 광고 덮개 위에 마우스를 놓고 클릭하세요. 취소: Esc';
    const outline = document.createElement('div');
    outline.style.cssText = 'position:fixed;border:3px solid #ef4444;box-sizing:border-box;background:rgba(239,68,68,.12);pointer-events:none;display:none';
    shadow.append(outline, help);
    document.documentElement.append(host);
    const move = event => {
      const element = candidateAt(event.clientX, event.clientY);
      outline.style.display = element ? 'block' : 'none';
      if (element) {
        const box = element.getBoundingClientRect();
        Object.assign(outline.style, {left: `${box.left}px`, top: `${box.top}px`, width: `${box.width}px`, height: `${box.height}px`});
      }
    };
    const cleanup = () => {
      window.removeEventListener('mousemove', move, true);
      window.removeEventListener('click', pick, true);
      window.removeEventListener('keydown', key, true);
      host.remove();
      pickerHost = null;
      cancelPicker = null;
    };
    const pick = async event => {
      event.preventDefault();
      event.stopImmediatePropagation();
      if (!event.isTrusted) return;
      const element = candidateAt(event.clientX, event.clientY);
      if (!element) {
        help.textContent = '광고 덮개를 찾지 못했습니다. 광고 위를 선택하거나 Esc로 취소하세요.';
        return;
      }
      const selector = selectorFor(element);
      try {
        const settings = await chrome.storage.local.get(ruleKey);
        const previous = Array.isArray(settings[ruleKey]) ? settings[ruleKey] : [];
        customRules = [...new Set([...previous, selector])];
        await chrome.storage.local.set({[ruleKey]: customRules});
        hide(element);
        cleanup();
      } catch (error) {
        help.textContent = `저장하지 못했습니다: ${error.message}. 취소: Esc`;
      }
    };
    const key = event => {
      if (event.key === 'Escape') {
        event.preventDefault();
        event.stopImmediatePropagation();
        cleanup();
      }
    };
    cancelPicker = cleanup;
    window.addEventListener('mousemove', move, true);
    window.addEventListener('click', pick, true);
    window.addEventListener('keydown', key, true);
  }
  chrome.runtime.onMessage.addListener((message, _sender, respond) => {
    if (message.type === 'pick-layer') {
      startPicker();
      respond({ok: true});
    } else if (message.type === 'reset-layers') {
      chrome.storage.local.remove(ruleKey).then(() => {
        customRules = [];
        restore();
        schedule();
        respond({ok: true});
      }).catch(error => respond({error: error.message}));
      return true;
    }
  });
  const observer = new MutationObserver(schedule);
  observer.observe(document, {subtree: true, childList: true, attributes: true, attributeFilter: ['id', 'class', 'src', 'style', 'data-ad-overlay']});
  chrome.storage.onChanged.addListener((_changes, area) => {
    if (area === 'local') refresh().catch(console.error);
  });
  window.addEventListener('resize', schedule);
  document.addEventListener('DOMContentLoaded', () => {publish(); schedule();}, {once: true});
  refresh().catch(console.error);
})();
