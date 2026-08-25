# Chrome Web Store listing — Breathable AI

Everything below is ready to paste into the Developer Dashboard. Character limits are
noted; `python tools/build.py --check-copy` verifies them against this file.

---

## Item name
`Breathable AI`

## Summary  *(max 132 characters)*
```
Make AI human again. Type "take a deep breath" in an AI chat and hear a real human breath — then take one yourself.
```

## Category
**Just for Fun** — it is a novelty extension and reviewers treat it more kindly there than
under Well-being, which invites health-claim scrutiny this extension cannot support.

## Language
English (United Kingdom or United States — either is fine, just be consistent with the
spelling in the description below, which is written in en-GB.)

---

## Description  *(max 16,000 characters)*

```
MAKE AI HUMAN AGAIN!

There is a well-known trick where you tell an AI model to "take a deep breath" before it
answers a hard question. The model does not have lungs. You do.

Breathable AI sits quietly in your AI chat tabs. When you type "take a deep breath"
anywhere in a message and press Enter, it plays a recording of a real human breath. That
is the entire extension. You send your prompt, you hear someone exhale, and for about
five seconds you are a person with a body again rather than a person with a backlog.

HOW IT WORKS

1. Type "take a deep breath" anywhere in your message.
2. Press Enter.
3. Hear it. Ideally, join in.

Shift+Enter is safe — the sound only fires on the keystroke that actually sends your
message, so you can write multi-line prompts without setting it off. The phrase is
matched case-insensitively and can sit anywhere in the message, so "ok take a deep breath
and rewrite this properly" works exactly as well.

ONE SETTING

Click the toolbar icon and you get a single On/Off button. It is on by default. Turn it
off before a meeting, turn it back on afterwards. There is nothing else to configure,
because there is nothing else.

PRIVACY

- It runs only inside AI chat interfaces. Chrome shows you the exact list of sites on
  the install prompt, and it cannot see any other tab you open.
- No network requests. The sound file is bundled inside the extension.
- Your messages are never read, stored, or transmitted. The text of the box you are
  typing in is tested against one pattern in local memory and immediately forgotten.
- No analytics, no telemetry, no third-party code, no accounts.
- The only thing saved is whether you switched it on or off, and it stays on your machine.

Breath sound: "deep breath sigh" by locrpg, via Pixabay.

Open source. Built as a joke that turned out to be quite nice to actually use.
```

---

## Privacy practices tab

**Single purpose** *(paste verbatim)*
```
Breathable AI has one purpose: to play a bundled sound file when the user presses Enter
on a message containing the phrase "take a deep breath" in an AI chat interface. It is a
novelty extension and does nothing else.
```

**Justification — `storage` permission**
```
The extension stores exactly one boolean: whether the user has switched the sound on or
off from the toolbar popup. chrome.storage.local is used so the setting survives a browser
restart. No other data is written, and nothing is synced.
```

**Justification — host access to the listed sites**
```
The extension must run a content script on these AI chat sites in order to detect the
Enter keypress and read the text of the message box the user is typing in. That detection
is only possible from within the page. Access is limited to a fixed list of AI chat
domains declared in the manifest; the extension requests no broad host permissions and
runs nowhere else.
```

**Data usage declarations** — tick *none* of the collection categories, then affirm all
three certification checkboxes:
- [x] I do not sell or transfer user data to third parties, outside of approved use cases
- [x] I do not use or transfer user data for purposes unrelated to my item's single purpose
- [x] I do not use or transfer user data to determine creditworthiness or for lending purposes

**Privacy policy URL** — required even for zero-collection items. Host `PRIVACY.md`
somewhere public (a GitHub repo file or GitHub Pages URL is accepted) and paste the link.

---

## Graphics checklist

| Asset | Required size | File | Status |
|---|---|---|---|
| Store icon | 128 x 128 | `../icons/icon128.png` | Ready |
| Screenshot 1 | 1280 x 800 | `screenshot-1-the-moment.png` | Ready |
| Screenshot 2 | 1280 x 800 | `screenshot-2-popup.png` | Ready |
| Screenshot 3 | 1280 x 800 | `screenshot-3-privacy.png` | Ready |
| Screenshot 4 | 1280 x 800 | `screenshot-4-how-it-works.png` | Ready |
| Small promo tile | 440 x 280 | `promo-tile-small-440x280.png` | Ready (optional; needed to be featured) |
| Marquee promo tile | 1400 x 560 | `promo-marquee-1400x560.png` | Ready (optional) |

Sources are in `src/`. To re-render one after editing its HTML:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1280,800 --screenshot="OUT.png" "file:///D:/Breathable-AI/store/src/shot1.html"
```

Headless Chrome refuses to write into the project directory on this machine — render to a
temp path and copy the file back.

---

## Before you submit

1. ~~Clear the rights to `breath.mp3`.~~ **Done.** It is "deep breath sigh" by locrpg
   from Pixabay, under the Pixabay Content License: commercial use permitted, attribution
   not required. The licence's only relevant restriction is on redistributing content
   *standalone*, which does not apply to a sound bundled as a working component of an
   extension. Credit is recorded in `LICENSE` and `README.md`, and in the description
   below.
2. Register as a Chrome Web Store developer (one-off 5 USD fee) if you have not already.
3. Host the privacy policy at a public URL and paste the link into the dashboard.
4. Upload `dist/breathable-ai-1.0.0.zip`.
5. Expect a few days for review. A narrow host-permission list like this one usually
   clears faster than a `<all_urls>` extension, which is why the manifest was scoped down.

## Firefox (AMO), if you want it there too

The manifest already carries `browser_specific_settings.gecko` with the ID
`mohaly0520@gmail.com` and `strict_min_version: 109.0`. That ID string ships publicly
inside the package. Upload the same zip at addons.mozilla.org; AMO review is separate,
usually faster, and has no listing fee.
