const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('extension/popup.js', 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));

function setup(initial = true) {
  let enabled = initial;
  let click;
  const calls = [];
  const button = {addEventListener: (_, callback) => {click = callback;}};
  const status = {};
  const api = {
    get: async () => ({setting: 'block'}),
    set: async options => {calls.push(['set', options]);},
    clear: async options => {calls.push(['clear', options]);}
  };
  vm.runInNewContext(source, {
    document: {querySelector: selector => selector === '#toggle' ? button : status},
    chrome: {contentSettings: {popups: api}, storage: {local: {
      get: async () => ({enabled}), set: async state => {enabled = state.enabled;}
    }}}
  });
  return {button, status, calls, api, click: () => click(), enabled: () => enabled};
}

test('disable clears only extension rules; Chrome can remain blocked', async () => {
  const app = setup(); await tick(); await app.click();
  assert.deepEqual(JSON.parse(JSON.stringify(app.calls)), [['clear', {scope:'regular'}]]);
  assert.equal(app.enabled(), false);
  assert.match(app.status.textContent, /꺼짐.*차단/);
  await app.click();
  assert.equal(app.calls[1][0], 'set');
  assert.equal(app.calls[1][1].setting, 'block');
  assert.equal(app.enabled(), true);
});

test('setting failure keeps stored state and enables retry', async () => {
  const app = setup(false); await tick();
  app.api.set = async () => {throw new Error('policy denied');};
  await app.click();
  assert.equal(app.enabled(), false);
  assert.equal(app.button.disabled, false);
  assert.match(app.status.textContent, /policy denied/);
});

test('installation enables blocking and updates preserve opt-out', async () => {
  const background = fs.readFileSync('extension/background.js', 'utf8');
  for (const existing of [undefined, false]) {
    let callback, stored, sets = 0;
    vm.runInNewContext(background, {chrome: {
      runtime: {onInstalled: {addListener: fn => {callback = fn;}}},
      storage: {local: {get: async () => ({enabled: existing}), set: async state => {stored = state.enabled;}}},
      contentSettings: {popups: {set: async () => {sets++;}}}
    }});
    await callback();
    assert.equal(stored, existing === undefined);
    assert.equal(sets, existing === undefined ? 1 : 0);
  }
});
