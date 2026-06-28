import React, { useMemo } from 'react';
import Svg, { Defs, LinearGradient, Path, Stop, Circle } from 'react-native-svg';
import type { TrackingPoint } from '../types/api';
import type { TracerConfig } from '../types/tracer';

interface Props {
  trackingPoints: TrackingPoint[];
  currentFrame: number;
  videoWidth: number;
  videoHeight: number;
  containerWidth: number;
  containerHeight: number;
  config: TracerConfig;
}

export default function TracerOverlay({
  trackingPoints,
  currentFrame,
  videoWidth,
  videoHeight,
  containerWidth,
  containerHeight,
  config,
}: Props) {
  const scaleX = containerWidth / (videoWidth || 1);
  const scaleY = containerHeight / (videoHeight || 1);

  const visiblePoints = useMemo(() => {
    const trailStart = currentFrame - config.trailLength;
    return trackingPoints
      .filter((p) => p.frame >= trailStart && p.frame <= currentFrame)
      .sort((a, b) => a.frame - b.frame);
  }, [trackingPoints, currentFrame, config.trailLength]);

  if (visiblePoints.length < 1) return null;

  const pixelPoints = visiblePoints.map((p) => ({
    px: p.x * videoWidth * scaleX,
    py: p.y * videoHeight * scaleY,
    frame: p.frame,
  }));

  // Build SVG path from points
  const pathD = pixelPoints.reduce((d, pt, i) => {
    return i === 0 ? `M ${pt.px} ${pt.py}` : `${d} L ${pt.px} ${pt.py}`;
  }, '');

  const head = pixelPoints[pixelPoints.length - 1];
  const headRadius = config.thickness + 3;

  return (
    <Svg
      width={containerWidth}
      height={containerHeight}
      style={{ position: 'absolute', top: 0, left: 0 }}
    >
      <Defs>
        <LinearGradient id="tracerGrad" x1="0" y1="0" x2="1" y2="0">
          <Stop offset="0%" stopColor={config.color} stopOpacity={0} />
          <Stop offset="100%" stopColor={config.color} stopOpacity={config.opacity} />
        </LinearGradient>
      </Defs>

      {/* Glow layer */}
      {config.glowRadius > 0 && (
        <Path
          d={pathD}
          stroke={config.color}
          strokeWidth={config.thickness * 3}
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
          opacity={config.glowOpacity * 0.4}
        />
      )}

      {/* Main tracer line */}
      <Path
        d={pathD}
        stroke="url(#tracerGrad)"
        strokeWidth={config.thickness}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
        opacity={config.opacity}
      />

      {/* Ball dot at head */}
      <Circle
        cx={head.px}
        cy={head.py}
        r={headRadius}
        fill={config.color}
        opacity={config.opacity}
      />
    </Svg>
  );
}
