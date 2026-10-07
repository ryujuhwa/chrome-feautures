const button = document.querySelector('#toggle');
const overlayControl = document.querySelector('#overlays');
const status = document.querySelector('#status');
let enabled = false;

async function refresh() {
  const current = await chrome.contentSettings.popups.get({primaryUrl: 'https://example.com/'});
  const settings = await chrome.storage.local.get(['enabled', 'overlays']);
  enabled = settings.enabled ?? true;
  overlayControl.checked = settings.overlays ?? true;
  overlayControl.disabled = false;
  status.textContent = `확장 프로그램 차단: ${enabled ? '켜짐' : '꺼짐'} · 크롬 설정: ${current.setting === 'block' ? '차단' : '허용'}`;
  button.textContent = enabled ? '이 확장 프로그램의 차단 해제' : '자동 팝업 차단 켜기';
  button.disabled = false;
}

function showError(error) {
  status.textContent = `설정을 변경하지 못했습니다: ${error.message}`;
  button.disabled = false;
}

button.addEventListener('click', async () => {
  button.disabled = true;
  try {
    if (enabled) {
      await chrome.contentSettings.popups.clear({scope: 'regular'});
    } else {
      await chrome.contentSettings.popups.set({primaryPattern: '<all_urls>', setting: 'block', scope: 'regular'});
    }
    await chrome.declarativeNetRequest.updateEnabledRulesets(!enabled ? {enableRulesetIds: ['ad_scripts']} : {disableRulesetIds: ['ad_scripts']});
    await chrome.storage.local.set({enabled: !enabled});
    await refresh();
  } catch (error) {
    showError(error);
  }
});
overlayControl.addEventListener('change', async () => {
  overlayControl.disabled = true;
  try {
    await chrome.storage.local.set({overlays: overlayControl.checked});
    await refresh();
  } catch (error) {
    overlayControl.disabled = false;
    showError(error);
  }
});
refresh().catch(showError);

async function sendToPage(type) {
  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  if (!tab?.id) throw new Error('현재 웹페이지를 찾지 못했습니다.');
  let result;
  try {
    result = await chrome.tabs.sendMessage(tab.id, {type}, {frameId: 0});
  } catch {
    throw new Error('웹사이트를 새로고침한 뒤 다시 시도하세요. 크롬 설정 페이지에서는 사용할 수 없습니다.');
  }
  if (result?.error) throw new Error(result.error);
}
document.querySelector('#pick-layer').addEventListener('click', async () => {
  try {
    if (!enabled || !overlayControl.checked) throw new Error('먼저 차단과 광고 레이어 숨기기를 켜 주세요.');
    await sendToPage('pick-layer');
    window.close();
  } catch (error) { showError(error); }
});
document.querySelector('#reset-layers').addEventListener('click', async () => {
  try {
    await sendToPage('reset-layers');
    status.textContent = '이 사이트에서 직접 선택한 차단 규칙을 삭제했습니다.';
  } catch (error) { showError(error); }
});
