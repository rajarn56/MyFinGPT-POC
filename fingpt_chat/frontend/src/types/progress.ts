/** Progress tracking types */

export interface ProgressEvent {
  timestamp: string;
  agent: string;
  event_type: 'agent_start' | 'agent_complete' | 'task_start' | 
              'task_complete' | 'task_progress' | 'api_call_start' |
              'api_call_success' | 'api_call_failed' | 'api_call_skipped';
  message: string;
  task_name?: string;
  symbol?: string;
  status: 'running' | 'completed' | 'failed' | 'success' | 'skipped';
  execution_order: number;
  is_parallel: boolean;
  integration?: string;
  error?: string;
}

export interface ExecutionOrderEntry {
  agent: string;
  start_time: number;
  end_time?: number;
  duration?: number;
}

export interface ProgressUpdate {
  type: 'progress_update';
  session_id: string;
  transaction_id: string;
  current_agent?: string;
  current_tasks: Record<string, string[]>;
  progress_events: ProgressEvent[];
  execution_order: ExecutionOrderEntry[];
  timestamp: string;
}

export interface ProgressState {
  currentAgent?: string;
  currentTasks: Record<string, string[]>;
  progressEvents: ProgressEvent[];
  executionOrder: ExecutionOrderEntry[];
  isActive: boolean;
}

