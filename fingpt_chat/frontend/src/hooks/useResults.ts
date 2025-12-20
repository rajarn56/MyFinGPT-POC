/** Results state management hook */
import { useState, useEffect } from 'react';
import { useChat } from './useChat';
import type { ResultsState, Visualization, AgentActivity } from '../types/chat';
import { getDemoChatMessage, DEMO_AGENT_ACTIVITY } from '../utils/demoData';
import { API_BASE_URL } from '../config/api';

// Only show demo data when connected to mock server (localhost:8000) and in development
const SHOW_DEMO_DATA = 
  import.meta.env.DEV && 
  (API_BASE_URL.includes('localhost:8000') || API_BASE_URL.includes('127.0.0.1:8000'));

export function useResults() {
  const { state: chatState } = useChat();
  const [results, setResults] = useState<ResultsState>(() => {
    // Initialize with demo data if enabled and no messages
    if (SHOW_DEMO_DATA && chatState.messages.length === 0) {
      const demoMessage = getDemoChatMessage();
      return {
        currentReport: demoMessage.content,
        visualizations: demoMessage.visualizations || [],
        agentActivity: DEMO_AGENT_ACTIVITY,
      };
    }
    return {
      currentReport: undefined,
      visualizations: [],
      agentActivity: undefined,
    };
  });

  useEffect(() => {
    // Get the latest assistant message
    const lastMessage = chatState.messages
      .filter((msg) => msg.role === 'assistant')
      .pop();

    if (lastMessage) {
      // Update results with new assistant message
      const agentActivity = (lastMessage as any).agentActivity;
      setResults({
        currentReport: lastMessage.content || undefined,
        visualizations: lastMessage.visualizations || [],
        agentActivity: agentActivity || undefined,
      });
    } else if (SHOW_DEMO_DATA && chatState.messages.length === 0) {
      // Show demo data when no messages (only in dev mode with mock server)
      const demoMessage = getDemoChatMessage();
      setResults({
        currentReport: demoMessage.content,
        visualizations: demoMessage.visualizations || [],
        agentActivity: DEMO_AGENT_ACTIVITY,
      });
    } else if (chatState.messages.length === 0 && !SHOW_DEMO_DATA) {
      // Clear results only when no messages and not showing demo data
      setResults({
        currentReport: undefined,
        visualizations: [],
        agentActivity: undefined,
      });
    }
    // Note: If there are user messages but no assistant response yet, keep previous results
  }, [chatState.messages]);

  // Update results when a new response arrives
  const updateResults = (
    content: string,
    visualizations?: Visualization[],
    agentActivity?: AgentActivity
  ) => {
    setResults({
      currentReport: content,
      visualizations: visualizations || [],
      agentActivity,
    });
  };

  return {
    results,
    updateResults,
  };
}

