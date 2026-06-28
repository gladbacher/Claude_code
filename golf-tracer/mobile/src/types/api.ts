export interface VideoMetadata {
  id: string;
  filename: string;
  fps: number | null;
  duration_s: number | null;
  width: number | null;
  height: number | null;
  frame_count: number | null;
  file_size_bytes: number | null;
  created_at: string;
}

export interface TrackingPoint {
  frame: number;
  x: number;      // normalized 0.0–1.0
  y: number;      // normalized 0.0–1.0
  confidence: number;
  is_interpolated: boolean;
  is_manual: boolean;
}

export type JobStatusType = 'queued' | 'processing' | 'done' | 'error';

export interface JobStatus {
  id: string;
  status: JobStatusType;
  progress: number;
  progress_message: string | null;
  error_message: string | null;
  created_at: string;
}

export interface JobResult {
  job_id: string;
  impact_frame: number;
  fps: number;
  frame_count: number;
  width: number;
  height: number;
  coverage: number;
  tracking_points: TrackingPoint[];
}

export interface ExportStatus {
  id: string;
  job_id: string;
  status: string;
  download_url: string | null;
  created_at: string;
}
