// Point to your backend — update for production
export const API_BASE_URL = __DEV__
  ? 'http://192.168.4.28:8000'  // Mac local IP — update if network changes
  : 'https://your-backend.railway.app';

export const API_TIMEOUT_MS = 30_000;

export const ENDPOINTS = {
  uploadVideo: '/videos',
  getVideo: (id: string) => `/videos/${id}`,
  createJob: '/jobs',
  getJobStatus: (id: string) => `/jobs/${id}/status`,
  getJobResult: (id: string) => `/jobs/${id}/result`,
  getFrame: (jobId: string, frame: number) => `/jobs/${jobId}/frames/${frame}`,
  patchCorrections: (id: string) => `/jobs/${id}/corrections`,
  triggerExport: (id: string) => `/jobs/${id}/export`,
  getExportStatus: (jobId: string, exportId: string) => `/jobs/${jobId}/exports/${exportId}`,
  downloadExport: (exportId: string) => `/exports/${exportId}/download`,
} as const;

export const POLL_INTERVAL_MS = 2_000;
export const MAX_UPLOAD_SIZE_MB = 500;
