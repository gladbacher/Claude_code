import client from './client';
import { API_BASE_URL, ENDPOINTS } from '../constants/api';
import type { ExportStatus } from '../types/api';
import type { TracerConfig } from '../types/tracer';

function toApiTracerConfig(config: TracerConfig) {
  return {
    color: config.color,
    thickness: config.thickness,
    opacity: config.opacity,
    glow_radius: config.glowRadius,
    glow_opacity: config.glowOpacity,
    trail_length: config.trailLength,
    fade_tail: config.fadeTail,
    fade_exponent: config.fadeExponent,
  };
}

export async function triggerExport(
  jobId: string,
  tracerConfig: TracerConfig,
): Promise<ExportStatus> {
  const response = await client.post<ExportStatus>(ENDPOINTS.triggerExport(jobId), {
    tracer_config: toApiTracerConfig(tracerConfig),
  });
  return response.data;
}

export async function getExportStatus(
  jobId: string,
  exportId: string,
): Promise<ExportStatus> {
  const response = await client.get<ExportStatus>(ENDPOINTS.getExportStatus(jobId, exportId));
  return response.data;
}

export function getDownloadUrl(exportId: string): string {
  return `${API_BASE_URL}${ENDPOINTS.downloadExport(exportId)}`;
}
