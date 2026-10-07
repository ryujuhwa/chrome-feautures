const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function setup(settings = {}) {
  let onCreated;
  const removed = [];
  vm.runInNewContext(fs.readFileSync('extension/background.js', 'utf8'), {console, chrome: {
    runtime: {onInstalled: {addListener: () => {}}},
    storage: {local: {get: async () => settings}},
    tabs: {onCreated: {addListener: fn => {onCreated = fn;}}, remove: async id => {removed.push(id);}}
  }});
  return {created: tab => onCreated(tab), removed};
}

test('strict closes opener tabs including blank popups and preserves manual windows', async () => {
  const app = setup();
  await app.created({id: 2, openerTabId: 0, url: 'about:blank'});
  await app.created({id: 3, openerTabId: 1, url: 'https://example.com'});
  await app.created({id: 4, url: 'about:blank'});
  assert.deepEqual(app.removed, [2, 3]);
});

test('disabled extension or disabled strict mode preserves site-created tabs', async () => {
  for (const settings of [{enabled:false,strict:true},{enabled:true,strict:false}]) {
    const app = setup(settings);
    await app.created({id: 2, openerTabId: 1});
    assert.deepEqual(app.removed, []);
  }
});
