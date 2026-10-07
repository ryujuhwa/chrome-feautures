chrome.runtime.onInstalled.addListener(async () => {
  const { enabled = true, strict = true } = await chrome.storage.local.get(['enabled', 'strict']);
  if (enabled) {
    await chrome.contentSettings.popups.set({primaryPattern: '<all_urls>', setting: 'block', scope: 'regular'});
  }
  await chrome.storage.local.set({enabled, strict});
});

// openerTabId identifies a tab opened by another tab. Do not guess from an
// about:blank URL: manually opened windows can have that URL too.
chrome.tabs.onCreated.addListener(async tab => {
  if (tab.openerTabId === undefined || tab.id === undefined) return;
  const { enabled = true, strict = true } = await chrome.storage.local.get(['enabled', 'strict']);
  if (!enabled || !strict) return;
  try {
    await chrome.tabs.remove(tab.id);
  } catch (error) {
    // The page or user may already have closed the tab.
    console.debug('Popup tab could not be closed:', error.message);
  }
});
