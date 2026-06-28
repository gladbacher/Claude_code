import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useState } from 'react';
import { DEFAULT_TRACER_CONFIG } from '../constants/tracer';
import type { TracerConfig } from '../types/tracer';

const STORAGE_KEY = '@golf_tracer_config';

export function useTracerConfig() {
  const [config, setConfig] = useState<TracerConfig>(DEFAULT_TRACER_CONFIG);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((raw) => {
      if (raw) {
        try {
          setConfig({ ...DEFAULT_TRACER_CONFIG, ...JSON.parse(raw) });
        } catch {
          // ignore corrupted storage
        }
      }
      setLoaded(true);
    });
  }, []);

  function updateConfig(partial: Partial<TracerConfig>) {
    setConfig((prev) => {
      const next = { ...prev, ...partial };
      AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }

  function resetConfig() {
    setConfig(DEFAULT_TRACER_CONFIG);
    AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_TRACER_CONFIG));
  }

  return { config, updateConfig, resetConfig, loaded };
}
