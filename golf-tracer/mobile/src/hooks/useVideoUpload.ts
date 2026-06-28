import { useState } from 'react';
import { uploadVideo } from '../api/videos';
import { createJob } from '../api/jobs';
import type { VideoMetadata, JobStatus } from '../types/api';

type UploadState =
  | { phase: 'idle' }
  | { phase: 'uploading'; progress: number }
  | { phase: 'done'; video: VideoMetadata; job: JobStatus }
  | { phase: 'error'; error: string };

export function useVideoUpload() {
  const [state, setState] = useState<UploadState>({ phase: 'idle' });

  async function upload(uri: string, filename: string) {
    setState({ phase: 'uploading', progress: 0 });
    try {
      const video = await uploadVideo(uri, filename, (progress) => {
        setState({ phase: 'uploading', progress });
      });

      const job = await createJob(video.id);
      setState({ phase: 'done', video, job });
      return { video, job };
    } catch (err: any) {
      const error = err.message ?? 'Upload failed';
      setState({ phase: 'error', error });
      throw err;
    }
  }

  function reset() {
    setState({ phase: 'idle' });
  }

  return { state, upload, reset };
}
