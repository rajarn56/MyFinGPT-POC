/** API types and interfaces */

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

export interface AgentActivity {
  agents_executed: string[];
  token_usage: Record<string, number>;
  execution_time: Record<string, number>;
  context_size?: number;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  context?: ConversationContext;
}

export interface ChatResponse {
  message_id: string;
  session_id: string;
  content: string;
  transaction_id: string;
  citations: Citation[];
  visualizations?: Visualization[];
  agent_activity: AgentActivity;
  timestamp: string;
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

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
  total_count: number;
  has_more: boolean;
}

export interface SessionResponse {
  session_id: string;
  created_at: string;
  expires_at: string;
}

export interface ConversationContext {
  symbols: string[];
  previous_queries: string[];
  research_data?: any;
  analysis_results?: any;
  citations?: Citation[];
  context_version: number;
  context_size: number;
}

