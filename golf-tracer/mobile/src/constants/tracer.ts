import type { TracerConfig } from '../types/tracer';

export const DEFAULT_TRACER_CONFIG: TracerConfig = {
  color: '#FF6B00',
  thickness: 4,
  opacity: 0.85,
  glowRadius: 8,
  glowOpacity: 0.4,
  trailLength: 30,
  fadeTail: true,
  fadeExponent: 2.0,
};

export const TRACER_PRESETS: Record<string, TracerConfig> = {
  Classic: {
    color: '#FF6B00',
    thickness: 4,
    opacity: 0.85,
    glowRadius: 8,
    glowOpacity: 0.4,
    trailLength: 30,
    fadeTail: true,
    fadeExponent: 2.0,
  },
  Neon: {
    color: '#00FF88',
    thickness: 3,
    opacity: 1.0,
    glowRadius: 16,
    glowOpacity: 0.7,
    trailLength: 25,
    fadeTail: true,
    fadeExponent: 1.5,
  },
  White: {
    color: '#FFFFFF',
    thickness: 3,
    opacity: 0.9,
    glowRadius: 6,
    glowOpacity: 0.3,
    trailLength: 20,
    fadeTail: true,
    fadeExponent: 2.5,
  },
  Minimal: {
    color: '#FF6B00',
    thickness: 2,
    opacity: 0.7,
    glowRadius: 0,
    glowOpacity: 0,
    trailLength: 15,
    fadeTail: true,
    fadeExponent: 3.0,
  },
};
