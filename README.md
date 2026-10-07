# Popup & Ad Overlay Blocker v1.3.0

A Chrome Manifest V3 extension that reduces unwanted scripted popups and identifiable advertising overlays while preserving intentional links. The blanket tab-closing mode from v1.1.0 has been removed. The extension does not collect browsing history or send it to an external collection server.

## Install or update on Windows

1. [Download the extension ZIP](https://github.com/ryujuhwa/chrome-feautures/raw/refs/heads/main/downloads/chrome-popup-blocker.zip).
2. In Downloads, right-click the ZIP and select **Extract All**. Extract into a new folder.
3. Open `chrome://extensions`. Remove the previous version if it is installed.
4. Enable **Developer mode**, select **Load unpacked**, and choose the extracted `chrome-popup-blocker/extension` folder. It must contain `manifest.json`.
5. Confirm version **1.3.0** and refresh any website tabs that were already open. Chrome does not need to restart.

Allow the extension to run on the websites you want to protect. Recent updates added website access and request-blocking permissions. Incognito browsing is not covered by default.

The extension interface remains in Korean. English menu names in this documentation and its diagrams describe the corresponding actions.

## Behavior

- Ordinary links, Ctrl-click, middle-click and windows opened through Chrome's menu are not indiscriminately closed.
- Scripted `window.open` requests without a qualifying user action, popups attached to clicks on noninteractive areas, and link scripts opening an unrelated address are blocking candidates.
- Button-driven sign-in and payment popups are normally preserved immediately after a real click. Popups to known advertising hosts are rejected by the page guard.
- Chrome's request rules block scripts and embedded frames from the general advertising host list: doubleclick.net, googlesyndication.com, popads.net, popcash.net, adsterra.com, exoclick.com and juicyads.com.
- Additional script/frame rules for displayvertising.com, capndr.com, wpushsdk.com, cabnnr.com, wpadmngr.com, rtbbtr.com, darnobedienceupscale.com and adsco.re apply to requests initiated by hitomi.la. These hosts were identified in user-provided HTML. The site's content CDN and ordinary page-navigation requests are not targeted by those rules.
- Overlay hiding targets large positioned elements identified by advertising markers such as `ad-overlay`, `ads-modal` or `data-ad-overlay`, or known advertising iframe URLs. Dynamically added elements are scanned too. Ordinary dialogs and menus are not blanket hiding targets.
- On hitomi.la, confirmed ad SDK selectors `.gfpl-overlay`, `.__bai-container` and `.__inst-container` also hide smaller corner ads. Unrecognized overlays can be added with **Select an ad overlay**.
- Overall blocking and overlay hiding can be toggled separately. Disabling overlay hiding restores the extension's saved display styles. Disabling overall blocking also disables the request rules and restores Chrome's previous native popup setting, which may still block popups.

## Limitations and validation status

User intent cannot be inferred perfectly. Ads attached to buttons, new advertising hosts, unmarked overlays and same-site advertising can escape detection. A legitimate popup from a custom control can also be blocked; temporarily disable blocking if needed. The page guard is not a security boundary and sites can bypass it. Existing windows and windows opened by external programs are not closed.

The hitomi.la-specific rules were derived from user-provided HTML. Chromium fixture tests reproduced the technical advertising structures without including the site's actual content. The supplied HTML and advertising tracking values are not included in the repository or download bundles.

The cloud proxy denied live hitomi.la access with HTTP 403, so live-site success remains unverified. Cloud Chromium also denies unpacked extension loading through administrator policy. Unit tests and injected-script browser tests passed, but installation and request-rule integration have not been validated in that environment. This extension does not promise to remove every advertisement or certify a site's safety.

## Development and checks

The extension needs no dependency installation or build step. Run the unit tests using Node.js 24:

```sh
node --test tests/*.test.js
```

With Python Playwright and `/usr/lib/chromium/chromium` available, run the browser behavior checks:

```sh
python tests/browser_behavior.py
python tests/layers_behavior.py
```

These tests run the shipped page scripts in real Chromium fixture pages with a storage API fixture. They exercise automatic and unrelated-click popups, intentional links and Ctrl-click, sign-in buttons, synthetic anchor clicks, initial and dynamic overlays, normal dialog preservation, manual selection, overlay recurrence, rule reset and disabling behavior. They do not validate unpacked extension installation or Chrome's network-rule enforcement.

`python tests/browser_smoke.py` attempts to load the actual unpacked extension. The current cloud administrator policy blocks that operation; run it separately in a development browser where unpacked extensions are allowed.

## Manually select an overlay

1. Enable overall blocking and **Hide ad overlays** in the extension menu.
2. While the unwanted overlay is visible, open the extension and choose **Select an ad overlay**.
3. Move the pointer over the ad. A red outline shows the element to hide. Click to save and hide it. Press Esc to cancel.
4. The selector is saved for the current origin (scheme, host and port) and reapplied to matching positioned overlays. If the identifier or structure changes, select it again.
5. If you selected the wrong element, choose **Reset selected rules for this site**. This removes your custom selections; built-in ad rules remain active.

The picker targets fixed/absolute overlays, not arbitrary page content. A transparent selection layer captures clicks so advertising iframes can also be selected. Rules are stored only in the local Chrome profile. Removing and reinstalling the extension clears them.

## Illustrated guide

A 20-page English guide: 12 introductory pages and an 8-page technical appendix. Diagrams explain request filtering, popup decisions, overlay hiding, manual selection, settings and limitations.

- [Download the PDF](https://github.com/ryujuhwa/chrome-feautures/raw/refs/heads/main/downloads/popup-blocker-guide.pdf)
- [Download the PDF and offline HTML bundle](https://github.com/ryujuhwa/chrome-feautures/raw/refs/heads/main/downloads/popup-blocker-guide.zip)

Extract the guide ZIP and double-click `popup-blocker-guide.html` to read it without an Internet connection. The PDF uses A4 landscape pages.

Pages 13–20 cover file roles, MAIN/ISOLATED execution worlds, settings events, `window.open` decisions, request rules, `MutationObserver`, hiding/restoration, selector storage, permissions and verification boundaries.

To regenerate the guide:

```sh
python docs/build_guide.py
python docs/render_guide.py
```

Generation requires fontTools, Python Playwright, Chromium at the configured path and the system Noto CJK font. PyMuPDF is optional for PDF text/page checks. The bundled subset font license is in `docs/FONT-LICENSE.txt`.
