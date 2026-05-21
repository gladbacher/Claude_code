// D3.js radar chart for insurance performance visualization
class InsuranceRadarChart {
  constructor(containerId, { width = 560 } = {}) {
    this.containerId = containerId;
    this.width = width;
    this.height = width;
    this.cx = width / 2;
    this.cy = width / 2;
    this.margin = 110;
    this.radius = width / 2 - this.margin;
    this.levels = 5;
    this._activeTooltip = null;
  }

  _angle(i, n) {
    return (i / n) * 2 * Math.PI - Math.PI / 2;
  }

  _point(value, i, n) {
    const angle = this._angle(i, n);
    const r = (Math.max(0, Math.min(100, value)) / 100) * this.radius;
    return [r * Math.cos(angle), r * Math.sin(angle)];
  }

  _anchor(angle) {
    const cos = Math.cos(angle);
    if (cos > 0.1) return 'start';
    if (cos < -0.1) return 'end';
    return 'middle';
  }

  _buildSvg() {
    const container = d3.select(`#${this.containerId}`);
    container.selectAll('*').remove();

    const svg = container
      .append('svg')
      .attr('width', this.width)
      .attr('height', this.height)
      .attr('viewBox', `0 0 ${this.width} ${this.height}`)
      .style('display', 'block');

    // Background
    svg.append('rect')
      .attr('width', this.width)
      .attr('height', this.height)
      .attr('fill', '#0d1b2a')
      .attr('rx', 16);

    // Inner glow background circle
    const defs = svg.append('defs');

    const radialGrad = defs.append('radialGradient')
      .attr('id', 'chart-bg-grad')
      .attr('cx', '50%').attr('cy', '50%').attr('r', '50%');
    radialGrad.append('stop')
      .attr('offset', '0%').attr('stop-color', '#1a2e48').attr('stop-opacity', 1);
    radialGrad.append('stop')
      .attr('offset', '100%').attr('stop-color', '#0d1b2a').attr('stop-opacity', 1);

    const g = svg.append('g')
      .attr('transform', `translate(${this.cx}, ${this.cy})`);

    g.append('circle')
      .attr('r', this.radius + 2)
      .attr('fill', 'url(#chart-bg-grad)')
      .attr('stroke', 'rgba(255,255,255,0.06)')
      .attr('stroke-width', 1);

    return { svg, g, defs };
  }

  _drawGrid(g, n) {
    for (let lv = 1; lv <= this.levels; lv++) {
      const r = (lv / this.levels) * this.radius;
      g.append('circle')
        .attr('r', r)
        .attr('fill', 'none')
        .attr('stroke', lv === this.levels
          ? 'rgba(255,255,255,0.18)'
          : 'rgba(255,255,255,0.07)')
        .attr('stroke-width', lv === this.levels ? 1.5 : 1);

      // Level labels at top
      if (lv < this.levels) {
        g.append('text')
          .attr('x', 4)
          .attr('y', -r + 3)
          .attr('fill', 'rgba(255,255,255,0.22)')
          .attr('font-size', '9px')
          .attr('font-family', 'Inter, system-ui, sans-serif')
          .text(lv * 20);
      }
    }

    // Axis lines
    for (let i = 0; i < n; i++) {
      const angle = this._angle(i, n);
      g.append('line')
        .attr('x1', 0).attr('y1', 0)
        .attr('x2', this.radius * Math.cos(angle))
        .attr('y2', this.radius * Math.sin(angle))
        .attr('stroke', 'rgba(255,255,255,0.1)')
        .attr('stroke-width', 1);
    }
  }

  _drawLabels(g, metrics) {
    const n = metrics.length;
    const labelR = this.radius + 22;

    metrics.forEach((metric, i) => {
      const angle = this._angle(i, n);
      const x = labelR * Math.cos(angle);
      const y = labelR * Math.sin(angle);
      const anchor = this._anchor(angle);

      const words = metric.label.split(' ');
      const lineH = 14;

      // Highlight axis tip
      g.append('circle')
        .attr('cx', this.radius * Math.cos(angle))
        .attr('cy', this.radius * Math.sin(angle))
        .attr('r', 2.5)
        .attr('fill', 'rgba(255,255,255,0.25)');

      if (words.length <= 1) {
        g.append('text')
          .attr('x', x).attr('y', y)
          .attr('text-anchor', anchor)
          .attr('dominant-baseline', 'middle')
          .attr('fill', '#a8c0db')
          .attr('font-size', '11.5px')
          .attr('font-family', 'Inter, system-ui, sans-serif')
          .attr('font-weight', '500')
          .text(metric.label);
      } else {
        const half = Math.ceil(words.length / 2);
        const lines = [
          words.slice(0, half).join(' '),
          words.slice(half).join(' '),
        ].filter(Boolean);
        const totalH = lines.length * lineH;

        lines.forEach((line, li) => {
          g.append('text')
            .attr('x', x)
            .attr('y', y - totalH / 2 + lineH / 2 + li * lineH)
            .attr('text-anchor', anchor)
            .attr('dominant-baseline', 'middle')
            .attr('fill', '#a8c0db')
            .attr('font-size', '11.5px')
            .attr('font-family', 'Inter, system-ui, sans-serif')
            .attr('font-weight', '500')
            .text(line);
        });
      }

      // Direction badge
      const badgeAngle = this._angle(i, n);
      const badgeR = this.radius - 10;
      const bx = badgeR * Math.cos(badgeAngle);
      const by = badgeR * Math.sin(badgeAngle);
      g.append('text')
        .attr('x', bx).attr('y', by)
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .attr('fill', metric.higherIsBetter ? '#4ade80' : '#f87171')
        .attr('font-size', '10px')
        .attr('opacity', 0.7)
        .text(metric.higherIsBetter ? '▲' : '▼');
    });
  }

  _drawArea(g, defs, entity, metrics, color, opacity, isComparison) {
    const n = metrics.length;
    const gradId = `area-grad-${isComparison ? 'cmp' : 'pri'}`;

    const radGrad = defs.append('radialGradient')
      .attr('id', gradId)
      .attr('cx', '50%').attr('cy', '50%').attr('r', '50%');
    radGrad.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', color)
      .attr('stop-opacity', opacity * 1.4);
    radGrad.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', color)
      .attr('stop-opacity', opacity * 0.6);

    const points = metrics.map((m, i) =>
      this._point(entity.scores[m.key] || 0, i, n)
    );

    const pathStr = 'M' + points.map(p => p.join(',')).join('L') + 'Z';

    // Shadow path for glow
    if (!isComparison) {
      g.append('path')
        .attr('d', pathStr)
        .attr('fill', 'none')
        .attr('stroke', color)
        .attr('stroke-width', 8)
        .attr('stroke-opacity', 0.12)
        .attr('stroke-linejoin', 'round');
    }

    // Main filled area
    g.append('path')
      .attr('d', pathStr)
      .attr('fill', `url(#${gradId})`)
      .attr('stroke', color)
      .attr('stroke-width', isComparison ? 1.8 : 2.5)
      .attr('stroke-opacity', isComparison ? 0.7 : 0.95)
      .attr('stroke-linejoin', 'round')
      .attr('stroke-dasharray', isComparison ? '6,3' : null);

    return points;
  }

  _drawDots(g, points, metrics, entity, color, isComparison, tooltip) {
    points.forEach((pt, i) => {
      const metric = metrics[i];
      const percentile = entity.scores[metric.key] || 0;
      const rawVal = entity.rawValues ? entity.rawValues[metric.key] : null;

      const dot = g.append('circle')
        .attr('cx', pt[0]).attr('cy', pt[1])
        .attr('r', isComparison ? 3.5 : 5)
        .attr('fill', color)
        .attr('stroke', '#ffffff')
        .attr('stroke-width', isComparison ? 1 : 1.8)
        .style('cursor', 'pointer');

      dot.on('mouseover', (event) => {
        dot.attr('r', isComparison ? 5 : 7);
        tooltip
          .style('display', 'block')
          .html(`
            <div class="tt-metric">${metric.label}</div>
            <div class="tt-percentile">
              <span class="tt-value-big">${percentile}</span>
              <span class="tt-label">th percentile</span>
            </div>
            ${rawVal !== null ? `<div class="tt-raw">${metric.format(rawVal)}</div>` : ''}
            <div class="tt-entity">${entity.name}</div>
            <div class="tt-desc">${metric.description}</div>
          `);
        this._positionTooltip(event, tooltip);
      });

      dot.on('mousemove', (event) => {
        this._positionTooltip(event, tooltip);
      });

      dot.on('mouseout', () => {
        dot.attr('r', isComparison ? 3.5 : 5);
        tooltip.style('display', 'none');
      });
    });
  }

  _positionTooltip(event, tooltip) {
    const tw = 220;
    const margin = 14;
    let left = event.pageX + margin;
    if (left + tw > window.innerWidth) left = event.pageX - tw - margin;
    tooltip
      .style('left', left + 'px')
      .style('top', (event.pageY - 60) + 'px');
  }

  render(primaryEntity, metrics, primaryColor, compareEntity = null, compareColor = null) {
    const { svg, g, defs } = this._buildSvg();
    const n = metrics.length;

    this._drawGrid(g, n);

    let tooltip = d3.select('body').select('.radar-tooltip');
    if (tooltip.empty()) {
      tooltip = d3.select('body').append('div').attr('class', 'radar-tooltip');
    }

    // Draw comparison entity first (underneath)
    if (compareEntity) {
      const cmpPoints = this._drawArea(g, defs, compareEntity, metrics, compareColor, 0.18, true);
      this._drawDots(g, cmpPoints, metrics, compareEntity, compareColor, true, tooltip);
    }

    // Draw primary entity
    const priPoints = this._drawArea(g, defs, primaryEntity, metrics, primaryColor, 0.38, false);
    this._drawDots(g, priPoints, metrics, primaryEntity, primaryColor, false, tooltip);

    // Labels drawn last so they're always on top
    this._drawLabels(g, metrics);

    // Legend
    if (compareEntity) {
      const legendY = this.height - 24;
      const items = [
        { label: primaryEntity.name, color: primaryColor },
        { label: compareEntity.name, color: compareColor },
      ];
      const totalW = items.reduce((sum, it) => sum + it.label.length * 7 + 24, 0) + 20;
      let lx = (this.width - totalW) / 2;

      items.forEach(item => {
        svg.append('rect')
          .attr('x', lx).attr('y', legendY - 8)
          .attr('width', 14).attr('height', 4)
          .attr('rx', 2).attr('fill', item.color);
        svg.append('text')
          .attr('x', lx + 18).attr('y', legendY - 4)
          .attr('fill', 'rgba(255,255,255,0.6)')
          .attr('font-size', '11px')
          .attr('font-family', 'Inter, system-ui, sans-serif')
          .text(item.label);
        lx += item.label.length * 7 + 34;
      });
    }
  }
}
