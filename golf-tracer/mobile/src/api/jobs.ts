import client from './client';
import { ENDPOINTS } from '../constants/api';
import type { JobResult, JobStatus } from '../types/api';

export async function createJob(videoId: string, sport = 'golf'): Promise<JobStatus> {
  const response = await client.post<JobStatus>(ENDPOINTS.createJob, {
    video_id: videoId,
    sport,
  });
  return response.data;
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const response = await client.get<JobStatus>(ENDPOINTS.getJobStatus(jobId));
  return response.data;
}

export async function getJobResult(jobId: string): Promise<JobResult> {
  const response = await client.get<JobResult>(ENDPOINTS.getJobResult(jobId));
  return response.data;
}

export function getFrameUrl(jobId: string, frameIndex: number): string {
  const { API_BASE_URL } = require('../constants/api');
  return `${API_BASE_URL}${ENDPOINTS.getFrame(jobId, frameIndex)}`;
}
