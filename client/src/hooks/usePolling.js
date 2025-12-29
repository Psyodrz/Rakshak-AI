/**
 * Custom hook for polling data at intervals
 */
import { useState, useEffect, useCallback } from 'react';

export function usePolling(fetchFn, interval = 5000, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const result = await fetchFn();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchFn, ...dependencies]);

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, interval);
    return () => clearInterval(timer);
  }, [fetchData, interval]);

  return { data, loading, error, refetch: fetchData };
}

export default usePolling;
