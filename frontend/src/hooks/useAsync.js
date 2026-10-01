import {useCallback, useState} from 'react';

export function useAsync(action) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = useCallback(async (...args) => {
    setLoading(true);
    setError('');
    try {
      return await action(...args);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Unexpected error');
      throw cause;
    } finally {
      setLoading(false);
    }
  }, [action]);

  return {run, loading, error};
}

