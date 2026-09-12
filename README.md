# Breathable AI

**[Install from the Chrome Web Store](https://chromewebstore.google.com/detail/breathable-ai/jflnamibokeipdcidnfnjejfelnlhpgc)**

A novelty Chrome/Firefox extension. Type **"take a deep breath"** into an AI chat box,
press Enter, and you hear a real human breath.

The running joke: the famous prompt tells the *model* to take a deep breath. This makes
the *user* take one instead.

## Install (unpacked, for development)

The published build is on the Chrome Web Store, linked above. To run the working copy:

**Chrome / Edge / Brave / Opera**
1. Go to `chrome://extensions`
2. Turn on **Developer mode**
3. **Load unpacked** → select this folder

**Firefox** (temporary, until signed)
1. Go to `about:debugging#/runtime/this-firefox`
2. **Load Temporary Add-on** → select `manifest.json`

## How it works

`content.js` registers a `keydown` listener on `window` in the **capture** phase at
`document_start`. That ordering is load-bearing: every major chat UI calls
`stopPropagation()` inside its own composer handler, so a bubble-phase listener on
`document` would never fire on exactly the sites this extension targets.

On Enter (without Shift, and not mid-IME-composition) it reads the text of the focused
field — `value` for inputs and textareas, `textContent` for contenteditable composers —
and plays `breath.mp3` if the phrase is in there. It deliberately does *not* read
`textContent` off arbitrary targets, so a page that merely displays the phrase somewhere
doesn't trigger it.

A single `Audio` object is reused and rewound with `currentTime = 0`, so back-to-back
sends replay it cleanly instead of stacking.

### Why the sound is loaded as a blob

The page's Content-Security-Policy governs media the content script loads into the
document, and a strict `media-src` will reject a `chrome-extension:` URL. ChatGPT serves:

```
media-src 'self' *.oaiusercontent.com blob: https://cdn.oaistatic.com https://cdn.openai.com https://persistent.oaistatic.com
```

No extension scheme there — but `blob:` is allowed. So `content.js` fetches the file from
the content script's isolated world, which carries the extension's origin and is exempt
from the page CSP, then plays the resulting `blob:` URL. If that fetch ever fails it falls
back to the direct `chrome-extension:` URL, which is why `breath.mp3` stays in
`web_accessible_resources`.

This was measured on the live site, not assumed — see the verification notes below.

## Where it runs

Only on the AI chat sites listed in `manifest.json` — ChatGPT, Claude, Gemini, AI Studio,
Copilot, Perplexity, Grok, DeepSeek, Mistral, Poe, HuggingChat, Qwen, and Meta AI.
It requests no broad host access. To add a site, add the match pattern to **both**
`content_scripts[0].matches` and `web_accessible_resources[0].matches`, then bump the
version.

## Cross-browser notes

Both scripts use `globalThis.chrome ?? globalThis.browser`. Firefox 109+ and Safari both
expose `chrome` with Chrome-style callbacks; Firefox's `browser` namespace is
**promise-only**, so preferring `browser` while passing callbacks — a common shim
mistake — breaks on Firefox specifically.

| Browser | Status |
|---|---|
| Chrome 88+ | Supported |
| Edge | Verified working, installed from the Chrome Web Store |
| Brave / Opera / Vivaldi | Chromium; install from the Chrome Web Store |
| Firefox 109+ | Supported via `browser_specific_settings.gecko` |
| Safari 16.4+ | Code is compatible; still needs `xcrun safari-web-extension-converter` |

## Development

```bash
python tools/make_icons.py   # regenerate icons from icons/source-glyph-512.png
python tools/build.py        # produce dist/breathable-ai-<version>.zip for upload
```

Behavioural tests live in `tools/test/harness.html` — 15 checks across five modes
(`?only=disabled`, `?only=swallow`, `?only=source`, `?only=fallback`, and the default
run). They stub the extension APIs, `fetch` and the `Audio` constructor, then dispatch
synthetic keydown events. Run them headless:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --no-sandbox --dump-dom --virtual-time-budget=2000 "file:///D:/Breathable-AI/tools/test/harness.html"
```

## Store assets

`store/` holds the finished Chrome Web Store graphics plus the HTML they were rendered
from (`store/src/`). Re-render any of them with headless Chrome at the exact pixel size —
see `store/STORE-LISTING.md`, which also has the listing copy ready to paste.

## Licence

Code is MIT — see `LICENSE`.

`breath.mp3` is ["deep breath sigh" by locrpg](https://pixabay.com/sound-effects/people-deep-breath-sigh-104109/),
used under the [Pixabay Content License](https://pixabay.com/service/license-summary/):
free for commercial use, attribution not required, credited here anyway. The licence
forbids redistributing the file *standalone* — bundled inside the extension as a working
component, which is what happens here, is the intended use.

The sound is deliberately bundled rather than fetched from a URL: a remote file would
introduce a network request (breaking the extension's no-data-collection claim), would be
rejected by the strict `media-src` policies these chat sites serve, and could not load
fast enough to play inside the keystroke's user-activation window.

## Verification notes

The behaviour was confirmed against the live `chatgpt.com` composer, by injecting the
unmodified `content.js` at `document_start` over the Chrome DevTools Protocol with only
`chrome.*` and `fetch` stubbed, then driving real mouse and key input:

- the keydown reached the `window` capture listener with `target=prompt-textarea`,
  confirming the capture-phase fix defeats ProseMirror's `stopPropagation()`
- `audio.src` resolved to a `blob:` URL, `readyState` 4, **no CSP violations**
- `play()` resolved and `currentTime` advanced to ~2.6 s
- Shift+Enter stayed silent

Microsoft Edge was confirmed working by installing the published build from the Chrome
Web Store, so the Chromium path is demonstrated rather than assumed.

### Published build, tested live (12 September 2026)

The package served by the Chrome Web Store was downloaded and compared with this repo:
the code is byte-identical, differing only by the `update_url` the store inserts. That
build was then installed as a real extension in Edge (which, unlike Chrome, still loads
extensions in a DevTools-driven session) and exercised with real Enter keypresses:

| Site | Result |
|---|---|
| ChatGPT, Gemini, Perplexity, Grok, Qwen | Phrase detected, breath played |
| Mistral | Breath plays. Its `media-src 'self' data:` blocks `blob:`, so the direct `chrome-extension://` fallback is used, and it plays |
| Claude, DeepSeek, Poe, Meta AI, HuggingChat, AI Studio | Extension injects and the sound loads; the chat box sits behind a sign-in, so Enter was not exercised |
| Copilot, in Edge only | Edge blocks every extension on its own Copilot page; nothing to fix here |

Every site's redirects land inside the manifest's match patterns. Chrome itself was also
confirmed working by hand, via Load unpacked.
