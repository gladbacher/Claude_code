import client from './client';
import { ENDPOINTS } from '../constants/api';
import type { VideoMetadata } from '../types/api';

export async function uploadVideo(
  uri: string,
  filename: string,
  onProgress?: (progress: number) => void,
): Promise<VideoMetadata> {
  const formData = new FormData();
  formData.append('file', {
    uri,
    name: filename,
    type: 'video/mp4',
  } as any);

  const response = await client.post<VideoMetadata>(ENDPOINTS.uploadVideo, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(event.loaded / event.total);
      }
    },
    timeout: 120_000, // uploads can be large
  });

  return response.data;
}

export async function getVideo(videoId: string): Promise<VideoMetadata> {
  const response = await client.get<VideoMetadata>(ENDPOINTS.getVideo(videoId));
  return response.data;
}
