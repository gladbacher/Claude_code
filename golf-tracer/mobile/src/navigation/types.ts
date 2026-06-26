import type { JobResult, JobStatus, VideoMetadata } from '../types/api';

export type RootStackParamList = {
  Home: undefined;
  Record: undefined;
  Import: undefined;
  Processing: {
    videoId: string;
    jobId: string;
  };
  Result: {
    videoUri: string;
    jobResult: JobResult;
    jobId: string;
  };
  Correction: {
    jobId: string;
    jobResult: JobResult;
    videoUri: string;
  };
  Export: {
    jobId: string;
    jobResult: JobResult;
    videoUri: string;
  };
};
