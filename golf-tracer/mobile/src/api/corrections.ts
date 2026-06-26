import client from './client';
import { ENDPOINTS } from '../constants/api';
import type { JobResult } from '../types/api';
import type { CorrectionPoint } from '../types/tracer';

export async function patchCorrections(
  jobId: string,
  corrections: CorrectionPoint[],
): Promise<JobResult> {
  const response = await client.patch<JobResult>(ENDPOINTS.patchCorrections(jobId), {
    corrections: corrections.map((c) => ({
      frame: c.frame,
      x: c.x,
      y: c.y,
      delete: c.delete ?? false,
    })),
  });
  return response.data;
}
