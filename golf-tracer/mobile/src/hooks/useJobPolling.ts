import { useCallback, useEffect, useRef, useState } from 'react';
import { getJobResult, getJobStatus } from '../api/jobs';
import { POLL_INTERVAL_MS } from '../constants/api';
import type { JobResult, JobStatus } from '../types/api';

interface PollingState {
  status: JobStatus | null;
  result: JobResult | null;
  isPolling: boolean;
  error: string | null;
}

export function useJobPolling(jobId: string | null) {
  const [state, setState] = useState<PollingState>({
    status: null,
    result: null,
    isPolling: false,
    error: null,
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setState((prev) => ({ ...prev, isPolling: false }));
  }, []);

  const poll = useCallback(async () => {
    if (!jobId) return;
    try {
      const status = await getJobStatus(jobId);
      setState((prev) => ({ ...prev, status, error: null }));

      if (status.status === 'done') {
        const result = await getJobResult(jobId);
        setState((prev) => ({ ...prev, result, isPolling: false }));
        stopPolling();
      } else if (status.status === 'error') {
        setState((prev) => ({
          ...prev,
          error: status.error_message ?? 'Processing failed',
          isPolling: false,
        }));
        stopPolling();
      }
    } catch (err: any) {
      setState((prev) => ({ ...prev, error: err.message }));
    }
  }, [jobId, stopPolling]);

  useEffect(() => {
    if (!jobId) return;

    setState((prev) => ({ ...prev, isPolling: true, error: null }));
    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => stopPolling();
  }, [jobId, poll, stopPolling]);

  return { ...state, stopPolling };
}
