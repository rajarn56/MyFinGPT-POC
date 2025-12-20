/** WebSocket hook for progress updates */
import { useEffect, useState } from 'react';
import { wsClient } from '../services/websocket';
import type { ProgressUpdate, ProgressState } from '../types/progress';
import { getDemoProgressEvents, getDemoExecutionOrder } from '../utils/demoData';
import { WS_BASE_URL } from '../config/api';

// Only show demo data when connected to mock server (localhost:8000) and in development
const SHOW_DEMO_DATA = 
  import.meta.env.DEV && 
  (WS_BASE_URL.includes('localhost:8000') || WS_BASE_URL.includes('127.0.0.1:8000'));

export function useWebSocket(sessionId: string | null) {
  const [progress, setProgress] = useState<ProgressState>(() => {
    // Initialize with demo data if enabled
    if (SHOW_DEMO_DATA) {
      return {
        currentAgent: undefined,
        currentTasks: {},
        progressEvents: getDemoProgressEvents(),
        executionOrder: getDemoExecutionOrder(),
        isActive: false,
      };
    }
    return {
      currentAgent: undefined,
      currentTasks: {},
      progressEvents: [],
      executionOrder: [],
      isActive: false,
    };
  });

  useEffect(() => {
    if (!sessionId) {
      wsClient.disconnect();
      // Only clear demo data if we're not showing demo data
      if (!SHOW_DEMO_DATA) {
        setProgress({
          currentAgent: undefined,
          currentTasks: {},
          progressEvents: [],
          executionOrder: [],
          isActive: false,
        });
      } else {
        // Keep demo data but mark as inactive
        setProgress((prev) => ({
          ...prev,
          isActive: false,
        }));
      }
      return;
    }

    const handleProgressUpdate = (update: ProgressUpdate) => {
      setProgress((prev) => ({
        currentAgent: update.current_agent,
        currentTasks: update.current_tasks,
        progressEvents: [...prev.progressEvents, ...update.progress_events],
        executionOrder: update.execution_order,
        isActive: true,
      }));
    };

    wsClient.connect(sessionId, handleProgressUpdate);

    return () => {
      // Only disconnect if sessionId changes or component unmounts
      // Don't disconnect if we're just updating the callback
      wsClient.disconnect();
    };
  }, [sessionId]);

  return progress;
}

