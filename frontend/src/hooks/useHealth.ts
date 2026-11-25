import { useState, useEffect, useCallback } from 'react';
import { HealthResponse } from '../types';
import { getHealth } from '../services/api';

export function useHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);

  const checkHealth = useCallback(async () => {
    try {
      setHealthLoading(true);
      const data = await getHealth();
      setHealth(data);
    } catch (err) {
      console.warn('Backend gateway health check pending/failed:', err);
    } finally {
      setHealthLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    checkHealth();
    const interval = setInterval(() => {
      if (isMounted) checkHealth();
    }, 30000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [checkHealth]);

  return { health, healthLoading, refreshHealth: checkHealth };
}
