chrome.runtime.onInstalled.addListener(async () => {
  const { enabled = true, overlays = true } = await chrome.storage.local.get(['enabled', 'overlays']);
  if (enabled) {
    await chrome.contentSettings.popups.set({primaryPattern: '<all_urls>', setting: 'block', scope: 'regular'});
  }
  await chrome.declarativeNetRequest.updateEnabledRulesets(enabled ? {enableRulesetIds: ['ad_scripts']} : {disableRulesetIds: ['ad_scripts']});
  await chrome.storage.local.set({enabled, overlays});
});
