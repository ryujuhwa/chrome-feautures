(() => {
  let enabled = true;
  let intent = null;
  const nativeOpen = window.open;
  const adHosts = /(^|\.)(doubleclick\.net|googlesyndication\.com|popads\.net|popcash\.net|adsterra\.com|exoclick\.com|juicyads\.com)$/i;
  const absolute = value => {
    try { return new URL(value || 'about:blank', location.href).href; }
    catch { return null; }
  };
  const isAd = value => {
    try { return adHosts.test(new URL(value, location.href).hostname); }
    catch { return false; }
  };
  const interactive = event => event.composedPath().find(node =>
    node instanceof Element && node.matches('a[href], button, input[type="submit"], input[type="button"], [role="button"]'));
  const remember = event => {
    if (!event.isTrusted) return;
    const control = interactive(event);
    intent = control ? {
      time: performance.now(),
      url: control.matches('a[href]') ? absolute(control.href) : null
    } : null;
  };
  document.addEventListener('click', remember, true);
  document.addEventListener('auxclick', remember, true);
  document.addEventListener('keydown', event => {
    if (event.key === 'Enter' || event.key === ' ') remember(event);
  }, true);

  // This event transports a non-secret setting from the isolated extension world.
  // Page scripts can tamper with it; this is a convenience blocker, not a security boundary.
  document.addEventListener('popup-blocker-setting', event => {
    try { enabled = JSON.parse(event.detail).enabled !== false; } catch {}
  });

  function allowed(url) {
    if (!enabled) return true;
    const recent = intent && performance.now() - intent.time < 1000 && navigator.userActivation.isActive;
    if (!recent) return false;
    // An explicit link to the requested URL represents the user's intent.
    if (intent.url) return absolute(url) === intent.url;
    // Preserve button-driven sign-in/payment flows unless the destination is a known ad host.
    return !isAd(url);
  }

  window.open = function(url, target, features) {
    const destination = String(target || '_blank').toLowerCase();
    // Same-tab navigation is not a popup.
    if (!['_self', '_parent', '_top'].includes(destination) && !allowed(url)) return null;
    return Reflect.apply(nativeOpen, this, arguments);
  };

  // Stop synthetic anchor clicks that try to evade window.open interception.
  document.addEventListener('click', event => {
    if (!enabled || event.isTrusted) return;
    const link = event.composedPath().find(node => node instanceof Element && node.matches('a[href]'));
    if (link && !['_self', '_parent', '_top'].includes((link.target || '_self').toLowerCase()) && !allowed(link.href)) {
      event.preventDefault();
    }
  }, true);
})();
