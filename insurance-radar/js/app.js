// Application controller
(function () {
  let currentType = 'broker';
  let chart = null;

  function getColor(type) {
    return COLORS.primary[type];
  }

  function populateSelects() {
    const entities = DATA[currentType];
    const select = document.getElementById('entity-select');
    const compare = document.getElementById('compare-select');

    select.innerHTML = '';
    compare.innerHTML = '<option value="">None</option>';

    entities.forEach((e, idx) => {
      const opt1 = new Option(e.name, e.id);
      select.add(opt1);
      const opt2 = new Option(e.name, e.id);
      compare.add(opt2);
    });
  }

  function getEntityById(id) {
    return DATA[currentType].find(e => e.id === id);
  }

  function buildStatCards(entity, metrics, color) {
    const panel = document.getElementById('stats-panel');
    panel.innerHTML = '';

    metrics.forEach(metric => {
      const percentile = entity.scores[metric.key] || 0;
      const rawVal = entity.rawValues ? entity.rawValues[metric.key] : null;
      const bar = Math.round(percentile);
      const dir = metric.higherIsBetter;
      const tierColor = percentile >= 75 ? '#4ade80'
        : percentile >= 50 ? '#facc15'
        : '#f87171';

      const card = document.createElement('div');
      card.className = 'stat-card';
      card.innerHTML = `
        <div class="stat-header">
          <span class="stat-name">${metric.label}</span>
          <span class="stat-pct" style="color:${tierColor}">${percentile}<sup>th</sup></span>
        </div>
        <div class="stat-bar-bg">
          <div class="stat-bar-fill" style="width:${bar}%;background:${color}"></div>
        </div>
        ${rawVal !== null
          ? `<div class="stat-raw">${metric.format(rawVal)}</div>`
          : ''}
      `;
      panel.appendChild(card);
    });
  }

  function render() {
    const primaryId = document.getElementById('entity-select').value;
    const compareId = document.getElementById('compare-select').value;

    if (!primaryId) return;

    const primary = getEntityById(primaryId);
    const compare = compareId ? getEntityById(compareId) : null;
    const metrics = METRICS[currentType];
    const color = getColor(currentType);
    const cmpColor = COLORS.comparison;

    // Update header info
    document.getElementById('entity-name').textContent = primary.name;
    document.getElementById('entity-meta').textContent = primary.meta;

    const peerEl = document.getElementById('peer-group');
    peerEl.textContent = `Percentile rank among ${primary.peerGroup}`;

    if (!chart) {
      chart = new InsuranceRadarChart('radar-container', { width: 560 });
    }

    chart.render(primary, metrics, color, compare, cmpColor);
    buildStatCards(primary, metrics, color);

    // Update export button data
    document.getElementById('btn-export').dataset.entityName = primary.name;
  }

  function switchType(type) {
    currentType = type;
    chart = null;
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.type === type);
    });

    // Update type indicator
    const indicator = document.getElementById('type-indicator');
    const labels = { broker: 'Broker', segment: 'Trade Segment', product: 'Product' };
    indicator.textContent = labels[type];
    indicator.className = 'type-badge type-' + type;

    populateSelects();
    render();
  }

  function exportSvg() {
    const svg = document.querySelector('#radar-container svg');
    if (!svg) return;

    const entityName = document.getElementById('btn-export').dataset.entityName || 'radar';
    const blob = new Blob([svg.outerHTML], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${entityName.replace(/\s+/g, '-').toLowerCase()}-radar.svg`;
    a.click();
    URL.revokeObjectURL(url);
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => switchType(btn.dataset.type));
    });

    // Selects
    document.getElementById('entity-select').addEventListener('change', render);
    document.getElementById('compare-select').addEventListener('change', render);

    // Export
    document.getElementById('btn-export').addEventListener('click', exportSvg);

    // Init
    switchType('broker');
  });
})();
