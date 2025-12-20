/** Chat state types */

export interface ChatState {
  sessionId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  transaction_id?: string;
  citations?: Citation[];
  visualizations?: Visualization[];
}

export interface Citation {
  source: string;
  url?: string;
  date?: string;
  agent?: string;
  data_point?: string;
  symbol?: string;
}

export interface Visualization {
  type: 'line_chart' | 'bar_chart' | 'pie_chart' | 'scatter_plot';
  title: string;
  data: any;
  config?: any;
}

export interface ResultsState {
  currentReport?: string;
  visualizations: Visualization[];
  agentActivity?: AgentActivity;
}

export interface AgentActivity {
  agents_executed: string[];
  token_usage: Record<string, number>;
  execution_time: Record<string, number>;
  context_size?: number;
}

