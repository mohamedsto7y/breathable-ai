// Breathable AI - content script
// Watches for the phrase "take a deep breath" being submitted in a chat box
// and plays a real human breath, so the *user* takes one instead of the model.

// Firefox and Safari both expose `chrome` with Chrome-style callbacks, so a
// single namespace works everywhere. (`browser` is promise-only in Firefox,
// which is why we do NOT prefer it here.)
const api = globalThis.chrome ?? globalThis.browser;

const PHRASE = /take\s+a\s+deep\s+breath/i;

let enabled = true;

api.storage.local.get('enabled', (data) => {
  enabled = data.enabled !== false; // default on
});

api.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.enabled) {
    enabled = changes.enabled.newValue !== false;
  }
});

// Page CSP applies to media the content script loads into the document, and a
// strict media-src can reject a chrome-extension: URL outright. ChatGPT's, for
// one, is `'self' *.oaiusercontent.com blob: ...` -- no extension scheme.
// Fetching from the content script's isolated world is exempt from the page's
// CSP, and the resulting blob: URL is accepted far more widely. The direct URL
// stays as a fallback for anywhere the fetch is unavailable.
const directUrl = api.runtime.getURL('breath.mp3');
let triedFallback = false;

const audio = new Audio();
audio.preload = 'auto';

function useDirectUrl(why) {
  if (triedFallback) return;
  triedFallback = true;
  console.warn('[Breathable AI] blob source unusable (' + why + '); trying ' + directUrl);
  audio.src = directUrl;
  audio.load();
}

// A media-level failure (CSP rejection, decode error) never rejects the fetch
// promise, so it needs its own listener or it fails silently.
audio.addEventListener('error', () => {
  const err = audio.error;
  const detail = err ? err.code + ': ' + err.message : 'unknown';
  if (triedFallback) {
    console.warn('[Breathable AI] could not load breath.mp3 at all -- ' + detail);
  } else {
    useDirectUrl(detail);
  }
});

fetch(directUrl)
  .then((res) => {
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.blob();
  })
  .then((blob) => {
    if (!blob.size) throw new Error('empty blob'); // e.g. an opaque CORS response
    audio.src = URL.createObjectURL(blob);
    audio.load();
  })
  .catch((err) => useDirectUrl(err.message));

// Read text only from the field the user is actually typing in. Reading
// `textContent` off an arbitrary target would match any page that merely
// displays the phrase somewhere in its subtree.
function typedText(el) {
  if (!el) return '';
  if (typeof el.value === 'string') return el.value;
  if (el.isContentEditable) return el.textContent || '';
  return '';
}

let lastPlayed = 0;

function playBreath() {
  if (!audio.src) {
    console.warn('[Breathable AI] phrase matched but the sound is not loaded yet');
    return;
  }
  // Chat composers can emit more than one keydown for a single send (React and
  // ProseMirror both re-dispatch), and two triggers in the same instant used to
  // collide: the second call's pause() aborted the first call's pending play()
  // promise, so nothing was heard at all.
  const now = Date.now();
  if (now - lastPlayed < 300) return;
  lastPlayed = now;

  // Seeking to 0 restarts playback on its own. Calling pause() first is what
  // produced the AbortError, so it is deliberately absent.
  audio.currentTime = 0;
  audio.play().catch((err) => {
    if (err.name === 'AbortError') return; // superseded by a newer trigger
    console.warn('[Breathable AI] play() was blocked: ' + err.name + ' - ' + err.message);
  });
}

// Capture phase on `window` at document_start: chat UIs call stopPropagation()
// in their own composer handlers, so a bubble-phase listener never fires.
window.addEventListener(
  'keydown',
  (e) => {
    if (!enabled) return;
    if (e.key !== 'Enter' || e.shiftKey) return;
    if (e.repeat) return; // holding Enter down must not machine-gun it
    if (e.isComposing || e.keyCode === 229) return; // mid-IME composition
    if (PHRASE.test(typedText(e.target))) playBreath();
  },
  true
);
