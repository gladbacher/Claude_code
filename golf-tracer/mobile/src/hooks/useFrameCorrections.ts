import { useState } from 'react';
import { patchCorrections } from '../api/corrections';
import type { CorrectionPoint } from '../types/tracer';
import type { JobResult } from '../types/api';

export function useFrameCorrections(jobId: string) {
  const [corrections, setCorrections] = useState<Map<number, CorrectionPoint>>(new Map());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function addCorrection(frame: number, x: number, y: number) {
    setCorrections((prev) => {
      const next = new Map(prev);
      next.set(frame, { frame, x, y });
      return next;
    });
  }

  function deleteCorrection(frame: number) {
    setCorrections((prev) => {
      const next = new Map(prev);
      next.set(frame, { frame, x: 0, y: 0, delete: true });
      return next;
    });
  }

  function clearCorrections() {
    setCorrections(new Map());
  }

  async function commitCorrections(): Promise<JobResult | null> {
    if (corrections.size === 0) return null;
    setSaving(true);
    setError(null);
    try {
      const result = await patchCorrections(jobId, Array.from(corrections.values()));
      setCorrections(new Map());
      return result;
    } catch (err: any) {
      setError(err.message);
      return null;
    } finally {
      setSaving(false);
    }
  }

  const pendingCount = corrections.size;

  return {
    corrections,
    pendingCount,
    saving,
    error,
    addCorrection,
    deleteCorrection,
    clearCorrections,
    commitCorrections,
  };
}
