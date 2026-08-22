# Privacy Policy — Breathable AI

_Last updated: 21 August 2026_

Breathable AI does not collect, store, transmit, or sell any user data.

## What the extension does

It watches for the Enter keypress on the AI chat sites listed in its manifest. When the
text you are about to send contains the phrase "take a deep breath", it plays a sound
file that is bundled inside the extension.

## What it does not do

- It makes **no network requests**. The sound file ships inside the extension package.
- It does **not** read, store, or transmit the content of your messages. The text of the
  focused field is tested against a single regular expression in local memory and is
  never copied, retained, or sent anywhere.
- It has **no analytics, telemetry, crash reporting, or third-party code**.
- It does **not** use cookies, and does not read or modify page content.

## Stored data

One value — whether the extension is switched on or off — is saved with
`chrome.storage.local`. It stays on your own machine, is not synced, and is removed when
you uninstall the extension.

## Permissions

- **`storage`** — to remember your on/off setting.
- **Host access to the listed AI chat sites** — required to detect the keypress in those
  pages. The extension requests no access to any other site.

## Contact

mohaly0520@gmail.com
