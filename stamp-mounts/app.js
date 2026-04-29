'use strict';

const MM_TO_PX = 96 / 25.4; // 96 dpi: 1 mm = ~3.7795 px

const PAPER = {
  a4:     { w: 210,   h: 297   },
  letter: { w: 215.9, h: 279.4 },
  a5:     { w: 148,   h: 210   },
};

const DEFAULTS = {
  paperSize:     'a4',
  orientation:   'portrait',
  margin:        15,
  cols:          4,
  rows:          5,
  gap:           5,
  gridAlign:     'center',
  mountW:        35,
  mountH:        45,
  mountPreset:   '',
  borderStyle:   'solid',
  borderW:       1,
  borderColor:   '#333333',
  borderRadius:  0,
  mountBg:       '#ffffff',
  showLabels:    true,
  labelH:        8,
  fontSize:      7,
  labelColor:    '#222222',
  fontFamily:    'inherit',
  pageTitle:     'My Stamp Collection',
  pageSubtitle:  '',
  showDate:      false,
  titleSize:     14,
  headerSpacing: 5,
  showFooter:    false,
  footerText:    '',
};

let settings = { ...DEFAULTS };
let labels   = [];

function pageDims() {
  const base = PAPER[settings.paperSize];
  return settings.orientation === 'portrait'
    ? { w: base.w, h: base.h }
    : { w: base.h, h: base.w };
}

function mountCount() { return settings.cols * settings.rows; }

function syncLabels() {
  const n = mountCount();
  while (labels.length < n) labels.push('');
  labels.length = n;
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function escAttr(s) {
  return String(s).replace(/"/g, '&quot;');
}

// ── Render ──────────────────────────────────────────────────────────────────

function render() {
  syncLabels();

  const { w, h } = pageDims();
  const m        = settings.margin;
  const page     = document.getElementById('page-preview');

  page.style.cssText = `
    width: ${w}mm;
    height: ${h}mm;
    padding: ${m}mm;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
  `;

  let html = '';

  // ── Header ──
  const hasHeader = settings.pageTitle || settings.pageSubtitle || settings.showDate;
  if (hasHeader) {
    html += '<div class="page-header">';
    if (settings.pageTitle)
      html += `<div class="page-title" style="font-size:${settings.titleSize}pt;">${esc(settings.pageTitle)}</div>`;
    if (settings.pageSubtitle)
      html += `<div class="page-subtitle" style="font-size:${Math.max(8, settings.titleSize - 4)}pt;">${esc(settings.pageSubtitle)}</div>`;
    if (settings.showDate)
      html += `<div class="page-date">${new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}</div>`;
    html += `</div><div style="height:${settings.headerSpacing}mm;"></div>`;
  }

  // ── Grid ──
  const cellH        = settings.mountH + (settings.showLabels ? settings.labelH : 0);
  const borderRadius = settings.borderRadius > 0 ? `${settings.borderRadius}mm` : '0';
  const justifyMap   = { center: 'center', left: 'flex-start', right: 'flex-end' };
  const justify      = justifyMap[settings.gridAlign] || 'center';

  html += `<div class="mount-grid-wrap" style="display:flex;justify-content:${justify};">`;
  html += `<div class="mount-grid" style="
    grid-template-columns: repeat(${settings.cols}, ${settings.mountW}mm);
    grid-template-rows: repeat(${settings.rows}, ${cellH}mm);
    gap: ${settings.gap}mm;
  ">`;

  for (let i = 0; i < mountCount(); i++) {
    const val = escAttr(labels[i] || '');

    let labelHtml = '';
    if (settings.showLabels) {
      labelHtml = `<div class="mount-label" style="height:${settings.labelH}mm;">
        <input
          class="label-input"
          type="text"
          data-idx="${i}"
          value="${val}"
          placeholder="Label"
          style="font-size:${settings.fontSize}pt;color:${settings.labelColor};font-family:${settings.fontFamily};"
        >
      </div>`;
    }

    html += `<div class="mount-cell">
      <div class="mount-box" style="
        width:${settings.mountW}mm;
        height:${settings.mountH}mm;
        border:${settings.borderW}px ${settings.borderStyle} ${settings.borderColor};
        border-radius:${borderRadius};
        background:${settings.mountBg};
      "></div>
      ${labelHtml}
    </div>`;
  }

  html += '</div></div>';

  // ── Footer (spacer pushes it to page bottom via flex column) ──
  if (settings.showFooter && settings.footerText) {
    html += '<div style="flex:1;min-height:2mm;"></div>';
    html += `<div class="page-footer">${esc(settings.footerText)}</div>`;
  }

  page.innerHTML = html;

  // Re-attach label input handlers after innerHTML replacement
  page.querySelectorAll('.label-input').forEach(el => {
    el.addEventListener('input', e => {
      labels[+e.target.dataset.idx] = e.target.value;
    });
  });

  updateFitIndicator();
  scalePreview();
  updatePrintPageStyle();
}

// ── Fit check ───────────────────────────────────────────────────────────────

function estimatedHeaderMm() {
  let h = 0;
  if (settings.pageTitle)    h += settings.titleSize * 0.353 + 2;
  if (settings.pageSubtitle) h += Math.max(8, settings.titleSize - 4) * 0.353 + 2;
  if (settings.showDate)     h += 3.5;
  if (h > 0)                 h += settings.headerSpacing;
  return h;
}

function updateFitIndicator() {
  const { w, h }  = pageDims();
  const m         = settings.margin;
  const availW    = w - 2 * m;
  const availH    = h - 2 * m - estimatedHeaderMm();

  const gridW = settings.cols * settings.mountW + (settings.cols - 1) * settings.gap;
  const cellH = settings.mountH + (settings.showLabels ? settings.labelH : 0);
  const gridH = settings.rows * cellH + (settings.rows - 1) * settings.gap;

  const overW = Math.max(0, gridW - availW);
  const overH = Math.max(0, gridH - availH);
  const fits  = overW === 0 && overH === 0;

  const indicator = document.getElementById('fit-indicator');
  const icon      = document.getElementById('fit-icon');
  const text      = document.getElementById('fit-text');

  if (fits) {
    indicator.className = 'fit-ok';
    icon.textContent    = '✓';
    text.textContent    = `Grid fits — ${settings.cols * settings.rows} mount positions`;
  } else {
    const parts = [];
    if (overW > 0) parts.push(`${overW.toFixed(1)} mm too wide`);
    if (overH > 0) parts.push(`${overH.toFixed(1)} mm too tall`);
    indicator.className = 'fit-warn';
    icon.textContent    = '⚠';
    text.textContent    = `Overflow: ${parts.join(', ')}`;
  }
}

// ── Preview scaling ──────────────────────────────────────────────────────────

function scalePreview() {
  const { w, h }  = pageDims();
  const wrapper   = document.getElementById('preview-wrapper');
  const scaler    = document.getElementById('preview-scaler');
  const page      = document.getElementById('page-preview');

  const availW = wrapper.clientWidth  - 48;
  const availH = wrapper.clientHeight - 48;
  const pageW  = w * MM_TO_PX;
  const pageH  = h * MM_TO_PX;

  const scale = Math.min(availW / pageW, availH / pageH, 1);

  scaler.style.width  = Math.round(pageW * scale) + 'px';
  scaler.style.height = Math.round(pageH * scale) + 'px';
  page.style.transform = `scale(${scale})`;
}

// ── Print page-size CSS ──────────────────────────────────────────────────────

function updatePrintPageStyle() {
  const { w, h } = pageDims();
  document.getElementById('print-page-style').textContent =
    `@media print { @page { size: ${w}mm ${h}mm; margin: 0; } }`;
}

// ── Read controls ────────────────────────────────────────────────────────────

function readSettings() {
  const g = id => document.getElementById(id);

  settings.paperSize     = g('paperSize').value;
  settings.orientation   = g('orientation').value;
  settings.margin        = +g('margin').value        || 0;
  settings.cols          = Math.max(1, +g('cols').value   || 1);
  settings.rows          = Math.max(1, +g('rows').value   || 1);
  settings.gap           = +g('gap').value           || 0;
  settings.gridAlign     = g('gridAlign').value;
  settings.mountW        = +g('mountW').value        || 10;
  settings.mountH        = +g('mountH').value        || 10;
  settings.borderStyle   = g('borderStyle').value;
  settings.borderW       = +g('borderW').value       || 0;
  settings.borderColor   = g('borderColor').value;
  settings.borderRadius  = +g('borderRadius').value  || 0;
  settings.mountBg       = g('mountBg').value;
  settings.showLabels    = g('showLabels').checked;
  settings.labelH        = +g('labelH').value        || 5;
  settings.fontSize      = +g('fontSize').value      || 7;
  settings.labelColor    = g('labelColor').value;
  settings.fontFamily    = g('fontFamily').value;
  settings.pageTitle     = g('pageTitle').value;
  settings.pageSubtitle  = g('pageSubtitle').value;
  settings.showDate      = g('showDate').checked;
  settings.titleSize     = +g('titleSize').value     || 14;
  settings.headerSpacing = +g('headerSpacing').value || 0;
  settings.showFooter    = g('showFooter').checked;
  settings.footerText    = g('footerText').value;

  g('label-options').style.display  = settings.showLabels ? '' : 'none';
  g('footer-options').style.display = settings.showFooter ? '' : 'none';
}

// ── Reset ────────────────────────────────────────────────────────────────────

function resetAll() {
  labels   = [];
  settings = { ...DEFAULTS };

  Object.entries(DEFAULTS).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (!el) return;
    if (el.type === 'checkbox') el.checked = Boolean(val);
    else el.value = val;
  });

  render();
}

// ── Init ─────────────────────────────────────────────────────────────────────

function init() {
  const inner = document.getElementById('controls-inner');

  inner.addEventListener('input',  () => { readSettings(); render(); });
  inner.addEventListener('change', () => { readSettings(); render(); });

  // Mount preset selector applies width/height
  document.getElementById('mountPreset').addEventListener('change', e => {
    if (!e.target.value) return;
    const [mw, mh] = e.target.value.split(',').map(Number);
    document.getElementById('mountW').value = mw;
    document.getElementById('mountH').value = mh;
    readSettings();
    render();
    e.target.value = ''; // reset to "Custom" after applying
  });

  document.getElementById('printBtn').addEventListener('click', () => window.print());
  document.getElementById('resetBtn').addEventListener('click', resetAll);

  window.addEventListener('resize', () => scalePreview());

  readSettings();
  render();
}

document.addEventListener('DOMContentLoaded', init);
