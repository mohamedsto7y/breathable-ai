// Same namespace choice as content.js: `chrome` is callback-style in every
// browser that ships it, including Firefox 109+ and Safari.
const api = globalThis.chrome ?? globalThis.browser;

const btn = document.getElementById('toggle');
let enabled = true;

function render() {
  btn.textContent = enabled ? 'On' : 'Off';
  btn.className = enabled ? 'on' : 'off';
  btn.setAttribute('aria-pressed', String(enabled));
}

api.storage.local.get('enabled', (data) => {
  enabled = data.enabled !== false; // default on
  btn.disabled = false;
  render();
});

// Flip the local copy first so rapid clicks can't race two storage reads.
btn.addEventListener('click', () => {
  enabled = !enabled;
  render();
  api.storage.local.set({ enabled });
});
