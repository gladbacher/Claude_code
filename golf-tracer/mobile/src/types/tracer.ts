export interface TracerConfig {
  color: string;
  thickness: number;
  opacity: number;
  glowRadius: number;
  glowOpacity: number;
  trailLength: number;
  fadeTail: boolean;
  fadeExponent: number;
}

export interface CorrectionPoint {
  frame: number;
  x: number;
  y: number;
  delete?: boolean;
}
