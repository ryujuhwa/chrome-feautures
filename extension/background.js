chrome.runtime.onInstalled.addListener(async () => {
  const { enabled = true } = await chrome.storage.local.get('enabled');
  if (enabled) {
    await chrome.contentSettings.popups.set({primaryPattern: '<all_urls>', setting: 'block', scope: 'regular'});
  }
  await chrome.storage.local.set({enabled});
});
