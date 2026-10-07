(() => {
  let enabled = true;
  let overlays = true;
  let timer = null;
  const hidden = new Map();
  const adHost = /(^|\.)(doubleclick\.net|googlesyndication\.com|popads\.net|popcash\.net|adsterra\.com|exoclick\.com|juicyads\.com)$/i;
  const marker = /(?:^|[\s_-])(?:ad|ads|advert|advertisement)[_-](?:overlay|modal|popup|interstitial)(?:$|[\s_-])|(?:^|[\s_-])(?:overlay|modal|popup|interstitial)[_-](?:ad|ads|advert|advertisement)(?:$|[\s_-])/i;

  function advertisingFrame(element) {
    try { return element.tagName === 'IFRAME' && adHost.test(new URL(element.src, location.href).hostname); }
    catch { return false; }
  }
  function isOverlay(element) {
    const style = getComputedStyle(element);
    const box = element.getBoundingClientRect();
    return ['fixed', 'absolute'].includes(style.position) &&
      box.width * box.height >= innerWidth * innerHeight * 0.15 &&
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
    for (const element of document.querySelectorAll('[data-ad-overlay], [id*="ad" i], [class*="ad" i], iframe')) {
      if (hidden.has(element)) continue;
      const marked = element.hasAttribute('data-ad-overlay') || marker.test(`${element.id} ${element.getAttribute('class') || ''}`);
      if ((marked || advertisingFrame(element)) && isOverlay(element)) hide(element);
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
    const settings = await chrome.storage.local.get(['enabled', 'overlays']);
    enabled = settings.enabled ?? true;
    overlays = settings.overlays ?? true;
    publish();
    if (!enabled || !overlays) restore();
    else schedule();
  }
  const observer = new MutationObserver(schedule);
  observer.observe(document, {subtree: true, childList: true, attributes: true, attributeFilter: ['id', 'class', 'src', 'style', 'data-ad-overlay']});
  chrome.storage.onChanged.addListener((_changes, area) => {
    if (area === 'local') refresh().catch(console.error);
  });
  window.addEventListener('resize', schedule);
  document.addEventListener('DOMContentLoaded', () => {publish(); schedule();}, {once: true});
  refresh().catch(console.error);
})();
