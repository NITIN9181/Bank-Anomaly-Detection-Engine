import { useEffect, useRef } from 'react';

/**
 * Custom hook for setInterval with proper cleanup.
 * @param {Function} callback - Function to execute on interval
 * @param {number|null} delay - Interval in milliseconds, or null to pause
 */
function useInterval(callback, delay) {
  const savedCallback = useRef();

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval
  useEffect(() => {
    function tick() {
      savedCallback.current();
    }
    if (delay !== null) {
      const id = setInterval(tick, delay);
      return () => clearInterval(id);
    }
  }, [delay]);
}

export default useInterval;
